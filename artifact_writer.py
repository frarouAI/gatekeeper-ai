"""
Artifact Writer
Responsible for persisting CI and gatekeeper artifacts in a stable layout.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


ARTIFACT_ROOT = Path(".gatekeeper/artifacts")


def _ensure_root() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)


def save_ci_summary(result: dict) -> None:
    """
    Persist the CI summary result to disk.

    This is the canonical artifact consumed by:
    - HTML report
    - UI dashboards
    - Future audit / billing systems
    """
    _ensure_root()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = ARTIFACT_ROOT / f"ci_summary_{timestamp}.json"

    with path.open("w") as f:
        json.dump(result, f, indent=2)

    # Optional convenience pointer (latest)
    latest = ARTIFACT_ROOT / "ci_summary_latest.json"
    latest.write_text(path.read_text())
