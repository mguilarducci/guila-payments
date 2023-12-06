import uuid
import os

INSTRUCTIONS = """
voce é um bot bancario brasileiro. a sua unica função é faz transferencias bancarias via pix.
para realizar essas transferencias, voce precisa saber para qual chave pix ela sera enviada.
caso voce nao sabia, pergunte ao usuario se ele gostaria de cadastra-la. se o usuario cadastrar a chave, faça a transferencia pix solicitada.
mas se vc ja souber antecipadamente a chave, conclua a transferencia e avise ao usuario.
sempre informe o valor e para qual chave o pix foi enviado.
"""

import json 

from langchain.agents import  AgentExecutor, ZeroShotAgent, tool
from langchain.chat_models import ChatOpenAI

from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.chains import LLMChain

from src.db import db_pix_key
from src.key_management_agent import run as key_run

@tool
def get_key(owner: str) -> str:
    """
    Ask information about pix keys to the Key Agent.
    This agent is enable to retrieve keys. 
    The argument of this function is a string with the owner of the pix key.
    """
    print("\nExecutando integração entre agentes: pix-agent -> key-agent")
    return key_run(f'qual é a chave pix desta pessoa: {owner}?', str(uuid.uuid4()))

@tool
def create_key(data: str) -> str:
    """
    Ask information about pix keys to the Key Agent.
    This agent is enable to create keys. 
    The argument is a dictionary with owner and key values
    """
    print("\nExecutando integração entre agentes: pix-agent -> key-agent")
    return key_run(f'Crie uma chave pix com essas especificacoes: {data}?', str(uuid.uuid4()))



@tool
def send_pix(input: str) -> str:
    """
    Send a pix amount to a pix key.
    The argument is a dictionary with the key and amount values 
    """
    return "sent"

tools = [get_key, create_key, send_pix]

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

suffix = """
{chat_history}

Question: {input}
"""

def run(input: str, session_id: str):
    print(f'input do usuario: {input}')
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
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=bool(os.environ.get("VERBOSE_AGENT"))) 
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    response =  agent_chain.invoke(
        {"input": input},
        {"intermediate_steps": []},
    )

    print(response)
    return response.get("output")
    