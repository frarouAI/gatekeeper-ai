#!/usr/bin/env python3
"""Repair loop."""
from pathlib import Path
code = Path('submissions/broken.py').read_text()
print("Failed code:", code)
print("Claude: Rewrite safe version → paste fixed code")
