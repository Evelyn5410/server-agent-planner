"""
Raw Plan Handler - Single-read document to plan extraction.

Simple endpoint logic: input document → output plan
No metrics tracking here - that's handled by the benchmark pipeline.
"""

import json
import os
import re
import uuid
from google.genai import types
from app.constants import PLAN_SCHEMA, MODEL
from app.llm_client import client
from app.store import save_plan

MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"

# JSON schema to enforce valid response structure
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": ["obligation", "prohibition", "permission"]},
                    "statement": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["id", "type", "statement", "confidence"]
            }
        },
        "open_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rule_ids": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string"}
                },
                "required": ["rule_ids", "reason"]
            }
        }
    },
    "required": ["rules", "open_questions"]
}


def raw_plan_handler(document: str) -> dict:
    """
    Extract plan from document in a single LLM call.

    Args:
        document: Full document text

    Returns:
        Plan dict with 'rules' and 'open_questions'
    """

    prompt = f"""
You are a document analysis system.

Your task:
- Read the FULL document
- Extract ALL rules
- Produce a plan STRICTLY following this JSON schema
- Do not invent rules
- Do not omit rules
- Preserve original meaning and modality
- Output VALID JSON ONLY

Schema:
{PLAN_SCHEMA}

Document:
{document}
"""

    if MOCK_LLM:
        return {
            "rules": [
                {
                    "id": "RULE-001",
                    "type": "requirement",
                    "statement": "Authentication is required for all API endpoints",
                    "confidence": "high"
                },
                {
                    "id": "RULE-002",
                    "type": "constraint",
                    "statement": "Rate limiting must be enforced",
                    "confidence": "high"
                },
                {
                    "id": "RULE-003",
                    "type": "requirement",
                    "statement": "All responses must be in JSON format",
                    "confidence": "medium"
                }
            ],
            "open_questions": []
        }

    max_retries = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    {"role": "user", "parts": [{"text": prompt}]}
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    max_output_tokens=32768,
                    http_options=types.HttpOptions(timeout=600_000),  # 10 min in ms
                )
            )

            raw_text = response.text
            print(f"[RawPlanHandler] Response length: {len(raw_text) if raw_text else 0}")

            if not raw_text:
                raise RuntimeError("Empty response from LLM")

            # Strip markdown code blocks if present
            text = raw_text.strip()
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)

            result = json.loads(text)
            print(f"[RawPlanHandler] Rules extracted: {len(result.get('rules', []))}")
            
            # Save to store
            save_plan(result, f"process-raw_{uuid.uuid4()}.json")
            
            return result

        except json.JSONDecodeError as e:
            last_error = f"JSON parse error: {e}"
            print(f"[RawPlanHandler] Attempt {attempt + 1}: {last_error}")
        except Exception as e:
            last_error = str(e)
            print(f"[RawPlanHandler] Attempt {attempt + 1}: {last_error}")

    return {"rules": [], "open_questions": [], "error": f"Failed after {max_retries} attempts: {last_error}"}
