"""
Gatekeeper repair / iteration controller.

This module NEVER evaluates files.
It only wraps an existing judge_result and
controls repair lifecycle + auditing.
"""

def run_loop(
    filepath: str,
    judge_result: dict,
    profile: str,
    enable_repair: bool = False,
    dry_run: bool = False,
    max_iterations: int = 1,
):
    # Phase 5A: audit-only, inert loop
    iteration = 0

    violations = judge_result.get("violations", 0)
    compliant = judge_result.get("compliant", violations == 0)

    result = {
        **judge_result,
        "profile": profile,
        "iteration": iteration,
        "gate_pass": compliant,
    }

    # Repair is present but inert
    if enable_repair:
        result["repair_attempted"] = True
        result["repair_mode"] = "dry-run" if dry_run else "audit-only"

    return result
