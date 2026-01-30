"""
Owner Mapping Engine (v1)

Maps file paths to responsible owners.
"""

import json
import fnmatch
from pathlib import Path
from typing import Dict, List

OWNERS_FILE = Path(".gatekeeper/owners.json")
SCHEMA_FILE = Path("schemas/owners_v1.json")


def load_owners() -> List[Dict]:
    if not OWNERS_FILE.exists():
        return []

    return json.loads(OWNERS_FILE.read_text())["owners"]


def resolve_owner(filepath: str, owners: List[Dict]) -> List[str]:
    matched = []

    for owner in owners:
        for pattern in owner["paths"]:
            if fnmatch.fnmatch(filepath, pattern):
                matched.append(owner["name"])
                break

    return matched or ["unowned"]


def map_failures_to_owners(files: List[Dict]) -> Dict[str, Dict]:
    owners = load_owners()
    report: Dict[str, Dict] = {}

    for f in files:
        if f.get("judge", {}).get("compliant", True):
            continue

        path = f["filepath"]
        failures = f["judge"].get("failures", [])

        owner_names = resolve_owner(path, owners)

        for owner in owner_names:
            entry = report.setdefault(
                owner,
                {"files": [], "failure_count": 0},
            )

            entry["files"].append(path)
            entry["failure_count"] += len(failures)

    return report
