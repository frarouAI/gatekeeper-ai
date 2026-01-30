"""
Gatekeeper Baseline Engine

Responsible for:
- Loading baseline
- Writing baseline
- Comparing quality regressions
"""

import json
from pathlib import Path
from typing import Dict

BASELINE_PATH = Path(".gatekeeper/baseline.json")


def load_baseline() -> Dict | None:
    """Load baseline if it exists."""
    if not BASELINE_PATH.exists():
        return None
    return json.loads(BASELINE_PATH.read_text())


def write_baseline(summary: Dict):
    """Persist baseline from CI summary."""
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)

    baseline = {
        "schema_version": "baseline-v1",
        "team_quality_score": summary["team_quality_score"],
        "files_checked": summary["files_checked"],
        "total_failures": summary["total_failures"],
        "timestamp": summary["timestamp"],
    }

    BASELINE_PATH.write_text(json.dumps(baseline, indent=2))


def compare_to_baseline(
    current_score: float,
    baseline: Dict,
    max_drop: float = 0.0
) -> Dict:
    """
    Compare current score to baseline.

    max_drop: allowed regression (e.g. 0.05 = -5%)
    """
    baseline_score = baseline["team_quality_score"]
    delta = current_score - baseline_score

    regressed = delta < -max_drop

    return {
        "baseline_score": baseline_score,
        "current_score": current_score,
        "delta": round(delta, 4),
        "regressed": regressed,
    }
