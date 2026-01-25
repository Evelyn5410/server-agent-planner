import json
import re
from google.genai import types
from app.llm_client import client
from app.constants import EXTRACTOR_SYSTEM_PROMPT, MODEL
from app.util.json_repair import repair_json

EXTRACTOR_SCHEMA = {
    "type": "object",
    "properties": {
        "extracted_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["constraint", "behavior", "requirement", "prohibition"]},
                    "statement": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]}
                },
                "required": ["type", "statement", "confidence"]
            }
        }
    },
    "required": ["extracted_rules"]
}

def extract_rules(chunk: str) -> dict:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                {"role": "user", "parts": [{"text": f"{EXTRACTOR_SYSTEM_PROMPT}\n\nDOCUMENT CHUNK:\n{chunk}"}]},
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=8192,
                response_mime_type="application/json",
                response_schema=EXTRACTOR_SCHEMA,
            ),
        )

        raw_text = response.text
    except Exception as e:
        print(f"[Extractor] Error generating content: {e}")
        return {"extracted_rules": []}

    if not raw_text or not raw_text.strip():
        print("[Extractor] Warning: Empty response from LLM")
        return {"extracted_rules": []}

    # Strip markdown code blocks if present
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"[Extractor] JSON parse error. Attempting repair.")
        try:
            if response.candidates and response.candidates[0].finish_reason:
                print(f"[Extractor] Finish Reason: {response.candidates[0].finish_reason}")
        except Exception:
            pass
            
        try:
            repaired = repair_json(text)
            print(f"[Extractor] Repaired JSON (tail): {repaired[-50:]}")
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            print(f"[Extractor] Repair failed: {e}")
            return {"extracted_rules": []}

