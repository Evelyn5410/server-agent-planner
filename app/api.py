from fastapi import FastAPI, Body
from app.executor import run, doc_to_plan

endpoint = FastAPI()

@endpoint.post("/process")
def process(req: dict = Body(...)):
    return run(req["input"])

@endpoint.post("/plan")
def plan(req: dict = Body(...)):
    return doc_to_plan(req["doc"], req["name"])
