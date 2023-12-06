import uuid
import os

from fastapi import FastAPI
from pydantic import BaseModel

from src.db import init, db_get_key, db_create_key
from src.key_management_agent import run as key_agent_run
from src.pix_agent import run as pix_agent_run
from src.health import check
from src.payment_agent import load, run_query


init()
base_path = os.getcwd()

class Key(BaseModel):
    name: str
    owner: str

class KeyAgentRequest(BaseModel):
    session_id: str
    input: str


class QueryRequest(BaseModel):
    query: str


app = FastAPI()


@app.post("/agent/session")
def create_session():
    return {"id": uuid.uuid4()}

@app.get("/api/keys/{owner}")
def read_item(owner: str):
    return db_get_key(owner)

@app.post("/api/keys")
def create_key(key: Key):
    db_create_key(key)
    return key
    
@app.post("/agent/keys")
def execute_key_agent(input: KeyAgentRequest):
    answer = key_agent_run(input.input, input.session_id)
    return {"answer": answer}


@app.post("/agent/pix")
def execute_key_agent(input: KeyAgentRequest):
    answer = pix_agent_run(input.input, input.session_id)
    return {"answer": answer}

@app.get("/health")
def health():
    return check()

@app.post("/api/load")
def execute_load():
    load(base_path)

@app.post("/api/query")
def execute_query(query: QueryRequest):
    run_query(query.query)

    