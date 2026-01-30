"""
Gatekeeper History Engine

Maintains an append-only timeline of repo quality.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List

HISTORY_PATH = Path(".gatekeeper/history.json")


def load_history() -> List[Dict]:
    """Load full history timeline."""
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text())


def append_history(entry: Dict):
    """Append a new immutable history entry."""
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    history = load_history()
    history.append(entry)

    HISTORY_PATH.write_text(json.dumps(history, indent=2))


def build_history_entry(
    *,
    current_score: float,
    baseline_score: float,
    delta: float,
    ci_pass: bool,
    blocking_files: int,
) -> Dict:
    """Create a normalized history entry."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "team_quality_score": round(current_score, 4),
        "baseline_score": round(baseline_score, 4),
        "delta": round(delta, 4),
        "ci_pass": ci_pass,
        "blocking_files": blocking_files,
    }
