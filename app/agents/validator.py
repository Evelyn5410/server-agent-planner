def validate(output: str, plan: dict = None) -> dict:
    """Validate output against the plan. Currently checks length only."""
    issues = []
    if len(output) > 1000:
        issues.append("too_long")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }
