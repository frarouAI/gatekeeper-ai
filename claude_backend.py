"""
Claude Backend — Hardened, Retry-Safe, Cost-Aware

Enterprise guarantees:
- Bounded retries with exponential backoff
- Hard timeouts (never hang)
- Cost tracking per call
- Structured failure responses (no surprise crashes)
- CI-safe fallback signaling
"""

from __future__ import annotations

import os
import time
import anthropic
from typing import Dict, Any, Optional

# ------------------------------------------------------------
# Pricing table (USD per 1M tokens)
# ------------------------------------------------------------
PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
    }
}

# ------------------------------------------------------------
# Retry / timeout policy (HARD GUARANTEES)
# ------------------------------------------------------------
MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 2, 4]  # exponential
DEFAULT_TIMEOUT = 30.0


class ClaudeBackend:
    """
    Hardened Claude API client.

    Never raises on transient failures.
    Always returns structured results.
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1500,
        temperature: float = 0.0,
        timeout: Optional[float] = None,
        **_ignored: Dict,
    ):
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        self.available = bool(api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout or DEFAULT_TIMEOUT

        self.client = (
            anthropic.Anthropic(api_key=api_key)
            if api_key
            else None
        )

        # ---- Usage tracking (per-call) ----
        self.last_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
        }

    # --------------------------------------------------------
    # Cost estimation
    # --------------------------------------------------------
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = PRICING.get(self.model)
        if not pricing:
            return 0.0

        return round(
            (input_tokens / 1_000_000) * pricing["input"]
            + (output_tokens / 1_000_000) * pricing["output"],
            6,
        )

    # --------------------------------------------------------
    # Error classification
    # --------------------------------------------------------
    def _classify_error(self, exc: Exception) -> Dict[str, Any]:
        msg = str(exc).lower()

        if "rate limit" in msg or "429" in msg:
            return {"type": "rate_limit", "retryable": True}

        if "timeout" in msg:
            return {"type": "timeout", "retryable": True}

        if "5" in msg:
            return {"type": "server_error", "retryable": True}

        if "authentication" in msg or "api key" in msg:
            return {"type": "auth_error", "retryable": False}

        return {"type": "unknown", "retryable": False}

    # --------------------------------------------------------
    # Primary API
    # --------------------------------------------------------
    def judge(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Execute a Claude request.

        Returns:
            {
              ok: bool,
              text: str | None,
              error_type: str | None,
              retryable: bool,
              usage: dict
            }
        """

        if not self.available:
            return {
                "ok": False,
                "text": None,
                "error_type": "no_api_key",
                "retryable": False,
                "usage": self.last_usage,
            }

        messages = [{"role": "user", "content": user_prompt}]

        for attempt in range(MAX_RETRIES):
            try:
                msg = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    timeout=self.timeout,
                )

                usage = msg.usage or {}
                input_tokens = usage.input_tokens or 0
                output_tokens = usage.output_tokens or 0

                self.last_usage = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "estimated_cost_usd": self._estimate_cost(
                        input_tokens, output_tokens
                    ),
                }

                return {
                    "ok": True,
                    "text": msg.content[0].text.strip(),
                    "error_type": None,
                    "retryable": False,
                    "usage": self.last_usage,
                }

            except Exception as exc:
                info = self._classify_error(exc)

                if not info["retryable"] or attempt == MAX_RETRIES - 1:
                    return {
                        "ok": False,
                        "text": None,
                        "error_type": info["type"],
                        "retryable": info["retryable"],
                        "usage": self.last_usage,
                    }

                time.sleep(BACKOFF_SECONDS[attempt])

        # Should never reach here
        return {
            "ok": False,
            "text": None,
            "error_type": "exhausted",
            "retryable": False,
            "usage": self.last_usage,
        }


# ------------------------------------------------------------
# Manual sanity check
# ------------------------------------------------------------
if __name__ == "__main__":
    backend = ClaudeBackend()
    print("Backend initialized:")
    print("  model:", backend.model)
    print("  available:", backend.available)
    print("  timeout:", backend.timeout)
