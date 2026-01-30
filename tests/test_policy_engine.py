import pytest

from policy_engine import (
    Finding,
    apply_policy_engine,
)


# ----------------------------
# Helpers
# ----------------------------

def make_finding(
    *,
    fid="f1",
    path="src/main.py",
    signal="ok",
    line_count=10,
):
    return Finding(
        id=fid,
        type="file",
        path=path,
        signal=signal,
        metadata={"line_count": line_count},
    )


# ----------------------------
# Tests
# ----------------------------

def test_empty_findings_produces_summary_only():
    result = apply_policy_engine([])

    summary = result["policy_summary"]
    judgements = result["judgements"]

    assert summary.checked_rules == 3
    assert summary.violations == 0
    assert summary.warnings == 0
    assert summary.passes == 3
    assert judgements == []


def test_forbidden_path_fails():
    finding = make_finding(path="/secrets/config.py")

    result = apply_policy_engine([finding])
    judgements = result["judgements"]

    assert len(judgements) == 1
    j = judgements[0]

    assert j.rule_id == "FORBIDDEN_PATH"
    assert j.status == "fail"
    assert j.confidence == 0.98
    assert "forbidden" in j.reason.lower()


def test_missing_metadata_warns():
    finding = make_finding(signal="missing_metadata")

    result = apply_policy_engine([finding])
    judgements = result["judgements"]

    assert len(judgements) == 1
    j = judgements[0]

    assert j.rule_id == "REQUIRED_METADATA_MISSING"
    assert j.status == "warn"
    assert j.confidence == 0.85


def test_oversized_file_warns():
    finding = make_finding(line_count=999)

    result = apply_policy_engine([finding])
    judgements = result["judgements"]

    assert len(judgements) == 1
    j = judgements[0]

    assert j.rule_id == "FILE_TOO_LARGE"
    assert j.status == "warn"
    assert j.confidence == 0.75


def test_multiple_rules_apply_to_single_finding():
    finding = make_finding(
        path="/private/huge.py",
        signal="missing_metadata",
        line_count=1000,
    )

    result = apply_policy_engine([finding])
    judgements = result["judgements"]

    rule_ids = {j.rule_id for j in judgements}

    assert rule_ids == {
        "FORBIDDEN_PATH",
        "REQUIRED_METADATA_MISSING",
        "FILE_TOO_LARGE",
    }


def test_summary_counts_failures_and_warnings():
    finding = make_finding(
        path="/private/big.py",
        signal="missing_metadata",
        line_count=1000,
    )

    result = apply_policy_engine([finding])
    summary = result["policy_summary"]

    assert summary.checked_rules == 3
    assert summary.violations == 1
    assert summary.warnings == 2
    assert summary.passes == 0
