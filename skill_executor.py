class SkillExecutor:
    def execute(self, *, skill: dict, intent: dict, mode: str = "observe") -> dict:
        if mode != "observe":
            raise RuntimeError("Execution disabled (observe-only mode)")

        return {
            "status": "observed",
            "skill": skill["skill"]["id"],
            "reason": intent["reason"],
            "confidence": intent["confidence"]
        }
