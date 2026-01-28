#!/usr/bin/env python3
import subprocess, json
from pathlib import Path

def parse_gate(json_str: str) -> bool:
    try:
        data = json.loads(json_str)
        return data.get('gate_pass', False)
    except:
        return '"gate_pass": true' in json_str

def repair(file_path: str):
    path = Path(file_path)
    code = path.read_text()
    print("BROKEN:", code)
    # SIMULATED CLAUDE FIX (replace with API call)
    fixed = code.replace('1/0', '10/2').replace('buggy', 'safe')
    path.write_text(fixed)
    print("SIMULATED FIX:", fixed)
    result = subprocess.run(['python3', 'claude_cli.py', str(path), '--gate'], 
                           capture_output=True, text=True)
    print("AFTER:", result.stdout)
    return parse_gate(result.stdout)

repair('submissions/broken.py')
