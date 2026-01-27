import json
from datetime import datetime, timezone
from claude_backend import ClaudeBackend

SCHEMA_VERSION = "1.0"

AGENT_POLICY = {
    "correctness": {"weight": 2.0, "blocking": True},
    "security":    {"weight": 2.0, "blocking": True},
    "performance": {"weight": 1.0, "blocking": False},
    "style":       {"weight": 0.5, "blocking": False},
}


class MultiAgentCodeJudge:
    def __init__(self, model="claude-sonnet-4-20250514", max_tokens=1500):
        self.model = model
        self.backend = ClaudeBackend(model=model, max_tokens=max_tokens)

        self.agents = {
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
- No code blocks
- No explanations
- Output must be valid JSON

CODE:
{code}
"""

    def _run_agent(self, agent_name: str, code: str) -> dict:
        system_prompt = self.agents[agent_name]
        user_prompt = self._build_prompt(agent_name, code)

        raw = self.backend.judge(system_prompt, user_prompt)

        try:
            data = json.loads(raw)

            if not isinstance(data, dict):
                raise ValueError("JSON root is not an object")

            required_keys = {"agent", "pass", "score", "issues", "summary"}
            if not required_keys.issubset(data.keys()):
                raise ValueError("Missing required JSON keys")

            return data

        except Exception as e:
            return {
                "agent": agent_name,
                "pass": False,
                "score": 0,
                "issues": [f"Invalid JSON response from model: {e}"],
                "summary": "Model failed to return valid JSON."
            }

    def judge(self, code: str) -> dict:
        verdicts = []
        blocking_failures = []

        total_weighted_score = 0.0
        total_weight = 0.0

        for agent_name in self.agents:
            result = self._run_agent(agent_name, code)
            verdicts.append(result)

            policy = AGENT_POLICY[agent_name]
            weight = policy["weight"]

            total_weighted_score += result["score"] * weight
            total_weight += weight

            if policy["blocking"] and not result["pass"]:
                blocking_failures.append(agent_name)

        average_score = round(total_weighted_score / total_weight, 2)

        policy_pass = len(blocking_failures) == 0

        if not policy_pass:
            overall_pass = False
        else:
            overall_pass = average_score >= 75

        return {
            "schema_version": SCHEMA_VERSION,
            "model": self.model,
            "timestamp": datetime.now(timezone.utc).isoformat(),

            "overall_pass": overall_pass,
            "policy_pass": policy_pass,
            "average_score": average_score,
            "blocking_failures": blocking_failures,
            "verdicts": verdicts
        }


# ---- manual test ----
if __name__ == "__main__":
    code = """
def add(a: float, b: float) -> float:
    \"\"\"Return the sum of two numbers.\"\"\"
    if a is None or b is None:
        raise ValueError("Inputs must not be None")
    return a + b
"""

    judge = MultiAgentCodeJudge()
    result = judge.judge(code)

    print(json.dumps(result, indent=2))
