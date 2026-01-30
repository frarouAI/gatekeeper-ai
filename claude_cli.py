#!/usr/bin/env python3
"""
Claude Code Judge CLI

Usage:
    python3 claude_cli.py <file> [options]

Options:
    --profile <strict|balanced|permissive>  Quality profile (default: strict)
    --repair-dry-run                        Generate repair proposals (no file changes)
    --repair-live                           Apply repairs iteratively (DANGEROUS, auditable)
    --preview                               Show detailed preview of changes
"""

import sys
import json
from pathlib import Path

from judge import judge_code
from loop_controller import run_loop
from repair_schema import display_preview


def main():
    args = sys.argv[1:]
    
    if not args or '--help' in args:
        print(__doc__)
        sys.exit(0)
    
    filepath = args[0]
    profile = "strict"
    repair_dry_run = False
    repair_live = False
    show_preview = False
    
    # Parse flags
    i = 1
    while i < len(args):
        arg = args[i]
        if arg == "--profile" and i + 1 < len(args):
            profile = args[i + 1]
            i += 2
        elif arg == "--repair-dry-run":
            repair_dry_run = True
            i += 1
        elif arg == "--repair-live":
            repair_live = True
            i += 1
        elif arg == "--preview":
            show_preview = True
            repair_dry_run = True
            i += 1
        else:
            i += 1
    
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        code = f.read()
    
    # Step 1: Judge the code
    judge_result = judge_code(code, profile)
    
    # Step 2: Run repair if requested
    if repair_dry_run or repair_live:
        result = run_loop(
            filepath=filepath,
            judge_result=judge_result,
            profile=profile,
            enable_repair=True,
            dry_run=not repair_live,
            max_iterations=3
        )
        
        if show_preview and result.get("diff"):
            print("\n" + "="*60)
            print("BEFORE:")
            print("="*60)
            print(result["diff"]["before"])
            print("\n" + "="*60)
            print("AFTER:")
            print("="*60)
            print(result["diff"]["after"])
        
        print("\n" + "="*60)
        print("RESULT:")
        print("="*60)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(judge_result, indent=2))


if __name__ == "__main__":
    main()
