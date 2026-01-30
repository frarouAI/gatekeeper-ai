import subprocess
import sys
import tempfile
import os


def test_repair_loop_stops():
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
        assert '"iteration": 0' in result.stdout
