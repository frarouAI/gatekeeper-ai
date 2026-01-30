from typing import List, Set
import os
import json
import hashlib

from repair_types import RepairPlan

# Phase 5A safety guard: only no-op allowed
ALLOWED_ACTIONS: Set[str] = {"noop"}


def propose_repairs(judgements) -> List[RepairPlan]:
    """
    Phase 5A.x: proposal stub.
    Claude may suggest repairs later, but for now this is inert.
    """
    return []


def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def apply_repairs(
    plans: List[RepairPlan],
    allowed_files: Set[str],
    audit_log_path: str,
    iteration: int,
) -> bool:
    """
    Phase 5A.x: audit-only repair loop.
    Never mutates files. Always returns False.
    """

    audit_entry = {
        "iteration": iteration,
        "repairs": [],
    }

    allowed_realpaths = {os.path.realpath(p) for p in allowed_files}

    for plan in plans:
        if plan.action not in ALLOWED_ACTIONS:
            continue

        real_path = os.path.realpath(plan.file_path)
        if real_path not in allowed_realpaths:
            continue

        before = _file_hash(real_path)
        after = before  # inert by design

        audit_entry["repairs"].append(
            {
                "rule_id": plan.rule_id,
                "file": real_path,
                "action": plan.action,
                "description": plan.description,
                "before_hash": before,
                "after_hash": after,
            }
        )

    os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)
    with open(audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(audit_entry, sort_keys=True) + "\n")

    # Never claim mutation in Phase 5A
    return False
