from pathlib import Path
from app.agents import merger, chunker, conflict_dealer, extractor, normalizer, assemble
from app.store import save_plan

def doc_to_plan(text, doc_id="demo-doc", version="v1"):
    if not text:
        # Read default fixture file
        fixture_path = Path(__file__).parent / "fixture" / "apispec.txt"
        text = fixture_path.read_text()
    chunks = chunker.chunk_text(text)
    extracted = []

    for index, chunk in enumerate(chunks):
        result = extractor.extract_rules(chunk)
        print(f"Extracted Rules: {result}")
        extracted.append(result["extracted_rules"])
        print(index)

    print("===============finished extracting==============")
    normalized = [normalizer.normalize_rule(r) for rules in extracted for r in rules]
    print("==================rule normalized=================")
    merged = merger.merge_rules([normalized])
    print("================rule merged=====================")
    conflicts = conflict_dealer.detect_conflicts(merged)
    print("================conflict resolved================")
    plan = assemble.build_plan(doc_id, version, merged, conflicts)
    save_plan(plan, f"{doc_id}_plan.json")
    print("===============plan saved===================")
    return plan    

if __name__ == "__main__":
    doc_to_plan(None)

