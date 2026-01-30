import subprocess
import sys
import tempfile
import os


def test_strict_profile_fails_on_warning():
    with tempfile.TemporaryDirectory() as tmp:
        secrets = os.path.join(tmp, "secrets")
        os.makedirs(secrets)

        big = os.path.join(secrets, "big.py")
        with open(big, "w") as f:
            f.write("x\n" * 600)

        result = subprocess.run(
            [sys.executable, "claude_cli.py", tmp, "--gate"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert '"profile": "strict"' in result.stdout
