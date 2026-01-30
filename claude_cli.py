#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from typing import List

from gatekeeper.engine import run_gatekeeper


EXCLUDED_DIRS = {".git", ".venv", "__pycache__"}


def collect_files(root: Path) -> List[Path]:
    files: List[Path] = []

    for path in root.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path)

    return sorted(files)


def gate_file(path: Path, profile: str) -> dict:
    with open(path, "r") as f:
        code = f.read()

    return run_gatekeeper(
        code=code,
        filename=str(path),
        profile=profile,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--profile", default="strict")

    args = parser.parse_args()

    target = Path(args.path)

    if target.is_file():
        result = gate_file(target, args.profile)
        print(result)
        sys.exit(0 if result["compliant"] else 1)

    if target.is_dir():
        failures = []

        files = collect_files(target)

        if not files:
            print({"compliant": True, "files_checked": 0})
            sys.exit(0)

        for file in files:
            result = gate_file(file, args.profile)
            if not result["compliant"]:
                failures.append(
                    {
                        "file": str(file),
                        "failures": result["failures"],
                    }
                )
                break  # strict mode = fail fast

        if failures:
            output = {
                "compliant": False,
                "files_checked": len(files),
                "failures": failures,
                "profile": args.profile,
            }
            print(output)
            sys.exit(1)

        print(
            {
                "compliant": True,
                "files_checked": len(files),
                "profile": args.profile,
            }
        )
        sys.exit(0)

    raise RuntimeError(f"Invalid path: {target}")


if __name__ == "__main__":
    main()
