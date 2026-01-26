"""
Raw Plan Handler - Single-read document to plan extraction.

Simple endpoint logic: input document → output plan
No metrics tracking here - that's handled by the benchmark pipeline.
"""
from pathlib import Path
import uuid
import json
import re
from google.genai import types
from app.constants import MODEL
from app.llm_client import client
from app.store import save_plan
from app.util.json_repair import repair_json
from app.constants import RESPONSE_SCHEMA_FOR_PROCESS_RAW_DOC

def raw_plan_handler(document: str) -> dict:
    """
    Extract plan from document in a single LLM call.

    Args:
        document: Full document text

    Returns:
        Plan dict with 'rules' and 'open_questions'
    """
    doc_id = str(uuid.uuid4())
    
    if not document:
        # Read default fixture file
        fixture_path = Path(__file__).parent / "fixture" / "apispec.txt"
        document = fixture_path.read_text()

    prompt = f"""
You are a document analysis system. Read the full Document.

Extract explicit rules, constraints, requirements, or prohibitions.

Rules:
- Output ONLY valid JSON.
- Do not summarize.
- Do not explain.
- If nothing is extractable, return an empty list.

Schema:
{{
  "extracted_rules": [
    {{
      "type": "constraint | behavior | requirement | prohibition",
      "statement": "string",
      "confidence": "high | medium | low"
    }}
  ]
}}

Document:
{document}
"""

    max_retries = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            # Use streaming to handle long responses better and debug truncation
            response_stream = client.models.generate_content_stream(
                model=MODEL,
                contents=[
                    {"role": "user", "parts": [{"text": prompt}]}
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA_FOR_PROCESS_RAW_DOC,
                    max_output_tokens=32768,
                    http_options=types.HttpOptions(timeout=600_000),
                ),
            )

            raw_text = ""
            for chunk in response_stream:
                if chunk.text:
                    raw_text += chunk.text
            
            # Check finish reason from the last chunk/response
            # Note: In stream, usage_metadata and finish_reason are usually on the last chunk
            # We can inspect the accumulated response object if needed, but iteration is simplest.
            print(f"[RawPlanHandler] Response length: {len(raw_text)}")
            
            # Try to log finish reason if possible (implementation specific)
            try:
                # Iterate through candidates of the LAST chunk if accessible, 
                # or rely on the loop finishing. 
                # Printing the last chunk's finish reason:
                if chunk.candidates and chunk.candidates[0].finish_reason:
                     print(f"[RawPlanHandler] Finish Reason: {chunk.candidates[0].finish_reason}")
            except:
                pass

            if not raw_text:
                raise RuntimeError("Empty response from LLM")

            # Strip markdown code blocks if present
            text = raw_text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)

            result = json.loads(text)
            print(f"[RawPlanHandler] Rules extracted: {len(result.get('extracted_rules', []))}")
            save_plan(result, f"{doc_id}_plan.json")
            return result

        except json.JSONDecodeError as e:
            print(f"[RawPlanHandler] Attempt {attempt + 1} JSON parse error: {e}. Attempting repair.")
            try:
                repaired = repair_json(text)
                print(f"[RawPlanHandler] Repaired JSON (tail): {repaired[-50:]}")
                result = json.loads(repaired)
                print(f"[RawPlanHandler] Rules extracted (repaired): {len(result.get('extracted_rules', []))}")
                save_plan(result, f"{doc_id}_plan.json")
                return result
            except Exception as repair_err:
                last_error = f"Repair failed: {repair_err}"
                print(f"[RawPlanHandler] Attempt {attempt + 1}: {last_error}")
        except Exception as e:
            last_error = str(e)
            print(f"[RawPlanHandler] Attempt {attempt + 1}: {last_error}")

    return {"extracted_rules": [], "open_questions": [], "error": f"Failed after {max_retries} attempts: {last_error}"}


if __name__ == "__main__":
    raw_plan_handler(None)
