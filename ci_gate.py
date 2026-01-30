#!/usr/bin/env python3
"""
Gatekeeper CI entrypoint.

Responsibilities:
- Load validated config
- Collect files
- Run judge (LIVE or OFFLINE)
- Persist artifacts
- Print human-grade UX
- Exit with correct semantics
"""

import os
import sys
from pathlib import Path

from gatekeeper_config import load_config
from multi_judge import MultiAgentCodeJudge
from artifact_writer import save_ci_summary
from utils import print_header


# --------------------------------------------------
# Exit helpers
# --------------------------------------------------
def exit_ok():
    sys.exit(0)


def exit_block():
    sys.exit(1)


def exit_error():
    sys.exit(2)


# --------------------------------------------------
# File collection
# --------------------------------------------------
def collect_files(include_paths: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}

    for pattern in include_paths:
        for path in Path(".").glob(pattern):
            if path.is_file():
                try:
                    files[str(path)] = path.read_text()
                except Exception:
                    pass

    return files


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    print_header("GATEKEEPER CI")

    mode = os.environ.get("GATEKEEPER_MODE", "offline")
    print(f"Requested mode:  {mode}")

    # --------------------------------------------------
    # Load config
    # --------------------------------------------------
    try:
        config = load_config(".gatekeeper.yml")
    except Exception as exc:
        print("\n❌ Config error:")
        print(f"   {exc}")
        exit_error()

    include_paths = config.paths.include

    if not include_paths:
        print("⚠️  No files to check")
        exit_ok()

    files = collect_files(include_paths)

    if not files:
        print("⚠️  No matching files found")
        exit_ok()

    # --------------------------------------------------
    # Initialize judge
    # --------------------------------------------------
    judge = MultiAgentCodeJudge(
        model=config.runtime.model,
        profile=config.profile,
        max_tokens=config.runtime.max_tokens,
        temperature=config.runtime.temperature,
        timeout=config.runtime.timeout,
        cost_limit_usd=config.runtime.cost_limit_usd,
    )

    # --------------------------------------------------
    # Run judge
    # --------------------------------------------------
    try:
        result = judge.judge_repo(files)
    except Exception as exc:
        print("\n❌ Internal error during CI execution")
        print(f"   {type(exc).__name__}: {exc}")
        exit_error()

    # --------------------------------------------------
    # Persist artifacts
    # --------------------------------------------------
    save_ci_summary(result)

    # --------------------------------------------------
    # UX Output
    # --------------------------------------------------
    print_header("RESULT SUMMARY")

    print(f"Files processed: {result['files_processed']} / {result['files_total']}")
    print(f"Average score:   {result['average_score']:.2f}")
    print(f"Threshold:       {result['threshold']:.2f}")

    print("\n💰 Cost Summary")
    cost = result["cost_summary"]
    print(f"Input tokens:    {cost['input_tokens']}")
    print(f"Output tokens:   {cost['output_tokens']}")
    print(f"Estimated cost:  ${cost['estimated_cost_usd']:.4f}")

    if result["cost_limit_hit"]:
        print("\n⚠️  Cost limit approached — partial results returned")
        print("   CI PASSED (budget safety enforced)")
        exit_ok()

    if not result["gate_pass"]:
        print("\n❌ QUALITY CHECK FAILED")
        for f in result.get("non_compliant_files", []):
            print(f"  • {f}")
        exit_block()

    print("\n✅ CI PASSED — Quality enforced")
    exit_ok()


if __name__ == "__main__":
    main()
