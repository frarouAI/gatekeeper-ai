import subprocess
import sys
import tempfile
import os
import json


def test_repair_is_inert_and_audited():
    with tempfile.TemporaryDirectory() as tmp:
        secrets = os.path.join(tmp, "secrets")
        os.makedirs(secrets)

        bad = os.path.join(secrets, "config.py")
        with open(bad, "w") as f:
            f.write("password = 'oops'\n")

        before = open(bad).read()

        result = subprocess.run(
            [sys.executable, "claude_cli.py", tmp, "--gate", "--repair"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1

        after = open(bad).read()
        assert before == after  # no mutation

        audit1 = os.path.join(tmp, ".gatekeeper", "repair_audit.jsonl")
        audit2 = ".gatekeeper/repair_audit.jsonl"
        audit = audit1 if os.path.exists(audit1) else audit2

        assert os.path.exists(audit)

        with open(audit) as f:
            lines = f.readlines()

        assert len(lines) >= 1
        entry = json.loads(lines[0])
        assert "iteration" in entry
        assert "repairs" in entry
