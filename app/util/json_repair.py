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
                    pass
    
    # Reconstruct
    result = text
    if in_string:
        result += '"'
    
    if stack:
        result += "".join(reversed(stack))
        
    return result
