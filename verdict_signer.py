import json
import hmac
import hashlib
from typing import Dict, Any


class VerdictSigner:
    def __init__(self, secret_key: str):
        if not secret_key:
            raise ValueError("Signing key must not be empty")
        self.secret_key = secret_key.encode("utf-8")

    def _canonical_json(self, verdict: Dict[str, Any]) -> bytes:
        """
        Deterministic JSON encoding for signing.
        Excludes existing signature if present.
        """
        clean = dict(verdict)
        clean.pop("signature", None)
        return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign(self, verdict: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._canonical_json(verdict)

        sig = hmac.new(
            self.secret_key,
            payload,
            hashlib.sha256
        ).hexdigest()

        signed = dict(verdict)
        signed["signature"] = {
            "alg": "HMAC-SHA256",
            "value": sig,
        }

        return signed

    def verify(self, verdict: Dict[str, Any]) -> bool:
        sig_block = verdict.get("signature")
        if not sig_block:
            return False

        expected = sig_block.get("value")
        if not expected:
            return False

        payload = self._canonical_json(verdict)

        actual = hmac.new(
            self.secret_key,
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(actual, expected)
