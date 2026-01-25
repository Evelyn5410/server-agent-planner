def normalize_rule(rule):
    return {
        "type": rule.get("type", "unknown").lower(),
        "statement": rule.get("statement", "").strip().rstrip("."),
        "confidence": rule.get("confidence", "low")
    }
