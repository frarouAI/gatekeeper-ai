#!/usr/bin/env python3
"""
Claude Code Judge CLI

Usage:
    python3 claude_cli.py <file> [options]

Options:
    --profile <strict|balanced|permissive>  Quality profile (default: strict)
    --repair-dry-run                        Generate repair proposals (no file changes)
    --preview                               Show detailed preview of changes
    --apply                                 Apply repairs to file (creates backup)
    --no-backup                             Don't create backup when applying
"""

import sys
import json
from pathlib import Path

from judge import judge_code
from loop_controller import run_loop
from repair_schema import display_preview, apply_patches_to_file


def main():
    # Parse arguments
    args = sys.argv[1:]
    
    if not args or '--help' in args:
        print(__doc__)
        sys.exit(0)
    
    filepath = args[0]
    profile = "strict"
    repair_dry_run = False
    show_preview = False
    apply_repairs = False
    create_backup = True
    
    # Parse flags
    i = 1
    while i < len(args):
        arg = args[i]
        if arg == "--profile" and i + 1 < len(args):
            profile = args[i + 1]
            i += 2
        elif arg.startswith("--profile="):
            profile = arg.split("=")[1]
            i += 1
        elif arg == "--repair-dry-run":
            repair_dry_run = True
            i += 1
        elif arg == "--preview":
            show_preview = True
            repair_dry_run = True  # Preview requires repair proposals
            i += 1
        elif arg == "--apply":
            apply_repairs = True
            repair_dry_run = True  # Must generate proposals first
            i += 1
        elif arg == "--no-backup":
            create_backup = False
            i += 1
        else:
            i += 1
    
    # Validate file exists
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    # Read code
    with open(filepath, 'r') as f:
        code = f.read()
    
    # Step 1: Judge the code
    judge_result = judge_code(code, profile)
    
    # Step 2: If repair mode, run loop controller
    if repair_dry_run:
        result = run_loop(
            filepath=filepath,
            judge_result=judge_result,
            profile=profile,
            enable_repair=True,
            dry_run=True,
            max_iterations=3
        )
        
        # Step 3: Show preview if requested
        if show_preview and result.get("repairs_proposed"):
            display_preview(code, result["repairs_proposed"])
        
        # Step 4: Apply if requested
        if apply_repairs and result.get("repairs_proposed"):
            # Ask for confirmation
            print("\n⚠️  WARNING: This will modify the file!")
            if create_backup:
                print(f"   Backup will be created: {filepath}.bak")
            
            response = input("\nProceed with repair? [y/N]: ")
            
            if response.lower() == 'y':
                apply_result = apply_patches_to_file(
                    filepath,
                    result["repairs_proposed"],
                    dry_run=False,
                    create_backup=create_backup
                )
                result["apply_result"] = apply_result
                print(f"\n✅ Repairs applied successfully!")
                print(f"   Patches applied: {apply_result['patches_applied']}")
                if apply_result['backup_created']:
                    print(f"   Backup saved: {apply_result['backup_path']}")
            else:
                print("\n❌ Repair cancelled by user.")
                result["apply_result"] = {"status": "cancelled"}
        
        # Output JSON result
        print("\n" + "="*60)
        print("FULL RESULT (JSON):")
        print("="*60)
        print(json.dumps(result, indent=2))
    else:
        # Just return judge result
        print(json.dumps(judge_result, indent=2))


if __name__ == "__main__":
    main()
