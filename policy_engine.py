"""
Policy Engine v1

Evaluates CI results against global + owner-based rules.
"""

import json
from pathlib import Path
from typing import Dict, List

POLICY_FILE = Path(".gatekeeper/policy.json")
SCHEMA_FILE = Path("schemas/policy_v1.json")


def load_policy() -> Dict:
    if not POLICY_FILE.exists():
        return {
            "schema_version": "policy-v1",
            "rules": {}
        }

    return json.loads(POLICY_FILE.read_text())


def evaluate_policy(
    policy: Dict,
    baseline_score: float,
    current_score: float,
    blocking_issues: int,
    owners_report: Dict[str, Dict]
) -> Dict:
    violations: List[str] = []
    rules = policy.get("rules", {})

    # -----------------------------
    # Global rules
    # -----------------------------
    global_rules = rules.get("global", {})

    max_blocking = global_rules.get("max_blocking_files")
    if max_blocking is not None and blocking_issues > max_blocking:
        violations.append(
            f"Blocking files exceed global limit ({blocking_issues} > {max_blocking})"
        )

    # -----------------------------
    # Owner rules
    # -----------------------------
    owner_rules = rules.get("owners", {})

    for owner, data in owners_report.items():
        rules_for_owner = owner_rules.get(owner)
        if not rules_for_owner:
            continue

        files = len(set(data.get("files", [])))
        failures = data.get("failure_count", 0)

        max_files = rules_for_owner.get("max_blocking_files")
        if max_files is not None and files > max_files:
            violations.append(
                f"Owner '{owner}' exceeds blocking files limit ({files} > {max_files})"
            )

        max_failures = rules_for_owner.get("max_failures")
        if max_failures is not None and failures > max_failures:
            violations.append(
                f"Owner '{owner}' exceeds failure limit ({failures} > {max_failures})"
            )

    return {
        "allowed": len(violations) == 0,
        "violations": violations
    }
