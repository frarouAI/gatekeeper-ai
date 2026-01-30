from dataclasses import dataclass
from typing import List, Dict, Optional
import os

from profiles import resolve_profile


# ----------------------------
# Data contracts
# ----------------------------

@dataclass(frozen=True)
class Finding:
    id: str
    type: str
    path: str
    signal: str
    metadata: Dict


@dataclass(frozen=True)
class PolicyJudgement:
    finding_id: str
    rule_id: str
    status: str          # pass | warn | fail
    confidence: float
    reason: str
    suggested_fix: Optional[str] = None


@dataclass
class PolicySummary:
    checked_rules: int
    violations: int
    warnings: int
    passes: int
    profile: str


# ----------------------------
# Policy rules (UNCHANGED)
# ----------------------------

FORBIDDEN_PATHS = ("secrets", "private", ".env")
MAX_LINE_COUNT = 500


def _normalized_path(path: str) -> str:
    norm = os.path.normpath(path)
    return "/".join(norm.split(os.sep))


def rule_forbidden_path(finding: Finding) -> Optional[PolicyJudgement]:
    norm_path = _normalized_path(finding.path)
    if any(f"/{p}/" in f"/{norm_path}/" for p in FORBIDDEN_PATHS):
        return PolicyJudgement(
            finding_id=finding.id,
            rule_id="FORBIDDEN_PATH",
            status="fail",
            confidence=0.98,
            reason="Files may not reside in forbidden or sensitive directories.",
        )
    return None


def rule_missing_metadata(finding: Finding) -> Optional[PolicyJudgement]:
    if finding.signal == "missing_metadata":
        return PolicyJudgement(
            finding_id=finding.id,
            rule_id="REQUIRED_METADATA_MISSING",
            status="warn",
            confidence=0.85,
            reason="Required metadata is missing from this file.",
        )
    return None


def rule_file_too_large(finding: Finding) -> Optional[PolicyJudgement]:
    line_count = finding.metadata.get("line_count")
    if isinstance(line_count, int) and line_count > MAX_LINE_COUNT:
        return PolicyJudgement(
            finding_id=finding.id,
            rule_id="FILE_TOO_LARGE",
            status="warn",
            confidence=0.75,
            reason="File exceeds the recommended maximum line count.",
        )
    return None


POLICY_RULES = [
    rule_forbidden_path,
    rule_missing_metadata,
    rule_file_too_large,
]


# ----------------------------
# Policy engine (profile-aware aggregation ONLY)
# ----------------------------

def apply_policy_engine(findings: List[Finding]) -> Dict:
    judgements: List[PolicyJudgement] = []

    for finding in findings:
        for rule in POLICY_RULES:
            judgement = rule(finding)
            if judgement:
                judgements.append(judgement)

    violations = 0
    warnings = 0

    for j in judgements:
        profile = resolve_profile(j.finding_id)
        if j.status == "fail":
            violations += 1
        elif j.status == "warn":
            warnings += 1
            if profile.fail_on_warnings:
                violations += 1

    profile_name = (
        resolve_profile(findings[0].path).name if findings else "default"
    )

    summary = PolicySummary(
        checked_rules=len(POLICY_RULES),
        violations=violations,
        warnings=warnings,
        passes=len(POLICY_RULES) - violations - warnings,
        profile=profile_name,
    )

    return {
        "policy_summary": summary,
        "judgements": judgements,
    }
