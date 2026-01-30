from gatekeeper.explain import explain_verdict


class FakeFailure:
    def __init__(self):
        self.kind = "forbidden_path"
        self.rule_id = "FORBIDDEN_PATH"
        self.files = ["secrets/api_key.py"]
        self.message = "forbidden path touched"


class FakeVerdict:
    compliant = False
    profile = "strict"
    failures = [FakeFailure()]


def test_forbidden_path_explanation_blocks_autofix():
    verdict = FakeVerdict()
    explanation = explain_verdict(verdict)

    assert explanation.kind == "forbidden_path"
    assert explanation.autofix_attempted is False
    assert explanation.autofix_blocked_reason is not None
    assert "Forbidden paths" in explanation.summary
