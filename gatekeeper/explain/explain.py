from dataclasses import dataclass
from typing import List, Literal, Optional


ExplanationKind = Literal[
    "forbidden_path",
    "strict_escalation",
    "fixable_failure",
]


@dataclass(frozen=True)
class Explanation:
    kind: ExplanationKind
    summary: str
    bullets: List[str]
    rule_ids: List[str]
    files: List[str]
    autofix_attempted: bool
    autofix_blocked_reason: Optional[str]


def explain_verdict(verdict) -> Explanation:
    """
    Produce a deterministic, human-readable explanation
    derived strictly from the final verdict.

    This function MUST NOT infer, repair, or modify state.
    """

    failures = getattr(verdict, "failures", []) or []

    # --- Rule 1: Forbidden paths dominate everything ---
    forbidden = [
        f for f in failures
        if getattr(f, "kind", None) == "forbidden_path"
    ]

    if forbidden:
        files = sorted(
            {file for f in forbidden for file in getattr(f, "files", [])}
        )
        rule_ids = sorted({f.rule_id for f in forbidden})

        return Explanation(
            kind="forbidden_path",
            summary=(
                "This change modifies files under forbidden paths. "
                "Forbidden paths are absolute and dominate all enforcement logic."
            ),
            bullets=[
                "One or more modified files are located in forbidden paths",
                "Forbidden paths cannot be repaired or bypassed",
                "Autofix is intentionally disabled for this class of violation",
            ],
            rule_ids=rule_ids,
            files=files,
            autofix_attempted=False,
            autofix_blocked_reason="forbidden paths are non-negotiable",
        )

    # --- Rule 2: Strict profile escalation ---
    if getattr(verdict, "profile", None) == "strict":
        escalated = [
            f for f in failures
            if getattr(f, "kind", None) == "warning"
        ]

        if escalated:
            files = sorted(
                {file for f in escalated for file in getattr(f, "files", [])}
            )
            rule_ids = sorted({f.rule_id for f in escalated})

            return Explanation(
                kind="strict_escalation",
                summary=(
                    "This change failed because warnings are treated as errors "
                    "under the strict enforcement profile."
                ),
                bullets=[
                    "One or more warnings were detected",
                    "The strict profile escalates warnings to failures",
                    "No automatic repair was attempted",
                ],
                rule_ids=rule_ids,
                files=files,
                autofix_attempted=False,
                autofix_blocked_reason="strict profile escalation",
            )

    # --- Rule 3: Fixable structural failure ---
    if failures:
        files = sorted(
            {file for f in failures for file in getattr(f, "files", [])}
        )
        rule_ids = sorted({f.rule_id for f in failures})

        return Explanation(
            kind="fixable_failure",
            summary=(
                "This change failed due to fixable structural issues "
                "that may be eligible for a bounded autofix."
            ),
            bullets=[
                "Structural rule violations were detected",
                "These violations are potentially repairable",
                "No repair has been applied at this stage",
            ],
            rule_ids=rule_ids,
            files=files,
            autofix_attempted=False,
            autofix_blocked_reason=None,
        )

    # --- Defensive fallback (should never happen) ---
    return Explanation(
        kind="fixable_failure",
        summary="No violations were detected.",
        bullets=[],
        rule_ids=[],
        files=[],
        autofix_attempted=False,
        autofix_blocked_reason=None,
    )
