from gatekeeper.explain import explain_verdict


class StructuralFailure:
    kind = "structural"
    rule_id = "FORMAT_ERROR"
    files = ["src/utils.py"]
    message = "formatting issue"


class Verdict:
    compliant = False
    profile = "default"
    failures = [StructuralFailure()]


def test_fixable_structural_failure_explained():
    explanation = explain_verdict(Verdict())

    assert explanation.kind == "fixable_failure"
    assert explanation.autofix_attempted is False
    assert explanation.autofix_blocked_reason is None
    assert "fixable structural issues" in explanation.summary
    assert explanation.rule_ids == ["FORMAT_ERROR"]
    assert explanation.files == ["src/utils.py"]
