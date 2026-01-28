#!/usr/bin/env python3
import argparse
import sys
import json
from pathlib import Path
from multi_judge import MultiAgentCodeJudge

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?')
    parser.add_argument('--gate', action='store_true')
    parser.add_argument('--profile', default='strict')
    args = parser.parse_args()
    
    if not args.path:
        print("Usage: python3 claude_cli.py <file.py> [--gate] [--profile strict]")
        sys.exit(1)
    
    judge = MultiAgentCodeJudge(engine_version="v2", profile=args.profile)
    result = judge.judge(args.path)
    
    print(json.dumps(result, indent=2))
    
    # Exit codes for automation
    if args.gate and not result["gate_pass"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

def collectrepofiles(root):
    files = {}
    for path in root.rglob('*.py'):
        if '.git' in path.parts or '__pycache__' in path.parts: continue
        try:
            files[str(path)] = path.read_text()
        except: pass
    return files
