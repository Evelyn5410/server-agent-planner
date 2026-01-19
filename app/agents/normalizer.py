def normalize_rule(rule):
    return {
        "type": rule["type"].lower(),
        "statement": rule["statement"].strip().rstrip("."),
        "confidence": rule["confidence"]
    }
