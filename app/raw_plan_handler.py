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
  "rules": [
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
                    max_output_tokens=65536,
                    http_options=types.HttpOptions(timeout=600_000),
                ),
            )

            raw_text = ""
            finish_reason = None
            for chunk in response_stream:
                if chunk.text:
                    raw_text += chunk.text
                if chunk.candidates and chunk.candidates[0].finish_reason:
                    finish_reason = chunk.candidates[0].finish_reason
            
            print(f"[RawPlanHandler] Response length: {len(raw_text)}")
            if finish_reason:
                 print(f"[RawPlanHandler] Finish Reason: {finish_reason}")

            if not raw_text:
                raise RuntimeError("Empty response from LLM")

            # Strip markdown code blocks if present
            text = raw_text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)

            result = {"rules": [], "open_questions": []}
            is_truncated = (finish_reason == "MAX_TOKENS") or (finish_reason == 2) # 2 is MAX_TOKENS in some enums

            try:
                result = json.loads(text)
            except json.JSONDecodeError as e:
                print(f"[RawPlanHandler] JSON parse error: {e}. Attempting repair.")
                try:
                    repaired = repair_json(text)
                    result = json.loads(repaired)
                    print(f"[RawPlanHandler] Repaired JSON. Rules: {len(result.get('rules', []))}")
                    result["warning"] = "Response was truncated and repaired."
                except Exception as repair_err:
                    print(f"[RawPlanHandler] Repair failed: {repair_err}")
                    result["error"] = f"JSON parse failed: {e}"
            
            if is_truncated:
                result["finish_reason"] = "MAX_TOKENS"
                print("[RawPlanHandler] WARNING: Token limit exceeded.")

            # Ensure rules key exists
            if "rules" not in result:
                result["rules"] = []
            
            print(f"[RawPlanHandler] Rules extracted: {len(result.get('rules', []))}")
            save_plan(result, f"{doc_id}_plan.json")
            return result

        except Exception as e:
            last_error = str(e)
            print(f"[RawPlanHandler] Attempt {attempt + 1} failed: {last_error}")

    return {"rules": [], "open_questions": [], "error": f"Failed after {max_retries} attempts: {last_error}"}


if __name__ == "__main__":
    raw_plan_handler(None)
