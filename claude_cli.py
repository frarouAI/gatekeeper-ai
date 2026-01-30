#!/usr/bin/env python3
"""
Gatekeeper AI — CLI
Final, invariant-correct orchestration layer.
"""

import sys
import json
from pathlib import Path

from judge import judge_code
from loop_controller import run_loop


def main():
    try:
        args = sys.argv[1:]
        if not args:
            print(json.dumps({"error": "No path provided"}))
            sys.exit(1)

        target = args[0]
        profile = "strict"
        enable_repair = False
        dry_run = False

        i = 1
        while i < len(args):
            arg = args[i]
            if arg == "--profile" and i + 1 < len(args):
                profile = args[i + 1]
                i += 1
            elif arg in ("--repair", "--repair-live"):
                enable_repair = True
            elif arg == "--repair-dry-run":
                dry_run = True
            i += 1

        # Single source of truth
        judge_result = judge_code(target, profile=profile)

        violations = judge_result.get("violations")
        if violations is None:
            # backward compatibility
            violations = judge_result.get("failure_count", 0)

        # Enforce invariant
        gate_pass = violations == 0

        # Wrap in loop only if needed
        if enable_repair or Path(target).is_dir():
            output = run_loop(
                filepath=target,
                judge_result=judge_result,
                profile=profile,
                enable_repair=enable_repair,
                dry_run=dry_run,
                max_iterations=1,
            )
        else:
            output = judge_result.copy()

        # Enforce invariant AGAIN (cannot be overridden)
        output["violations"] = violations
        output["gate_pass"] = gate_pass
        output["profile"] = profile

        # Phase 5B envelope (still inert)
        output.setdefault("autofix_applied", False)
        output.setdefault("rule_id", None)
        output.setdefault("files_modified", [])
        output.setdefault("audit", None)

        print(json.dumps(output, indent=2))
        sys.exit(0 if gate_pass else 1)

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "gate_pass": False,
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
