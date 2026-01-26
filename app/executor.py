import uuid
import concurrent.futures
from pathlib import Path
from app.agents import merger, chunker, conflict_dealer, extractor, normalizer, assemble
from app.store import save_plan

def doc_to_plan(text, version="v1"):
    doc_id = str(uuid.uuid4())[:8]
    if not text:
        # Read default fixture file
        fixture_path = Path(__file__).parent / "fixture" / "apispec.txt"
        text = fixture_path.read_text()
    chunks = chunker.chunk_text(text)
    extracted = []

    print(f"Starting extraction for {len(chunks)} chunks...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Map chunks to executor
        future_to_chunk = {executor.submit(extractor.extract_rules, chunk): i for i, chunk in enumerate(chunks)}
        
        # Collect results as they complete (or strictly ordered)
        results = [None] * len(chunks)
        for future in concurrent.futures.as_completed(future_to_chunk):
            index = future_to_chunk[future]
            try:
                result = future.result()
                results[index] = result["extracted_rules"]
                print(f"Chunk {index} finished. Rules: {len(result['extracted_rules'])}")
            except Exception as exc:
                print(f"Chunk {index} generated an exception: {exc}")
                results[index] = []

    # Flatten list
    extracted = [extracted_rules for extracted_rules in results if extracted_rules]

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

