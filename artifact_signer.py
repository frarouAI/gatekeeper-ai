"""
Artifact Signer — Gatekeeper AI

Provides deterministic hashing and signing metadata
for CI summaries, baselines, and artifacts.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict


def compute_sha256(data: str) -> str:
    """Compute SHA-256 hash of input string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def sign_artifact(path: Path) -> Dict:
    """
    Sign an artifact by hashing its contents.

    Returns signature metadata.
    """
    raw = path.read_text()
    digest = compute_sha256(raw)

    signature = {
        "algorithm": "sha256",
        "digest": digest,
        "signed_at": datetime.now(timezone.utc).isoformat()
    }

    return signature


def attach_signature(path: Path) -> Path:
    """
    Attach signature block to artifact (sidecar file).
    """
    signature = sign_artifact(path)
    sig_path = path.with_suffix(path.suffix + ".sig.json")
    sig_path.write_text(json.dumps(signature, indent=2))
    return sig_path
