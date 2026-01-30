#!/usr/bin/env python3

import argparse
import json
import sys

from scanner import scan_target
from policy_engine import apply_policy_engine
from repair_engine import propose_repairs, apply_repairs
from claude_proposer import propose_repairs_with_claude


MAX_REPAIR_ITERATIONS = 3
AUDIT_LOG = ".gatekeeper/repair_audit.jsonl"


def run_gate_mode(target: str, repair: bool, propose: bool) -> int:
    iteration = 0
    previous_violations = None

    while True:
        findings = scan_target(target)
        result = apply_policy_engine(findings)
        summary = result["policy_summary"]

        gate_output = {
            "gate_pass": summary.violations == 0,
            "violations": summary.violations,
            "warnings": summary.warnings,
            "checked_rules": summary.checked_rules,
            "profile": summary.profile,
            "iteration": iteration,
        }

        print(json.dumps(gate_output, indent=2))

        if gate_output["gate_pass"]:
            return 0

        if not repair or iteration >= MAX_REPAIR_ITERATIONS:
            return 1

        if previous_violations is not None and summary.violations >= previous_violations:
            return 1

        previous_violations = summary.violations

        # ---- Repair proposal phase ----
        plans = propose_repairs(result["judgements"])

        if propose:
            claude_plans = propose_repairs_with_claude(
                result["judgements"],
                claude_client=None,  # injected later
            )
            plans.extend(claude_plans)

        allowed_files = {j.finding_id for j in result["judgements"]}

        changed = apply_repairs(
            plans=plans,
            allowed_files=allowed_files,
            audit_log_path=AUDIT_LOG,
            iteration=iteration,
        )

        if not changed:
            return 1

        iteration += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="Target file or directory")
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--repair", action="store_true")
    parser.add_argument(
        "--propose",
        action="store_true",
        help="Allow Claude to propose RepairPlans (proposal-only)",
    )

    args = parser.parse_args()

    if args.gate:
        return run_gate_mode(args.target, args.repair, args.propose)

    print({"success": True})
    return 0


if __name__ == "__main__":
    sys.exit(main())
