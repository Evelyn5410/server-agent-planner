import json
from app.llm_client import client
from app.constants import EXTRACTOR_SYSTEM_PROMPT, MODEL

def extract_rules(chunk: str) -> dict:
    from google.genai import types
    import re
    import time

    def repair_json(text: str) -> str:
        """
        Attempts to repair truncated JSON by closing open strings, arrays, and objects.
        """
        stack = []
        in_string = False
        escape = False
        
        # Iterate to find the point where valid JSON ends or truncation occurs
        for char in text:
            if in_string:
                if escape:
                    escape = False
                elif char == '\\':
                    escape = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == '{':
                    stack.append('}')
                elif char == '[':
                    stack.append(']')
                elif char == '}' or char == ']':
                    if stack and stack[-1] == char:
                        stack.pop()
                    else:
                        # Mismatched closer - likely garbage or error. 
                        # We could stop here, but simple repair is to just let it be 
                        # and see if closing what we have helps, or return current text.
                        # For now, let's just continue and assume maybe we missed an opener?
                        # Or strictly, this is invalid.
                        pass
        
        # Reconstruct
        result = text
        if in_string:
            result += '"'
        
        if stack:
            result += "".join(reversed(stack))
            
        return result

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

    retries = 3
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    {"role": "user", "parts": [{"text": f"{EXTRACTOR_SYSTEM_PROMPT}\n\nDOCUMENT CHUNK:\n{chunk}"}]},
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                    response_schema=EXTRACTOR_SCHEMA,
                ),
            )

            try:
                raw_text = response.text
            except Exception as e:
                print(f"[Extractor] Error accessing response.text: {e}")
                continue

            if not raw_text or not raw_text.strip():
                print(f"[Extractor] Warning: Empty response from LLM (attempt {attempt+1})")
                continue

            # Strip markdown code blocks if present
            text = raw_text.strip()
            if text.startswith("```"):
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
