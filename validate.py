#!/usr/bin/env python3
"""Standalone code validator with local rules (no API)."""
import sys
import json
import ast
from datetime import datetime, timezone
from pathlib import Path

def validate(code_path, profile="strict"):
    """Validate code without API calls."""
    try:
        code = Path(code_path).read_text()
    except Exception as e:
        return {
            "schema_version": "1.2",
            "engine": "v2",
            "profile": profile,
            "gate_pass": False,
            "score": 0,
            "blocking_failures": ["CORRECTNESS"],
            "error": f"Cannot read file: {e}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    filename = Path(code_path).name
    blocking = []
    score = 90
    gate_pass = True
    
    # VALIDATION RULE #1: Syntax error blocks CORRECTNESS
    try:
        ast.parse(code)
    except SyntaxError as e:
        blocking.append("CORRECTNESS")
        score = 0
        gate_pass = False
    
    # VALIDATION RULE #2: Empty file blocks CORRECTNESS
    if gate_pass and len(code.strip()) < 20:
        blocking.append("CORRECTNESS")
        score = 40
        gate_pass = False
    
    return {
        "schema_version": "1.2",
        "engine": "v2",
        "profile": profile,
        "gate_pass": gate_pass,
        "score": score,
        "blocking_failures": blocking,
        "results": {filename: {"score": score, "pass": gate_pass}},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <file.py> [--profile strict]")
        sys.exit(1)
    
    path = sys.argv[1]
    profile = "strict"
    if "--profile" in sys.argv:
        idx = sys.argv.index("--profile")
        if idx + 1 < len(sys.argv):
            profile = sys.argv[idx + 1]
    
    result = validate(path, profile=profile)
    print(json.dumps(result, indent=2))
    
    if not result["gate_pass"]:
        sys.exit(1)
