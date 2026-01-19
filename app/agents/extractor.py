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
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "system", "parts": [EXTRACTOR_SYSTEM_PROMPT]},
            {"role": "user", "parts": [f"DOCUMENT CHUNK:\n{chunk}"]},
        ],
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 512,
        },
    )

    return json.loads(response.text)
