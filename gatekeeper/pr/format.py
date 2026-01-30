from typing import List
from gatekeeper.explain import Explanation


_KIND_TITLES = {
    "forbidden_path": "❌ Forbidden Path Violation",
    "strict_escalation": "❌ Strict Profile Escalation",
    "fixable_failure": "⚠️ Fixable Structural Failure",
}


def _bullet(lines: List[str]) -> List[str]:
    return [f"- {line}" for line in lines]


def _code(items: List[str]) -> List[str]:
    return [f"`{item}`" for item in items]


def format_pr_comment(explanation: Explanation) -> str:
    """
    Format an Explanation as a GitHub PR comment (Markdown).

    PURE PRESENTATION.
    Deterministic.
    No policy inference.
    """

    lines: List[str] = []

    # Title
    title = _KIND_TITLES.get(explanation.kind, "❌ Gatekeeper Failure")
    lines.append(f"## {title}")
    lines.append("")

    # Summary
    lines.append("**Summary**")
    lines.append("")
    lines.append(explanation.summary)
    lines.append("")

    # Details
    if explanation.files or explanation.rule_ids or explanation.bullets:
        lines.append("**Details**")
        lines.append("")

        if explanation.files:
            lines.append("**Files**")
            lines.extend(_bullet(_code(sorted(explanation.files))))
            lines.append("")

        if explanation.rule_ids:
            lines.append("**Rules**")
            lines.extend(_bullet(_code(sorted(explanation.rule_ids))))
            lines.append("")

        if explanation.bullets:
            lines.append("**Facts**")
            lines.extend(_bullet(explanation.bullets))
            lines.append("")

    # Autofix
    lines.append("**Autofix**")
    if explanation.autofix_attempted:
        lines.append("- Attempted")
    else:
        reason = explanation.autofix_blocked_reason or "not applicable"
        lines.append(f"- Disabled ({reason})")

    return "\n".join(lines).rstrip()
