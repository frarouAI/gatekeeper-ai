import sys
from pathlib import Path
from gatekeeper.engine import scan
from gatekeeper.version import __version__

def main():
    if "--version" in sys.argv:
        print(__version__)
        return 0

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    violations = scan(root)

    if violations:
        print("✖ Gatekeeper failed\n")
        print("Forbidden paths detected:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)

    print("✔ Gatekeeper passed")
    return 0
