from gatekeeper.explain import explain_verdict


class WarningFailure:
    kind = "warning"
    rule_id = "STYLE_WARNING"
    files = ["src/main.py"]
    message = "style warning"


class Verdict:
    compliant = False
    profile = "strict"
    failures = [WarningFailure()]


def test_strict_profile_escalates_warning():
    explanation = explain_verdict(Verdict())

    assert explanation.kind == "strict_escalation"
    assert explanation.autofix_attempted is False
    assert explanation.autofix_blocked_reason == "strict profile escalation"
    assert "warnings are treated as errors" in explanation.summary
    assert explanation.rule_ids == ["STYLE_WARNING"]
    assert explanation.files == ["src/main.py"]
