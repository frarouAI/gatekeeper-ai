import os
import subprocess
from typing import List, Set

from policy_engine import Finding


def _git_changed_files(base_ref: str = "HEAD~1") -> Set[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref],
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            os.path.abspath(line.strip())
            for line in result.stdout.splitlines()
            if line.strip()
        }
    except Exception:
        return set()


def _scan_file(path: str) -> Finding:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            line_count = sum(1 for _ in f)
    except Exception:
        line_count = None

    return Finding(
        id=path,
        type="file",
        path=path,
        signal="ok",
        metadata={"line_count": line_count},
    )


def scan_target(path: str) -> List[Finding]:
    findings: List[Finding] = []

    if not path or not os.path.exists(path):
        return findings

    root = os.path.abspath(path)
    changed_files = _git_changed_files()

    # Determine whether PR-diff mode is actually relevant
    relevant_changes = [
        f for f in changed_files
        if f.startswith(root) and os.path.isfile(f)
    ]

    # ---- PR diff mode (only if relevant) ----
    if relevant_changes:
        for file_path in relevant_changes:
            findings.append(_scan_file(file_path))
        return findings

    # ---- Full scan fallback ----
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            file_path = os.path.join(dirpath, name)
            if os.path.isfile(file_path):
                findings.append(_scan_file(file_path))

    return findings
