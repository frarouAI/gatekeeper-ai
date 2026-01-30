from typing import List
from gatekeeper.explain import Explanation


def _indent(lines: List[str], spaces: int = 2) -> List[str]:
    prefix = " " * spaces
    return [f"{prefix}{line}" for line in lines]


def render_explanation(explanation: Explanation) -> str:
    """
    Render a human-readable CLI explanation.

    PURE PRESENTATION.
    Deterministic. Snapshot-safe.
    """

    lines: List[str] = []

    # Header
    lines.append("✖ Gatekeeper failed")
    lines.append("")

    # Summary
    lines.append("Summary:")
    lines.extend(_indent([explanation.summary]))
    lines.append("")

    # Details
    lines.append("Details:")
    details: List[str] = []

    if explanation.files:
        details.append("Files:")
        details.extend(_indent(sorted(explanation.files)))

    if explanation.rule_ids:
        if details:
            details.append("")
        details.append("Rules:")
        details.extend(_indent(sorted(explanation.rule_ids)))

    if explanation.bullets:
        if details:
            details.append("")
        details.append("Facts:")
        details.extend(_indent(explanation.bullets))

    lines.extend(_indent(details))
    lines.append("")

    # Autofix
    lines.append("Autofix:")
    if explanation.autofix_attempted:
        lines.extend(_indent(["Attempted"]))
    else:
        reason = explanation.autofix_blocked_reason or "not applicable"
        lines.extend(_indent([f"Disabled ({reason})"]))

    return "\n".join(lines)
