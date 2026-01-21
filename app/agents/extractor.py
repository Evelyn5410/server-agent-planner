import json
from app.llm_client import client, MODEL

EXTRACTOR_SYSTEM_PROMPT = """
You are an EXTRACTION module.

Extract explicit rules, constraints, requirements, or prohibitions.

Rules:
- Output ONLY valid JSON.
- Do not summarize.
- Do not explain.
- If nothing is extractable, return an empty list.

Schema:
{
  "extracted_rules": [
    {
      "type": "constraint | behavior | requirement | prohibition",
      "statement": "string",
      "confidence": "high | medium | low"
    }
  ]
}
"""

def extract_rules(chunk: str) -> dict:
    from google.genai import types
    import re

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": f"{EXTRACTOR_SYSTEM_PROMPT}\n\nDOCUMENT CHUNK:\n{chunk}"}]},
        ],
        config=types.GenerateContentConfig(
            temperature=0.0,
            maxOutputTokens=512,
        ),
    )

    try:
        raw_text = response.text
    except Exception as e:
        print(f"[Extractor] Error accessing response.text: {e}")
        return {"extracted_rules": []}

    # Debug: log the raw response
    print(f"[Extractor] Raw response length: {len(raw_text) if raw_text else 0}")
    print(f"[Extractor] Raw response preview: {raw_text[:200] if raw_text else 'EMPTY'}...")

    # Handle empty response
    if not raw_text or not raw_text.strip():
        print("[Extractor] Warning: Empty response from LLM")
        return {"extracted_rules": []}

    # Strip markdown code blocks if present
    text = raw_text.strip()
    if text.startswith("```"):
        # Remove ```json or ``` prefix and ``` suffix
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[Extractor] JSON parse error: {e}")
        print(f"[Extractor] Failed to parse: {text[:500]}")
        # Return empty result on parse failure
        return {"extracted_rules": []}
