def get_security_prompt(context: str) -> str:
    base_prompt = (
        "You are a security reviewer. Look for vulnerabilities, unsafe patterns, "
        "input validation issues, injection risks, and misuse of dangerous APIs."
    )

    if context == "judge_internal":
        return base_prompt + """

CONTEXT: judge_internal — This is judge infrastructure code.

For judge_internal context, ALLOW these patterns when used for legitimate judge operations:
- exec()
- ast.parse()
- compile()
- open()
- __import__ / importlib

Still flag real vulnerabilities regardless of context.
"""
    return base_prompt


def get_correctness_prompt(context: str) -> str:
    base_prompt = (
        "You are a strict code correctness reviewer. Focus on logic, edge cases, "
        "type safety, and whether the code behaves correctly for all reasonable inputs."
    )

    if context == "judge_internal":
        return base_prompt + """

CONTEXT: judge_internal — This is judge infrastructure code.

Give positive correctness signals for:
- defensive coding
- explicit error handling
- deterministic logic
- config separation
- boundary checks

Do NOT fail correctness for:
- missing docstrings
- missing type hints
- dynamic orchestration logic
- glue code patterns

Focus on functional correctness over style polish.
"""
    return base_prompt


AGENTS = {
    "correctness": {
        "prompt_fn": get_correctness_prompt
    },
    "security": {
        "prompt_fn": get_security_prompt
    },
    "performance": {
        "system_prompt": (
            "You are a performance reviewer. Analyze time and space complexity, "
            "efficiency, scalability, and unnecessary overhead."
        )
    },
    "style": {
        "system_prompt": (
            "You are a Python style reviewer. Check readability, naming, docstrings, "
            "formatting, PEP8 compliance, and general maintainability."
        )
    },
}


AGENT_POLICY = {
    "correctness": {"weight": 2.0, "blocking": True},
    "security":    {"weight": 2.0, "blocking": True},
    "performance": {"weight": 1.0, "blocking": False},
    "style":       {"weight": 0.5, "blocking": False},
}


PROFILES = {
    "startup": {"threshold": 75},
    "strict":  {"threshold": 85},
    "relaxed": {"threshold": 65},
}
