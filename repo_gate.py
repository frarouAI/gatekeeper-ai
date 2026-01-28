#!/usr/bin/env python3
"""Repo-wide gate."""
from pathlib import Path
from multijudge import MultiAgentCodeJudge

def collect_py_files(root: Path) -> dict[str, str]:
    files = {}
    for path in root.rglob('*.py'):
        if '.git' in path.parts or '__pycache__' in path.parts:
            continue
        try:
            files[str(path)] = path.read_text()
        except Exception:
            pass
    return files

judge = MultiAgentCodeJudge(profile='strict')
files = collect_py_files(Path('.'))
gate = judge.gate_repo(files)
print(gate)
