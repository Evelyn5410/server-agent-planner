def detect_conflicts(rules):
    conflicts = []

    statements = [r["statement"].lower() for r in rules]
    for s in statements:
        if "must" in s and "must not" in s:
            conflicts.append(s)

    return conflicts
