import json
from app.llm_client import client
from app.constants import EXTRACTOR_SYSTEM_PROMPT, MODEL

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
            maxOutputTokens=2048,
            responseMimeType="application/json",
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
            except json.JSONDecodeError:
                print(f"[Extractor] JSON parse error (attempt {attempt+1}). Attempting stack-based repair.")
                
                try:
                    repaired = repair_json(text)
                    print(f"[Extractor] Repaired JSON (tail): {repaired[-50:]}")
                    return json.loads(repaired)
                except json.JSONDecodeError as repair_err:
                    print(f"[Extractor] Repair failed: {repair_err}")
                    # Try one last fallback: find last valid '}' and close from there (the strategy 2 from before)
                    try:
                        last_brace = text.rfind("}")
                        if last_brace != -1:
                            fallback = text[:last_brace+1] + "]}" 
                            return json.loads(fallback)
                    except:
                        pass
                    continue

        except Exception as e:
            print(f"[Extractor] API error (attempt {attempt+1}): {e}")
            time.sleep(1)

    print("[Extractor] Failed to extract rules after retries.")
    return {"extracted_rules": []}
