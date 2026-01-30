from gatekeeper.explain import explain_verdict


class ForbiddenFailure:
    kind = "forbidden_path"
    rule_id = "FORBIDDEN_PATH"
    files = ["secrets/token.py"]
    message = "forbidden"


class WarningFailure:
    kind = "warning"
    rule_id = "STYLE_WARNING"
    files = ["src/app.py"]
    message = "warning"


class Verdict:
    compliant = False
    profile = "strict"
    failures = [ForbiddenFailure(), WarningFailure()]


def test_forbidden_path_dominates_narrative():
    explanation = explain_verdict(Verdict())

    assert explanation.kind == "forbidden_path"
    assert "Forbidden paths" in explanation.summary
    assert explanation.autofix_attempted is False

    # Critical: warning must NOT leak into explanation
    assert explanation.rule_ids == ["FORBIDDEN_PATH"]
    assert explanation.files == ["secrets/token.py"]
