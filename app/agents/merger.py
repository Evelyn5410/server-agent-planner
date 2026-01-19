def merge_rules(rule_lists):
    seen = set()
    merged = []

    for rules in rule_lists:
        for r in rules:
            key = r["statement"].lower()
            if key not in seen:
                seen.add(key)
                merged.append(r)

    return merged
