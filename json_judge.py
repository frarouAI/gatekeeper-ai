import json
from claude_backend import ClaudeBackend


class JSONCodeJudge:
    def __init__(self, model="claude-sonnet-4-20250514"):
        self.backend = ClaudeBackend(model=model)

    def judge(self, code: str) -> dict:
        system_prompt = """
You are a strict code judge.

You MUST return your verdict as strict JSON using EXACTLY this schema:

{
  "pass": true or false,
  "score": 0-100,
  "issues": ["string", ...],
  "summary": "string"
}

Rules:
- "pass" is true only if the code is fully correct and production-safe.
- "score" reflects overall quality and correctness.
- "issues" must be empty if pass=true.
- "summary" must be concise (1–3 sentences).
- Output ONLY valid JSON. No markdown. No commentary.
"""

        user_prompt = f"""
Review this code:

{code}
"""

        raw = self.backend.judge(system_prompt, user_prompt)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {
                "pass": False,
                "score": 0,
                "issues": ["Model did not return valid JSON"],
                "summary": raw[:500]
            }

        return data


if __name__ == "__main__":
    code = """
def add(a, b):
    return a + b
"""

    judge = JSONCodeJudge()
    verdict = judge.judge(code)
    print(json.dumps(verdict, indent=2))
