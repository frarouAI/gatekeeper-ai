import json
from typing import List

from repair_engine import RepairPlan, ALLOWED_ACTIONS
from policy_engine import PolicyJudgement


def _build_prompt(judgements: List[PolicyJudgement]) -> str:
    """
    Claude is instructed to ONLY propose RepairPlans.
    No code. No prose. JSON only.
    """
    items = []
    for j in judgements:
        items.append(
            {
                "rule_id": j.rule_id,
                "file_path": j.finding_id,
                "reason": j.reason,
            }
        )

    return f"""
You are a static analysis assistant.

Your task:
- Propose ZERO OR MORE repair plans
- You MUST NOT suggest file deletion
- You MUST NOT suggest moving files
- You MUST NOT suggest disabling rules

Allowed actions: {sorted(ALLOWED_ACTIONS)}

Return ONLY valid JSON in this exact format:

{{
  "repairs": [
    {{
      "rule_id": "...",
      "file_path": "...",
      "action": "...",
      "description": "..."
    }}
  ]
}}

Input judgements:
{json.dumps(items, indent=2)}
""".strip()


def propose_repairs_with_claude(
    judgements: List[PolicyJudgement],
    claude_client=None,
) -> List[RepairPlan]:
    """
    Claude proposal-only integration.
    If Claude is unavailable, returns [] safely.
    """

    if not judgements or claude_client is None:
        return []

    prompt = _build_prompt(judgements)

    # ---- Claude call (sandboxed) ----
    try:
        response = claude_client(prompt)
    except Exception:
        return []

    try:
        data = json.loads(response)
    except Exception:
        return []

    plans: List[RepairPlan] = []

    for item in data.get("repairs", []):
        try:
            action = item["action"]
            if action not in ALLOWED_ACTIONS:
                continue

            plans.append(
                RepairPlan(
                    rule_id=item["rule_id"],
                    file_path=item["file_path"],
                    action=action,
                    description=item.get("description", ""),
                )
            )
        except Exception:
            continue

    return plans
