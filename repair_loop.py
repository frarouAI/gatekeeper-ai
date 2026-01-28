#!/usr/bin/env python3
import subprocess
from pathlib import Path

def parse_gate(output: str) -> bool:
    return '"gate_pass": true' in output

def repair_file(file_path: str, max_iters: int = 3):
    path = Path(file_path)
    for i in range(max_iters):
        result = subprocess.run(['python3', 'claude_cli.py', str(path), '--gate'], 
                               capture_output=True, text=True)
        print(f"Iter {i+1}: {result.stdout}")
        if parse_gate(result.stdout):
            return "PASS"
        # Simulate fix (real: Claude API rewrite)
        code = path.read_text()
        fixed = code.replace('1/0', '10/2')
        path.write_text(fixed)
    return "FAILED"

# Test broken code
Path('submissions/broken.py').write_text('def buggy(): print(1/0)')
print(repair_file('submissions/broken.py'))
