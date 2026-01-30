import subprocess
import sys
import tempfile
import os


def test_gate_fails_on_forbidden_path():
    with tempfile.TemporaryDirectory() as tmp:
        secrets_dir = os.path.join(tmp, "secrets")
        os.makedirs(secrets_dir)

        bad_file = os.path.join(secrets_dir, "config.py")
        with open(bad_file, "w") as f:
            f.write("password = 'oops'\n")

        result = subprocess.run(
            [sys.executable, "claude_cli.py", tmp, "--gate"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert '"gate_pass": false' in result.stdout.lower()
        assert '"violations": 1' in result.stdout.lower()
