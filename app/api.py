from fastapi import FastAPI, Body
from app.executor import run, doc_to_plan

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
