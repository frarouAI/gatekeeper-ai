"""
Baseline Manager — Quality Baseline Tracking
"""

import json
from pathlib import Path
from typing import Dict, Optional
from artifact_signer import attach_signature


BASELINE_FILE = Path(".gatekeeper/baseline.json")


def load_baseline() -> Optional[Dict]:
    """Load existing baseline."""
    if not BASELINE_FILE.exists():
        return None
    return json.loads(BASELINE_FILE.read_text())


def write_baseline(summary: Dict) -> Path:
    """Write and sign new baseline."""
    
    baseline = {
        "schema_version": "baseline-v1",
        "team_quality_score": summary["team_quality_score"],
        "total_failures": summary["total_failures"],
        "files_checked": summary["files_checked"],
        "timestamp": summary["timestamp"]
    }
    
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(json.dumps(baseline, indent=2))
    
    # 🔐 SIGN IT
    attach_signature(BASELINE_FILE)
    
    return BASELINE_FILE


def compare_to_baseline(current_score: float, baseline: Dict, max_drop: float = 0.0) -> Dict:
    """Compare current score to baseline."""
    
    baseline_score = baseline["team_quality_score"]
    delta = current_score - baseline_score
    
    regressed = delta < -max_drop if max_drop > 0 else current_score < baseline_score
    
    return {
        "current": current_score,
        "baseline": baseline_score,
        "delta": delta,
        "regressed": regressed
    }
