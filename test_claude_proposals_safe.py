import tempfile
import os
import sys
import subprocess


def test_claude_proposals_are_safe():
    with tempfile.TemporaryDirectory() as tmp:
        secrets = os.path.join(tmp, "secrets")
        os.makedirs(secrets)

        bad = os.path.join(secrets, "config.py")
        with open(bad, "w") as f:
            f.write("password = 'oops'\n")

        before = open(bad).read()

        result = subprocess.run(
            [sys.executable, "claude_cli.py", tmp, "--gate", "--repair", "--propose"],
            capture_output=True,
            text=True,
        )

        after = open(bad).read()

        assert result.returncode == 1
        assert before == after  # Claude cannot mutate files
