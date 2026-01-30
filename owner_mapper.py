"""
Owner Mapper v1

Maps failing files to owners using CODEOWNERS.
"""

from pathlib import Path
from collections import defaultdict
import fnmatch
import json


CODEOWNERS_PATH = Path(".github/CODEOWNERS")


def load_codeowners():
    if not CODEOWNERS_PATH.exists():
        return []

    rules = []
    for line in CODEOWNERS_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        pattern = parts[0]
        owners = parts[1:]
        rules.append((pattern, owners))

    return rules


def map_files_to_owners(files):
    rules = load_codeowners()
    owners_map = defaultdict(lambda: {"files": [], "blocking_issues": 0})
    unowned = []

    for file in files:
        matched = False
        for pattern, owners in rules:
            if fnmatch.fnmatch(file, pattern):
                for owner in owners:
                    owners_map[owner]["files"].append(file)
                    owners_map[owner]["blocking_issues"] += 1
                matched = True
                break

        if not matched:
            unowned.append(file)

    return {
        "schema_version": "owners-v1",
        "owners": owners_map,
        "unowned_files": unowned,
    }


def write_owners_report(failing_files, output_dir=Path(".gatekeeper")):
    report = map_files_to_owners(failing_files)
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / "owners_report.json"
    path.write_text(json.dumps(report, indent=2))

    return report
