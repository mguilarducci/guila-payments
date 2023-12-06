import json 

from langchain.agents import  AgentExecutor, ZeroShotAgent, tool
from langchain.chat_models import ChatOpenAI

from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.chains import LLMChain

from src.db import db_get_key, db_create_key

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

tools = [get_key, create_key, send_pix]

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

suffix = """
{chat_history}

Question: {input}
"""

def run(instructions: str, input: str, session_id: str):
    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=instructions,
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
    