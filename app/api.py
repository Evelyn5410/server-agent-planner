from fastapi import FastAPI, Body
from app.executor import run, doc_to_plan
from app.agents.raw_plan_handler import raw_plan_handler

endpoint = FastAPI()

@endpoint.post("/process")
def process(req: dict = Body(default={})):
    user_input = req.get("input", "")
    return run(user_input)

@endpoint.post("/plan")
def plan(req: dict = Body(default={})):
    doc = req.get("doc", "")
    name = req.get("name", "demo-doc")
    return doc_to_plan(doc, name)

@endpoint.post("/process-raw")
def process_raw(req: dict = Body(default={})):
    doc = req.get("doc", "")
    return raw_plan_handler(doc)