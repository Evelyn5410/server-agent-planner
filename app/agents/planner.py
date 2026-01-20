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

    plan_json = json.loads(response.text)

    return {
        "plan": plan_json,
        "latency_sec": round(elapsed, 3),
        "usage": response.usage_metadata,
    }
