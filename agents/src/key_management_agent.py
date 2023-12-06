import json
import os

from langchain.agents import tool
from langchain.agents import  AgentExecutor, ZeroShotAgent, tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.chains import LLMChain
from langfuse.callback import CallbackHandler


from src.db import db_get_key, db_create_key

langfuse_handler = CallbackHandler()
langfuse_handler.auth_check()

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
    db_create_key(json.loads(input))
    return "created"

@tool
def send_pix(input: str) -> str:
    """
    Send a pix amount to a pix key.
    The argument is a dictionary with the key and amount values 
    """
    return "sent"

tools = [get_key, create_key]

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

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

    llm_chain = LLMChain(llm=llm, prompt=prompt, callbacks=[langfuse_handler])
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True) 
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=bool(os.environ.get("VERBOSE_AGENT")), memory=memory
    )

    response =  agent_chain.invoke(
        {"input": input},
        {"intermediate_steps": []},
    )

    print(response)
    return response.get("output")
    