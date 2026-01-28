import json
from datetime import datetime, timezone

from claude_backend import ClaudeBackend

SCHEMA_VERSION = "1.2"

AGENTS = {
    "correctness": (
        "You are a strict code correctness reviewer. Focus on logic, edge cases, "
        "type safety, and whether the code behaves correctly for all reasonable inputs."
    ),
    "security": (
        "You are a security reviewer. Look for vulnerabilities, unsafe patterns, "
        "input validation issues, injection risks, and misuse of dangerous APIs."
    ),
    "performance": (
        "You are a performance reviewer. Analyze time and space complexity, "
        "efficiency, scalability, and unnecessary overhead."
    ),
    "style": (
        "You are a Python style reviewer. Check readability, naming, docstrings, "
        "formatting, PEP8 compliance, and general maintainability."
    ),
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


class EngineV1:
    name = "v1"

    def __init__(self, model="claude-sonnet-4-20250514", profile="startup", max_tokens=1500):
        if profile not in PROFILES:
            raise ValueError(f"Unknown profile '{profile}'. Available: {list(PROFILES.keys())}")

        self.profile_name = profile
        self.threshold = PROFILES[profile]["threshold"]
        self.backend = ClaudeBackend(model=model, max_tokens=max_tokens)

    def _build_prompt(self, agent_name: str, code: str) -> str:
        return f"""
Review the following Python code.

Return STRICT JSON in this exact schema:
{{
  "agent": "{agent_name}",
  "pass": true | false,
  "score": 0-100,
  "issues": ["string", ...],
  "summary": "string"
}}

Rules:
- No markdown
- No commentary outside JSON
- Score meaning:
  90-100 = excellent
  75-89  = good
  60-74  = weak
  <60    = poor

CODE:
{code}
"""

    def _run_agent(self, agent_name: str, code: str) -> dict:
        system_prompt = AGENTS[agent_name]
        user_prompt = self._build_prompt(agent_name, code)

        raw = self.backend.judge(system_prompt, user_prompt)

        try:
            return json.loads(raw)
        except Exception:
            return {
                "agent": agent_name,
                "pass": False,
                "score": 0,
                "issues": ["Model failed to return valid JSON."],
                "summary": "Model failed to return valid JSON."
            }

    def run_agents(self, code: str) -> list[dict]:
        verdicts = []
        for agent_name in AGENTS:
            result = self._run_agent(agent_name, code)
            verdicts.append(result)
        return verdicts

    # Compatibility shim expected by MultiAgentCodeJudge
    def judge(self, code: str):
        return self.run_agents(code)
