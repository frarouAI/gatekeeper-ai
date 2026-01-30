import subprocess
import sys
import tempfile
import os


def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def test_gate_uses_git_diff_only():
    with tempfile.TemporaryDirectory() as tmp:
        run(["git", "init"], tmp)

        # clean file
        good = os.path.join(tmp, "good.py")
        with open(good, "w") as f:
            f.write("print('ok')\n")

        run(["git", "add", "good.py"], tmp)
        run(["git", "commit", "-m", "initial"], tmp)

        # forbidden change
        secrets = os.path.join(tmp, "secrets")
        os.makedirs(secrets)
        bad = os.path.join(secrets, "config.py")
        with open(bad, "w") as f:
            f.write("password = 'oops'\n")

        cli = os.path.abspath("claude_cli.py")

        result = subprocess.run(
            [sys.executable, cli, tmp, "--gate"],
            cwd=tmp,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert '"gate_pass": false' in result.stdout.lower()
