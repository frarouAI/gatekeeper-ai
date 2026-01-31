import sys
from gatekeeper.version import __version__
from gatekeeper.engine import run

def main() -> None:
    if "--version" in sys.argv:
        print(__version__)
        return

    sys.exit(run())
