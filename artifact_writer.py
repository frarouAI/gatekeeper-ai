"""
Artifact Writer — Immutable Repair Evidence

Writes repair artifacts for auditing, CI, and enterprise compliance.
Every repair produces a timestamped, validated, immutable JSON artifact.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List
from schema_validator import validate_artifact_schema


ARTIFACT_DIR = Path(".gatekeeper/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def write_repair_artifact(
    filepath: str,
    profile: str,
    mode: str,
    initial_failures: List[str],
    final_failures: List[str],
    iterations_used: int,
    repair_confidence: float,
    history: List[Dict],
    diff_before: str,
    diff_after: str,
    improved: bool
) -> Path:
    """
    Write an immutable, schema-validated repair artifact.
    
    Fails closed if schema validation fails.
    """
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Create safe filename from filepath
    safe_name = filepath.replace("/", "_").replace("\\", "_")
    timestamp_short = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    artifact_filename = f"{timestamp_short}_{safe_name}.json"
    artifact_path = ARTIFACT_DIR / artifact_filename
    
    # Build artifact
    artifact = {
        "schema_version": "gatekeeper-artifact-v1.0",
        "timestamp": timestamp,
        "filepath": filepath,
        "mode": mode,
        "profile": profile,
        "summary": {
            "initial_failure_count": len(initial_failures),
            "final_failure_count": len(final_failures),
            "iterations_used": iterations_used,
            "repair_confidence": repair_confidence,
            "improved": improved,
            "fully_repaired": len(final_failures) == 0
        },
        "failures": {
            "initial": initial_failures,
            "final": final_failures
        },
        "iterations": history,
        "diff": {
            "before": diff_before,
            "after": diff_after
        },
        "metadata": {
            "gatekeeper_version": "1.0.0",
            "created_at": timestamp
        }
    }
    
    # CRITICAL: Validate before writing
    validate_artifact_schema(artifact)
    
    # Write atomically
    artifact_path.write_text(json.dumps(artifact, indent=2))
    
    return artifact_path


def get_latest_artifacts(limit: int = 10) -> List[Path]:
    """Get most recent artifacts."""
    artifacts = sorted(ARTIFACT_DIR.glob("*.json"), reverse=True)
    return artifacts[:limit]


def load_artifact(artifact_path: Path) -> Dict:
    """Load and validate artifact from disk."""
    artifact = json.loads(artifact_path.read_text())
    validate_artifact_schema(artifact)  # Validate on load too
    return artifact


def generate_artifact_summary() -> Dict:
    """Generate summary statistics from all artifacts."""
    artifacts = list(ARTIFACT_DIR.glob("*.json"))
    
    if not artifacts:
        return {
            "total_repairs": 0,
            "success_rate": 0.0,
            "avg_confidence": 0.0,
            "avg_iterations": 0.0
        }
    
    total = len(artifacts)
    successful = 0
    total_confidence = 0.0
    total_iterations = 0
    
    for artifact_path in artifacts:
        try:
            artifact = load_artifact(artifact_path)
            summary = artifact.get("summary", {})
            
            if summary.get("fully_repaired", False):
                successful += 1
            
            total_confidence += summary.get("repair_confidence", 0.0)
            total_iterations += summary.get("iterations_used", 0)
        except Exception as e:
            print(f"WARNING: Could not load {artifact_path}: {e}")
            continue
    
    return {
        "total_repairs": total,
        "successful_repairs": successful,
        "success_rate": round(successful / total, 3) if total > 0 else 0.0,
        "avg_confidence": round(total_confidence / total, 3) if total > 0 else 0.0,
        "avg_iterations": round(total_iterations / total, 2) if total > 0 else 0.0
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        summary = generate_artifact_summary()
        print(json.dumps(summary, indent=2))
    else:
        print("Recent artifacts:")
        for artifact_path in get_latest_artifacts(5):
            try:
                artifact = load_artifact(artifact_path)
                print(f"\n✅ {artifact_path.name}")
                print(f"   File: {artifact['filepath']}")
                print(f"   Confidence: {artifact['summary']['repair_confidence']}")
                print(f"   Fully repaired: {artifact['summary']['fully_repaired']}")
            except Exception as e:
                print(f"\n❌ {artifact_path.name}")
                print(f"   Error: {e}")
