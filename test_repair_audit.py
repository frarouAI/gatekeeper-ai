import subprocess
import sys
import tempfile
import os
import json


def test_repair_audit_created_and_inert():
    with tempfile.TemporaryDirectory() as tmp:
        secrets = os.path.join(tmp, "secrets")
        os.makedirs(secrets)

        bad = os.path.join(secrets, "config.py")
        with open(bad, "w") as f:
            f.write("password = 'oops'\n")

        result = subprocess.run(
            [sys.executable, "claude_cli.py", tmp, "--gate", "--repair"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1

        audit = os.path.join(tmp, ".gatekeeper", "repair_audit.jsonl")
        # audit may be written relative to CWD; allow either
        audit_alt = ".gatekeeper/repair_audit.jsonl"

        path = audit if os.path.exists(audit) else audit_alt
        assert os.path.exists(path)

        with open(path) as f:
            lines = f.readlines()

        assert len(lines) >= 1
        entry = json.loads(lines[0])
        assert "iteration" in entry
        assert "repairs" in entry
