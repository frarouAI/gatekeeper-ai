import pytest
from pathlib import Path
from tests.helpers import run_gatekeeper


EXPECTED_HEADER = (
    "# Gatekeeper: Managed File\n"
    "# Owner: unknown\n"
    "# Policy: strict\n\n"
)


def test_autofix_inserts_header_when_missing_strict(tmp_path):
    file = tmp_path / "example.py"
    file.write_text("print('hello')\n")

    result = run_gatekeeper(
        path=file,
        profile="strict",
        repair_live=True,
    )

    content = file.read_text()

    assert content.startswith(EXPECTED_HEADER)
    assert result is not None
    assert result.get("autofix_applied") is True
    assert result.get("rule_id") == "missing_required_header"


def test_autofix_skips_when_header_exists(tmp_path):
    file = tmp_path / "example.py"
    file.write_text(EXPECTED_HEADER + "print('hello')\n")

    result = run_gatekeeper(
        path=file,
        profile="strict",
        repair_live=True,
    )

    content = file.read_text()

    assert content.count("Gatekeeper: Managed File") == 1
    assert result.get("autofix_applied") is False


@pytest.mark.parametrize("profile", ["startup", "relaxed"])
def test_autofix_never_runs_outside_strict(tmp_path, profile):
    file = tmp_path / "example.py"
    file.write_text("print('hello')\n")

    result = run_gatekeeper(
        path=file,
        profile=profile,
        repair_live=True,
    )

    content = file.read_text()

    assert "Gatekeeper: Managed File" not in content
    assert result.get("autofix_applied") is False


def test_autofix_dry_run_never_mutates(tmp_path):
    file = tmp_path / "example.py"
    original = "print('hello')\n"
    file.write_text(original)

    result = run_gatekeeper(
        path=file,
        profile="strict",
        repair_dry_run=True,
    )

    assert file.read_text() == original
    assert result.get("autofix_applied") is False


def test_autofix_modifies_only_one_file(tmp_path):
    a = tmp_path / "a.py"
    b = tmp_path / "b.py"

    a.write_text("print('a')\n")
    b.write_text("print('b')\n")

    result = run_gatekeeper(
        path=tmp_path,
        profile="strict",
        repair_live=True,
    )

    modified = result.get("files_modified", [])
    assert isinstance(modified, list)
    assert len(modified) <= 1


def test_autofix_creates_audit_artifact(tmp_path):
    file = tmp_path / "example.py"
    file.write_text("print('hello')\n")

    result = run_gatekeeper(
        path=file,
        profile="strict",
        repair_live=True,
    )

    audit = result.get("audit")

    assert audit is not None
    assert audit.get("rule_id") == "missing_required_header"
    assert audit.get("file") == str(file)
    assert audit.get("before_hash") != audit.get("after_hash")
    assert "patch" in audit
