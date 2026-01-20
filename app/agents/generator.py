from app.llm_client import client, MODEL

GENERATOR_SYSTEM_PROMPT = """
You are a GENERATION module in a controlled AI system.

You must follow the provided PLAN exactly.
You do NOT add new constraints.
You do NOT explain your reasoning.
Output ONLY the final result.
"""

def generate(plan: dict) -> str:
    from google.genai import types

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": f"{GENERATOR_SYSTEM_PROMPT}\n\nPLAN:\n{plan}"}]},
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            maxOutputTokens=1024,
        ),
    )

    return response.text
