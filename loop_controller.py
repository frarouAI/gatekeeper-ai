"""
Loop Controller — Gatekeeper AI
Enables controlled iterative repair with re-judging and artifact persistence.
"""

from typing import Dict
from judge import judge_code
from repair_agent import generate_repairs
from repair_schema import apply_patches_preview, apply_patches_to_file
from artifact_writer import write_repair_artifact


def run_loop(
    filepath: str,
    judge_result: Dict,
    profile: str,
    enable_repair: bool = False,
    dry_run: bool = True,
    max_iterations: int = 3
) -> dict:
    """
    Controlled repair loop with re-judging and artifact persistence.
    """

    with open(filepath, "r") as f:
        original_code = f.read()

    current_code = original_code
    history = []

    prev_failure_count = len(judge_result.get("failures", []))

    for iteration in range(max_iterations):
        # Re-judge current code
        judge = judge_code(current_code, profile)
        failures = judge.get("failures", [])
        failure_count = len(failures)

        # Stop if clean
        if failure_count == 0:
            break

        # Stop if no improvement
        if iteration > 0 and failure_count >= prev_failure_count:
            break

        prev_failure_count = failure_count

        # Propose repairs
        repairs = generate_repairs(current_code, failures, profile)

        if not repairs:
            break

        # Apply preview or real patch
        if dry_run:
            new_code = apply_patches_preview(current_code, repairs)
        else:
            # Apply patches to file
            apply_result = apply_patches_to_file(
                filepath=filepath,
                patches=repairs,
                dry_run=False,
                create_backup=True
            )
            # Get the new code from the preview (what was applied)
            new_code = apply_patches_preview(current_code, repairs)
            # Actually write it
            with open(filepath, "w") as f:
                f.write(new_code)

        history.append({
            "iteration": iteration + 1,
            "failures_before": failure_count,
            "repairs_proposed": len(repairs),
            "repairs": repairs
        })

        current_code = new_code

    # Final judge
    final_judge = judge_code(current_code, profile)

    initial_failures = judge_result.get("failures", [])
    final_failures = final_judge.get("failures", [])
    
    repair_confidence = (
        1.0
        if len(initial_failures) == 0
        else max(0.0, 1 - (len(final_failures) / len(initial_failures)))
    )

    improved = len(final_failures) < len(initial_failures)
    
    # Write immutable artifact
    mode = "repair-live" if enable_repair and not dry_run else "repair-dry-run"
    
    artifact_path = write_repair_artifact(
        filepath=filepath,
        profile=profile,
        mode=mode,
        initial_failures=initial_failures,
        final_failures=final_failures,
        iterations_used=len(history),
        repair_confidence=repair_confidence,
        history=history,
        diff_before=original_code,
        diff_after=current_code,
        improved=improved
    )

    return {
        "mode": mode,
        "filepath": filepath,
        "profile": profile,
        "iterations_used": len(history),
        "initial_failures": initial_failures,
        "final_failures": final_failures,
        "repair_confidence": round(repair_confidence, 3),
        "improved": improved,
        "history": history,
        "diff": {
            "before": original_code,
            "after": current_code,
        },
        "artifact_path": str(artifact_path)
    }
