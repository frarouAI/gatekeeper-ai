import subprocess, json
def test_gate_pass():
    with open('test_pass.py', 'w') as f:
        f.write('def good(): return True')
    result = subprocess.run(['python3', 'claude_cli.py', 'test_pass.py', '--gate'], capture_output=True, text=True)
    assert '"gate_pass": true' in result.stdout
test_gate_pass()
