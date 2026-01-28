#!/usr/bin/env python3
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from claude_cli import main as cli_main
    cli_main()
except:
    subprocess.run([sys.executable, 'claude_cli.py'] + sys.argv[1:])
