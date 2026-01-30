"""
Owner Policy Engine — v1.1

Supports modes:
- observe  → report only
- warn     → notify owners, do not block
- enforce  → block CI if violations exist
"""

from typing import Dict, List


def apply_owner_policy(
    owners_report: Dict,
    result: Dict,
    config: Dict = None,
) -> Dict:
    """
    Apply owner-based policy decisions.

    Returns a structured policy decision used by CI gate.
    """

    config = config or {}
    policy_cfg = config.get("owner_policy", {})

    mode = policy_cfg.get("mode", "observe")
    max_unowned = policy_cfg.get("max_unowned_failures", 0)

    unowned_files = owners_report.get("unowned_files", [])
    unowned_failures = len(unowned_files)

    violations: List[str] = []
    notifications: List[Dict] = []

    # -------------------------------
    # Policy logic
    # -------------------------------
    if unowned_failures > max_unowned:
        violations.append(
            f"Unowned failing files exceed limit ({unowned_failures} > {max_unowned})"
        )

    # -------------------------------
    # Notification logic
    # -------------------------------
    if unowned_failures > 0 and mode in ("warn", "enforce"):
        notifications.append({
            "type": "owner_policy",
            "severity": "warning" if mode == "warn" else "critical",
            "message": (
                f"{unowned_failures} failing files have no owner assigned.\n"
                "Add CODEOWNERS entries to assign responsibility."
            ),
            "files": unowned_files[:10],  # cap for safety
        })

    # -------------------------------
    # Enforcement
    # -------------------------------
    should_block = False
    if mode == "enforce" and violations:
        should_block = True

    # -------------------------------
    # Decision object
    # -------------------------------
    decision = {
        "mode": mode,
        "should_block": should_block,
        "unowned_failures": unowned_failures,
        "block_reasons": violations,
        "notifications": notifications,
        "policy_summary": {
            "mode": mode,
            "total_unowned_files": unowned_failures,
            "total_owners_affected": len(owners_report.get("owners", {})),
        },
    }

    return decision
