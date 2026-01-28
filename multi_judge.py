import json
import hashlib
from typing import Dict
from datetime import datetime, timezone

from engines.registry import get_engine
from verdict_cache import VerdictCache
from verdict_signer import VerdictSigner

SCHEMA_VERSION = "1.2"

PROFILES = {
    "startup": {"threshold": 75},
    "strict":  {"threshold": 85},
    "relaxed": {"threshold": 65},
}


class MultiAgentCodeJudge:
    def __init__(
        self,
        model: str,
        engine: str | None = None,
        engine_version: str | None = None,
        profile: str | None = None,
        gate: bool = False,
        cache: VerdictCache | None = None,
        signer: VerdictSigner | None = None,
        verify: bool = False,
        enable_metering: bool = True,
        enable_cache: bool = True,
    ):
        if profile not in PROFILES:
            raise ValueError(f"Unknown profile '{profile}'. Available: {list(PROFILES.keys())}")

        resolved_engine = engine_version or engine
        if not resolved_engine:
            raise ValueError("Either engine or engine_version must be provided")

        self.model = model
        self.engine_version = resolved_engine
        self.profile_name = profile
        self.threshold = PROFILES[profile]["threshold"]
        self.gate = gate

        EngineClass = get_engine(resolved_engine)
        self.engine = EngineClass(model=model, profile=profile)

        self.cache = cache if cache is not None else (VerdictCache() if enable_cache else None)
        self.signer = signer
        self.verify_signatures = verify
        self.enable_metering = enable_metering

    def _cache_key(self, code: str) -> str:
        h = hashlib.sha256()
        h.update(code.encode("utf-8"))
        return h.hexdigest()

    def judge(self, code: str, file_path: str | None = None) -> dict:
        if self.cache:
            key = self._cache_key(code)
            cached = self.cache.get(key)
            if cached:
                return cached

        verdicts = self.engine.judge(code)

        total_weighted_score = 0.0
        total_weight = 0.0
        blocking_failures = []

        for v in verdicts:
            agent = v.get("agent")
            score = v.get("score", 0)
            passed = v.get("pass", False)

            from engines.v1 import AGENT_POLICY
            policy = AGENT_POLICY.get(agent, {"weight": 1.0, "blocking": False})

            weight = policy["weight"]
            total_weighted_score += score * weight
            total_weight += weight

            if policy["blocking"] and not passed:
                blocking_failures.append(agent)

        final_score = round(total_weighted_score / total_weight, 2) if total_weight else 0.0
        passed = final_score >= self.threshold and not blocking_failures

        verdict = {
            "schema_version": SCHEMA_VERSION,
            "engine": self.engine_version,
            "profile": self.profile_name,
            "score": final_score,
            "pass": passed,
            "blocking_failures": blocking_failures,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdicts": verdicts,
            "file": file_path,
        }

        if self.cache:
            self.cache.set(self._cache_key(code), verdict)

        if self.signer:
            verdict["signature"] = self.signer.sign(verdict)

        return verdict

    def judge_repo(self, files: Dict[str, str]) -> dict:
        results = {}
        failures = []

        for path, code in files.items():
            verdict = self.judge(code, file_path=path)
            results[path] = verdict
            if not verdict["pass"]:
                failures.append(path)

        return {
            "schema_version": SCHEMA_VERSION,
            "engine": self.engine_version,
            "profile": self.profile_name,
            "pass": not failures,
            "failures": failures,
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def gate_repo(self, files: Dict[str, str]) -> dict:
        return self.judge_repo(files)
