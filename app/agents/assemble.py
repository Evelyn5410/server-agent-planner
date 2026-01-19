def build_plan(doc_id, version, rules, conflicts):
    return {
        "document_id": doc_id,
        "version": version,
        "rules": [
            {
                "id": f"RULE-{i+1:03d}",
                **r
            }
            for i, r in enumerate(rules)
        ],
        "open_questions": conflicts
    }
