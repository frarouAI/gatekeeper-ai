"""
Batch Processor — Gatekeeper AI

Processes multiple Python files safely.
- Judge-only by default
- Repair is optional
- CI-safe (never hangs, never prompts)
"""

from pathlib import Path
from typing import List, Dict

from judge import judge_code
from loop_controller import run_loop


MAX_FILES = 200  # safety limit


def find_python_files(path: str) -> List[Path]:
    p = Path(path)

    if p.is_file() and p.suffix == ".py":
        return [p]

    if p.is_dir():
        return list(p.rglob("*.py"))

    return []


def process_batch(
    paths: List[str],
    profile: str = "strict",
    enable_repair: bool = False,
    apply_repairs: bool = False,
    ci_mode: bool = False,
) -> Dict:
    """
    Batch-process Python files.

    Returns a CI-friendly summary object.
    """

    files: List[Path] = []

    for path in paths:
        files.extend(find_python_files(path))

    files = list(set(files))  # de-dup

    if len(files) > MAX_FILES:
        return {
            "error": "too_many_files",
            "file_count": len(files),
            "limit": MAX_FILES,
            "ci_pass": False,
        }

    summary = {
        "total_files": len(files),
        "compliant_files": 0,
        "non_compliant_files": 0,
        "files_repaired": 0,
        "total_failures": 0,
        "files": [],
        "ci_pass": True,
    }

    for file_path in files:
        code = file_path.read_text()

        judge_result = judge_code(code, profile)

        file_report = {
            "filepath": str(file_path),
            "judge": judge_result,
        }

        if judge_result.get("compliant", True):
            summary["compliant_files"] += 1
        else:
            summary["non_compliant_files"] += 1
            summary["total_failures"] += judge_result.get("failure_count", 0)
            summary["ci_pass"] = False

            if enable_repair:
                repair_result = run_loop(
                    filepath=str(file_path),
                    judge_result=judge_result,
                    profile=profile,
                    enable_repair=False,  # dry-run only
                    dry_run=True,
                )
                file_report["repair"] = repair_result

        summary["files"].append(file_report)

    return summary
