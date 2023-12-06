import json
from langchain.agents import tool, AgentExecutor,ZeroShotAgent
from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chat_models import ChatOpenAI

from langchain.tools.render import format_tool_to_openai_function
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.chains import LLMChain

from src.db import db_get_key, db_create_key


# from db import db_get_key

INSTRUCTIONS = """
você é um bot que gerencia chaves pix. sua única função é essa.
se alguém pedir alguma coisa que não seja relacionado a buscar chaves pix ou adicionar uma nova, você deve responder que não pode ajudar sobre o outro assunto.
caso a chave solicitada não existe, pergunte ao usuario se ele gostaria que ela fosse cadastrada. se ele responder que sim, solicite qual é o valor da chave pix e cadastre com o owner mecionando anteriormente.
se o valor da chave pix a ser cadastrado nao for informado, pergunte ao usuario.
lembre-se de ser sempre bem educado.

"""

@tool
def get_key(owner: str) -> str:
    """Returns the PIX key from the given owner. 
    The argument is a dictionary with owner value"""

    value = json.loads(owner)
    key = db_get_key(value.get("owner"))
    if not key:
        return "Not found"
    
    return key.get("name")

@tool
def create_key(input: str) -> str:
    """
    Creates a new PIX key to the owner.
    The argument is a dictionary with owner and key values
    """

    print(input)
    db_create_key(json.loads(input))
    return "created"

functions = {
    'get_key': get_key,
    'create_key': create_key,
}



tools = [get_key, create_key]

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")
llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

suffix = """
{chat_history}

Question: {input}
"""

def run(input: str, session_id: str):
    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=INSTRUCTIONS,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )

    message_history = RedisChatMessageHistory(
        url="redis://:eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81@redis:6379/0", ttl=600, session_id=session_id
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history", chat_memory=message_history
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True) 
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    response =  agent_chain.invoke(
        {"input": input},
        {"intermediate_steps": []},
    )

    print(response)
    return response.get("output")
