"""
Gatekeeper Artifact Signer

Produces tamper-evident SHA256 signatures.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


def sign_file(path: Path) -> Path:
    """Create SHA256 signature for a file."""
    if not path.exists():
        raise FileNotFoundError(path)

    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    signature = {
        "algorithm": "sha256",
        "digest": digest,
        "signed_at": datetime.now(timezone.utc).isoformat(),
    }

    sig_path = path.with_suffix(path.suffix + ".sig.json")
    sig_path.write_text(json.dumps(signature, indent=2))

    print(f"🔐 Signed: {sig_path}")
    return sig_path
