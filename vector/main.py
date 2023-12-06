import uuid
import os

from fastapi import FastAPI
from pydantic import BaseModel

from src.health import check
from src.payment_agent import load, run_query, run


base_path = os.getcwd()

class QueryRequest(BaseModel):
    query: str


class AgentRequest(BaseModel):
    question: str

app = FastAPI()


@app.get("/health")
def health():
    return check()

@app.post("/api/load")
def execute_load():
    load(base_path)

@app.post("/api/query")
def execute_query(query: QueryRequest):
    run_query(query.query)

@app.post("/agent/payments")
def execute_payment_agent(input: AgentRequest):
    answer = run(input.question)
    return {"answer": answer}