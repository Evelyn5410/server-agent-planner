from app.llm_client import client, MODEL

GENERATOR_SYSTEM_PROMPT = """
You are a GENERATION module in a controlled AI system.

You must follow the provided PLAN exactly.
You do NOT add new constraints.
You do NOT explain your reasoning.
Output ONLY the final result.
"""

def generate(plan: dict) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "system", "parts": [GENERATOR_SYSTEM_PROMPT]},
            {"role": "user", "parts": [f"PLAN:\n{plan}"]},
        ],
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 1024,
        },
    )

    return response.text
