import sys
import argparse

from gatekeeper.version import __version__
from gatekeeper.explain import explain_verdict
from gatekeeper.cli.render import render_explanation
from gatekeeper.config.loader import load_config, ConfigError
from gatekeeper.engine import run


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="gatekeeper",
        description="Deterministic code governance and enforcement",
    )
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--version", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0

    try:
        config = load_config(args.path)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 2  # distinct exit for config problems

    verdict = run(path=args.path, config=config)

    if verdict.compliant:
        return 0

    explanation = explain_verdict(verdict)
    print(render_explanation(explanation))
    return 1


if __name__ == "__main__":
    sys.exit(main())
