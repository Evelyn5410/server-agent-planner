RESPONSE_SCHEMA_FOR_PROCESS_RAW_DOC = {
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
    "required": ["extracted_rules", "open_questions"]
}

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

GENERATOR_SYSTEM_PROMPT = """
You are a GENERATION module in a controlled AI system.

You must follow the provided PLAN exactly.
You do NOT add new constraints.
You do NOT explain your reasoning.
Output ONLY the final result.
"""

MODEL = "gemini-2.5-flash"
