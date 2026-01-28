import json
import hashlib
from datetime import datetime, timezone
from typing import Dict

from claude_backend import ClaudeBackend
from agents import AGENTS, AGENT_POLICY, PROFILES
from verdict_cache import VerdictCache
from verdict_signer import VerdictSigner


SCHEMA_VERSION = "1.2"

JUDGE_INTERNAL_FILES = {
    "multi_judge.py",
    "agents.py",
    "claude_backend.py",
    "verdict_cache.py",
    "verdict_signer.py",
    "usage_meter.py",
    "claude_cli.py",
    "html_report.py",
    "json_judge.py",
    "clawdbot.py",
}


def determine_context(file_path: str | None) -> str:
    if not file_path:
        return "model_code"

    import os
    name = os.path.basename(file_path)

    if name in JUDGE_INTERNAL_FILES:
        return "judge_internal"

    if "/engines/" in file_path or file_path.startswith("engines/"):
        return "judge_internal"

    return "model_code"


class MultiAgentCodeJudge:
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        profile: str = "startup",
        engine_version: str = "v1",
        enable_cache: bool = True,
        enable_metering: bool = True,
        sign_key: str | None = None,
        verify: bool = False,
        max_tokens: int = 1500,
    ):
        if profile not in PROFILES:
            raise ValueError(f"Unknown profile: {profile}")

        self.profile_name = profile
        self.profile = PROFILES[profile]
        self.threshold = self.profile["threshold"]

        self.engine_version = engine_version
        self.name = f"claude-code-judge:{engine_version}"

        self.backend = ClaudeBackend(model=model, max_tokens=max_tokens)

        self.enable_cache = enable_cache
        self.enable_metering = enable_metering

        self.cache = VerdictCache() if enable_cache else None
        self.signer = VerdictSigner(sign_key.encode()) if sign_key else None
        self.verify_signatures = verify

    # ---------- internals ----------

    def _cache_key(self, code: str, context: str) -> str:
        h = hashlib.sha256()
        h.update(code.encode("utf-8"))
        h.update(context.encode("utf-8"))
        h.update(self.profile_name.encode("utf-8"))
        h.update(self.engine_version.encode("utf-8"))
        h.update(self.backend.model.encode("utf-8"))
        return h.hexdigest()

    def _build_prompt(self, agent_name: str, code: str, context: str) -> str:
        return f"""
Review the following Python code.

CONTEXT: {context}

Return STRICT JSON in this exact schema:
{{
  "agent": "{agent_name}",
  "pass": true | false,
  "score": 0-100,
  "issues": ["string", ...],
  "summary": "string"
}}

Rules:
- No markdown
- No commentary outside JSON

CODE:
{code}
"""

    def _run_agent(self, agent_name: str, code: str, context: str) -> dict:
        agent = AGENTS[agent_name]

        if "prompt_fn" in agent:
            system_prompt = agent["prompt_fn"](context)
        else:
            system_prompt = agent["system_prompt"]

        user_prompt = self._build_prompt(agent_name, code, context)

        raw = self.backend.judge(system_prompt, user_prompt)

        try:
            data = json.loads(raw)
        except Exception:
            return {
                "agent": agent_name,
                "pass": False,
                "score": 0,
                "issues": ["Model failed to return valid JSON"],
                "summary": "Invalid JSON response from model.",
            }

        return data

    # ---------- public API ----------

    def judge(self, code: str, file_path: str | None = None) -> dict:
        context = determine_context(file_path)

        cache_hit = False
        key = None

        if self.cache:
            key = self._cache_key(code, context)
            cached = self.cache.get(key)
            if cached:
                cached["cache_hit"] = True
                return cached

        verdicts = []
        blocking_failures = []

        total_weighted_score = 0.0
        total_weight = 0.0

        for agent_name in AGENTS:
            result = self._run_agent(agent_name, code, context)
            verdicts.append(result)

            policy = AGENT_POLICY[agent_name]
            weight = policy["weight"]

            total_weighted_score += result["score"] * weight
            total_weight += weight

            if policy["blocking"] and not result["pass"]:
                blocking_failures.append(agent_name)

        average_score = round(total_weighted_score / total_weight, 2)

        policy_pass = len(blocking_failures) == 0
        overall_pass = policy_pass and average_score >= self.threshold

        result = {
            "schema_version": SCHEMA_VERSION,
            "engine": self.name,
            "engine_version": self.engine_version,
            "model": self.backend.model,
            "profile": self.profile_name,
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_pass": overall_pass,
            "policy_pass": policy_pass,
            "average_score": average_score,
            "threshold": self.threshold,
            "blocking_failures": blocking_failures,
            "verdicts": verdicts,
            "cache_hit": cache_hit,
        }

        if self.signer:
            result = self.signer.sign(result)

        if self.cache and key:
            result["cache_hit"] = False
            self.cache.set(key, result)

        return result

    # ---------- MONETIZATION FEATURE ----------
    # Gate mode = the product

    def gate_repo(self, files: Dict[str, str]) -> dict:
        blocking_agents = []
        total_scores = []

        for path, code in files.items():
            verdict = self.judge(code, file_path=path)
            total_scores.append(verdict["average_score"])

            for agent in verdict["blocking_failures"]:
                if agent not in blocking_agents:
                    blocking_agents.append(agent)

        avg_score = round(sum(total_scores) / max(len(total_scores), 1), 2)

        gate_pass = len(blocking_agents) == 0 and avg_score >= self.threshold

        return {
            "gate_pass": gate_pass,
            "engine": self.engine_version,
            "profile": self.profile_name,
            "blocking_agents": blocking_agents,
            "average_score": avg_score,
            "threshold": self.threshold,
            "files": list(files.keys()),
        }
