import os

from langchain.agents import AgentExecutor, tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langfuse.callback import CallbackHandler


embeddings = OpenAIEmbeddings()
connection_string = os.environ.get("DATABASE_URL")
collection_name = "payment_history_pgvector"


langfuse_handler = CallbackHandler()

def load(base_path):
    """
    Load the document, split it into chunks, embed each chunk and load it into the vector store.
    """
    path = f"{base_path}/data/payment_history.txt"
    print(f"loading: {path}")
    raw_documents = TextLoader(path).load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)

    PGVector.from_documents(
        embedding=embeddings,
        documents=documents,
        collection_name=collection_name,
        connection_string=connection_string,
    )

    print('load finished')

def run_query(query):
    print(f"running query: {query}")
    db = PGVector.from_existing_index(
        embedding=embeddings,
        collection_name=collection_name,
        connection_string=connection_string,
    )
    
    docs_with_score = db.max_marginal_relevance_search_with_score(query)

    for doc, score in docs_with_score:
        print("-" * 80)
        print("Score: ", score)
        print(doc.page_content)
        print("-" * 80)

    print("finished query")

@tool
def send_pix(key: str, amount: str):
    """
    Send pix to someone using the key.
    """
    print(f"sent {amount} to {key}")
    return "sent"

@tool
def pay_bill(code: str, amount: int):
    """
    Pay a bill (boleto) using the boleto code and the desired amount
    """
    print(f"paid: {code} amount {amount}")
    return "paid"

@tool
def get_bill(bill_name: str):
    """
    Get the bill (boleto) details by the bill (boleto) name.
    """
    bill = {"internet": {"code": "internetcode", "amount": 100},
            "agua": {"code": "aguacode", "amount": 200}}.get(bill_name)
    
    if not bill:
        return "Not found"
    return bill

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, callbacks=[langfuse_handler])
INSTRUCTIONS = """
voce é um bot bancário. sua responsabilidade é ajudar as pessoas a pagarem suas contas.
as contas só podem ser pagas enviando um pix ou pagando um boleto.
para pagar um boleto, voce deve fazer uma busca pela conta na api de boletos.
para voce enviar um pix, voce precisa saber a chave e o valor.

Context: {context}
"""

db = PGVector.from_existing_index(
    embedding=embeddings,
    collection_name=collection_name,
    connection_string=connection_string,
)

retriever = db.as_retriever()

tools = [send_pix, pay_bill, get_bill]


llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", INSTRUCTIONS),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

def run(input: str):
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
             "context": lambda x: format_docs(retriever.get_relevant_documents(input)),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input": input})
    return response.get("output")