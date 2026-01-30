from pathlib import Path
import hashlib

from autofix_header import HEADER, HEADER_RULE_ID, has_header as _has_header


FORBIDDEN_DIRS = {"secrets"}


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _contains_forbidden_path(path: Path) -> bool:
    return any(part in FORBIDDEN_DIRS for part in path.parts)


def _scan_directory(path: Path, profile: str):
    violations = 0
    failures = []

    for file in path.rglob("*"):
        if not file.is_file():
            continue

        # 🚫 Forbidden path rule
        if _contains_forbidden_path(file):
            failures.append({
                "rule": "FORBIDDEN_PATH",
                "path": str(file),
                "severity": "fail",
            })
            violations += 1
            continue

        try:
            content = file.read_text()
        except Exception:
            continue

        # Large file rule
        if content.count("\n") > 500:
            failures.append({
                "rule": "FILE_TOO_LARGE",
                "path": str(file),
                "severity": "warning",
            })
            if profile == "strict":
                violations += 1

    return violations, failures


def judge_code(
    path: Path,
    *,
    profile: str = "strict",
    repair_live: bool = False,
    repair_dry_run: bool = False,
):
    path = Path(path)

    violations = 0
    failures = []
    autofix_applied = False
    audit = None
    rule_id = None
    files_modified = []

    # =========================
    # FORBIDDEN PATH (early exit)
    # =========================
    if _contains_forbidden_path(path):
        failures.append({
            "rule": "FORBIDDEN_PATH",
            "path": str(path),
            "severity": "fail",
        })
        return {
            "compliant": False,
            "violations": 1,
            "failure_count": 1,
            "failures": failures,
            "autofix_applied": False,
            "audit": None,
            "rule_id": None,
            "files_modified": [],
        }

    # =========================
    # DIRECTORY TARGET
    # =========================
    if path.is_dir():
        violations, failures = _scan_directory(path, profile)

        return {
            "compliant": violations == 0,
            "violations": violations,
            "failure_count": violations,
            "failures": failures,
            "autofix_applied": False,
            "audit": None,
            "rule_id": None,
            "files_modified": [],
        }

    # =========================
    # FILE TARGET
    # =========================
    content = path.read_text()

    # Large file rule
    if content.count("\n") > 500:
        failures.append({
            "rule": "FILE_TOO_LARGE",
            "path": str(path),
            "severity": "warning",
        })
        if profile == "strict":
            violations += 1

    # =========================
    # Phase 5B — Safe auto-fix
    # =========================
    if (
        profile == "strict"
        and repair_live
        and path.suffix == ".py"
        and not _has_header(content)
        and violations == 0
    ):
        before_hash = _hash(content)
        new_content = HEADER + content
        after_hash = _hash(new_content)

        audit = {
            "rule_id": HEADER_RULE_ID,
            "file": str(path),
            "before_hash": before_hash,
            "after_hash": after_hash,
            "mode": "dry-run" if repair_dry_run else "live",
            "patch": HEADER,
        }

        rule_id = HEADER_RULE_ID

        if not repair_dry_run:
            path.write_text(new_content)
            autofix_applied = True
            files_modified.append(str(path))

    return {
        "compliant": violations == 0,
        "violations": violations,
        "failure_count": violations,
        "failures": failures,
        "autofix_applied": autofix_applied,
        "audit": audit,
        "rule_id": rule_id,
        "files_modified": files_modified,
    }
