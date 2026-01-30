import subprocess
import sys


def test_gate_pass():
    result = subprocess.run(
        [sys.executable, "claude_cli.py", "test_pass.py", "--gate"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"gate_pass": true' in result.stdout.lower()
