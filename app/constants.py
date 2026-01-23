PLAN_SCHEMA = """
{
  "rules": [
    {
      "id": "RULE-<number>",
      "type": "obligation | prohibition | permission",
      "statement": "string",
      "confidence": "low | medium | high"
    }
  ],
  "open_questions": [
    {
      "rule_ids": ["RULE-1", "RULE-2"],
      "reason": "string"
    }
  ]
}
"""

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

GENERATOR_SYSTEM_PROMPT = """
You are a GENERATION module in a controlled AI system.

You must follow the provided PLAN exactly.
You do NOT add new constraints.
You do NOT explain your reasoning.
Output ONLY the final result.
"""

MODEL = "gemini-2.5-flash"
