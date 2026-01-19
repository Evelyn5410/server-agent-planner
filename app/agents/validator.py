def validate(output: str) -> dict:
    issues = []
    if len(output) > 1000:
        issues.append("too_long")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }
