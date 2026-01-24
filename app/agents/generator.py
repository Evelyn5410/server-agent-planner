from app.llm_client import client, MODEL
from app.constants import GENERATOR_SYSTEM_PROMPT


def generate(plan: dict) -> str:
    from google.genai import types

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {"role": "user", "parts": [{"text": f"{GENERATOR_SYSTEM_PROMPT}\n\nPLAN:\n{plan}"}]},
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=1024,
            response_mime_type="text/plain",
        ),
    )

    return response.text
