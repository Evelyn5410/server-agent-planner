import json
import time
from app.llm_client import client, MODEL

PLANNER_SYSTEM_PROMPT = """
You are a PLANNING module in a controlled AI system.

Your job is to analyze the user request and produce a STRUCTURED PLAN.
You do NOT generate final answers.
You do NOT explain your reasoning.
You ONLY output valid JSON that follows the schema below.

Schema:
{
  "task": string,
  "status": "approved" | "rejected",
  "constraints": string[],
  "assumptions": string[],
  "output_requirements": string[]
}
"""


def plan(user_input: str) -> dict:
    from google.genai import types
    import re

    start = time.time()

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": f"{PLANNER_SYSTEM_PROMPT}\n\nUser request:\n{user_input}"}]},
        ],
        config=types.GenerateContentConfig(
            temperature=0.0,
            maxOutputTokens=512,
        ),
    )

    elapsed = time.time() - start

    raw_text = response.text

    # Debug: log the raw response
    print(f"[Planner] Raw response length: {len(raw_text) if raw_text else 0}")
    print(f"[Planner] Raw response preview: {raw_text[:200] if raw_text else 'EMPTY'}...")

    # Handle empty response
    if not raw_text or not raw_text.strip():
        print("[Planner] Warning: Empty response from LLM")
        return {
            "plan": {"task": user_input, "status": "rejected", "constraints": [], "assumptions": [], "output_requirements": []},
            "latency_sec": round(elapsed, 3),
            "usage": response.usage_metadata,
            "error": "Empty LLM response"
        }

    # Strip markdown code blocks if present
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    try:
        plan_json = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[Planner] JSON parse error: {e}")
        print(f"[Planner] Failed to parse: {text[:500]}")
        return {
            "plan": {"task": user_input, "status": "rejected", "constraints": [], "assumptions": [], "output_requirements": []},
            "latency_sec": round(elapsed, 3),
            "usage": response.usage_metadata,
            "error": f"JSON parse error: {str(e)}"
        }

    return {
        "plan": plan_json,
        "latency_sec": round(elapsed, 3),
        "usage": response.usage_metadata,
    }
