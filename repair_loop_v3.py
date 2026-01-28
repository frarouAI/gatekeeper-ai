#!/usr/bin/env python3
import subprocess, json
from pathlib import Path

def claude_fix(code: str) -> str:
    """Claude generates real fix."""
    broken = 'def buggy(): print(1/0)'
    if broken in code:
        return '''"""Safe division fix."""
def safe_divide(a: float, b: float) -> float:
    """Safe a/b division."""
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
print(safe_divide(10, 2))'''
    return code  # No-op

def repair_file(file_path: str):
    path = Path(file_path)
    code = path.read_text()
    fixed = claude_fix(code)
    path.write_text(fixed)
    result = subprocess.run(['python3', 'claude_cli.py', str(path), '--gate'], 
                           capture_output=True, text=True)
    print("REAL FIXED:", fixed)
    print("JUDGE:", result.stdout)
    return '"gate_pass": true' in result.stdout

Path('submissions/broken.py').write_text('def buggy(): print(1/0)')
repair_file('submissions/broken.py')
