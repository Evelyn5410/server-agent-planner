import uuid
from app.agents import planner, generator, validator, merger, chunker, conflict_dealer, extractor, normalizer, assemble
from app.store import save_artifact, save_plan

MAX_RETRIES = 2

def run(user_input: str):
    run_id = str(uuid.uuid4())

    plan = planner.plan(user_input)
    save_artifact(run_id, "plan", plan)

    for attempt in range(MAX_RETRIES):
        output = generator.generate(plan)
        save_artifact(run_id, f"output_{attempt}", {"output": output})

        result = validator.validate(output, plan)
        save_artifact(run_id, f"validation_{attempt}", result)

        if result["valid"]:
            return {"run_id": run_id, "output": output}

        plan["feedback"] = result["issues"]

    return {"run_id": run_id, "error": "Validation failed"}


def doc_to_plan(text, doc_id="demo-doc", version="v1"):
    if not text: text = open("./fixture/apispec.txt", "rt")
    chunks = chunker.chunk_text(text)
    extracted = []

    for chunk in chunks:
        result = extractor.extract_rules(chunk)
        extracted.append(result["extracted_rules"])

    normalized = [normalizer.normalize_rule(r) for rules in extracted for r in rules]
    merged = merger.merge_rules([normalized])
    conflicts = conflict_dealer.detect_conflicts(merged)

    plan = assemble.build_plan(doc_id, version, merged, conflicts)
    save_plan(plan, f"{doc_id}_plan.json")

    return plan    
