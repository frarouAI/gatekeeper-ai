#!/usr/bin/env python3
from pathlib import Path
import subprocess

def repair_file(file_path: str, max_iters: int = 3) -> str:
    path = Path(file_path)
    for i in range(max_iters):
        # Judge
        result = subprocess.run(['python3', 'claude_cli.py', str(path), '--gate', '--profile', 'startup'], 
                               capture_output=True, text=True)
        print(f"Iter {i+1}: {result.stdout}")
        if '"gate_pass": true' in result.stdout:
            return "PASS"
    return "FAILED after 3 attempts"

print(repair_file('submissions/bug.py'))
