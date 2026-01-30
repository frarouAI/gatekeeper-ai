def propose_skills(result: dict) -> list[dict]:
    """
    Translate judge failures into skill intents (observe-only).
    """
    if not result.get("non_compliant_files"):
        return []

    return [{
        "skill_id": "code.test_fixer",
        "capability": "propose_code_fix",
        "confidence": 0.75,
        "reason": "Non-compliant files detected by judge"
    }]
