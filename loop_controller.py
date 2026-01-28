"""
Loop Controller — Gatekeeper AI

This module defines the control flow for autonomous code judgement
and optional repair iterations.

DESIGN PRINCIPLE:
- Consumes judge output (doesn't call judge directly)
- Orchestrates repair flow
- Enforces dry-run safety
"""

from typing import Dict, List
from repair_agent import generate_repairs


def run_loop(
    filepath: str,
    judge_result: Dict,
    profile: str,
    enable_repair: bool = False,
    dry_run: bool = True,
    max_iterations: int = 3
) -> dict:
    """
    Repair loop controller.
    
    Args:
        filepath: Path to file being judged
        judge_result: Output from judge.judge_code()
        profile: Strictness profile used
        enable_repair: Whether repair is enabled
        dry_run: Safety mode (no file writes)
        max_iterations: Max repair attempts
    
    Returns:
        Structured report with judge results and repair plan
    """
    
    # Read the file
    with open(filepath, 'r') as f:
        code = f.read()
    
    # Extract failures from judge result
    failures = []
    if not judge_result.get("compliant", True):
        failures = judge_result.get("failures", [])
    
    # Map failures to repair slots (intent only, no fixes yet)
    repair_slots = map_failures_to_repair_slots(failures, code)
    
    # Generate repair proposals using Claude (if enabled and failures exist)
    repairs_proposed = []
    if enable_repair and failures:
        repairs_proposed = generate_repairs(code, failures, profile)
    
    # Prepare dry-run output
    return {
        "mode": "repair-dry-run" if dry_run else "repair-live",
        "filepath": filepath,
        "profile": profile,
        "enable_repair": enable_repair,
        "dry_run": dry_run,
        "max_iterations": max_iterations,
        "iterations_used": 0,
        "judge_result": {
            "compliant": judge_result.get("compliant", True),
            "failure_count": len(failures),
            "failures": failures
        },
        "repair_slots": repair_slots,
        "repairs_proposed": repairs_proposed,
        "note": f"Judge executed. {len(repairs_proposed)} repairs proposed by Claude. Execution disabled." if dry_run and enable_repair else "Repair agent not invoked."
    }


def map_failures_to_repair_slots(
    failures: list[str],
    code: str
) -> list[dict]:
    """
    Convert judge failures into empty repair slots.
    No fixes yet. Just intent.
    
    This creates the bridge between judgement and Claude repair agent.
    
    Args:
        failures: List of failure descriptions from judge
        code: Original code (to extract line content)
    
    Returns:
        List of repair slot dictionaries with:
        - line number
        - old content
        - new: "__PROPOSED__" (placeholder)
        - reason (from failure)
        - category (inferred)
        - blocking status
    """
    from repair_schema import ALLOWED_CATEGORIES
    
    repair_slots = []
    lines = code.split('\n')
    
    for failure in failures:
        # Parse failure string (assumes format: "Line N: description")
        if not failure.startswith("Line "):
            continue
        
        try:
            parts = failure.split(":", 1)
            line_num = int(parts[0].replace("Line ", "").strip())
            description = parts[1].strip()
            
            # Infer category from description
            category = "spacing"  # Default
            if "docstring" in description.lower():
                category = "docstring"
            elif "name" in description.lower() or "naming" in description.lower():
                category = "naming"
            elif "type" in description.lower():
                category = "typing"
            elif "security" in description.lower():
                category = "security"
            
            # Determine if blocking (simple heuristic for now)
            blocking = any(keyword in description.lower() for keyword in ["security", "error", "critical"])
            
            # Get old line content
            old_content = lines[line_num - 1] if line_num <= len(lines) else ""
            
            repair_slot = {
                "line": line_num,
                "old": old_content,
                "new": "__PROPOSED__",  # Placeholder - Claude will fill this
                "reason": description,
                "category": category,
                "blocking": blocking
            }
            
            repair_slots.append(repair_slot)
            
        except (ValueError, IndexError) as e:
            print(f"WARNING: Could not parse failure: {failure} ({e})")
            continue
    
    return repair_slots
