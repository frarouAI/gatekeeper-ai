"""
MultiAgentCodeJudge — Repo-wide orchestration with cost tracking.
Hard contract: ALWAYS returns a complete result schema.
"""

from engines.v1 import EngineV1


class MultiAgentCodeJudge:
    def __init__(
        self,
        *,
        model: str,
        profile: str,
        engine_version: str = "v1",
        max_tokens: int = 1500,
        temperature: float = 0.0,
        timeout: float | None = None,
        cost_limit_usd: float = 1.0,
    ):
        if engine_version != "v1":
            raise ValueError(f"Unsupported engine version: {engine_version}")

        self.engine = EngineV1(
            model=model,
            profile=profile,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
            cost_limit_usd=cost_limit_usd,
        )

        self.profile = profile
        self.threshold = self.engine.threshold
        self.cost_limit_usd = cost_limit_usd

    def judge(self, code: str, file_path: str | None = None) -> dict:
        verdicts = self.engine.judge(code)

        valid = [v for v in verdicts if not v.get("error")]
        avg_score = (
            sum(v.get("score", 0) for v in valid) / len(valid)
            if valid else 0.0
        )

        passed = avg_score >= self.threshold

        return {
            "file": file_path,
            "verdicts": verdicts,
            "average_score": avg_score,
            "pass": passed,
        }

    def judge_repo(self, files: dict[str, str]) -> dict:
        results = []
        non_compliant_files = []
        cost_limit_hit = False

        for path, code in files.items():
            cost = self.engine.get_cost_summary()["estimated_cost_usd"]

            if cost >= (self.cost_limit_usd * 0.9):
                cost_limit_hit = True
                break

            result = self.judge(code, file_path=path)
            results.append(result)

            if not result["pass"]:
                non_compliant_files.append(path)

        avg_score = (
            sum(r["average_score"] for r in results) / len(results)
            if results else 0.0
        )

        return {
            "results": results,
            "average_score": avg_score,
            "threshold": self.threshold,
            "gate_pass": avg_score >= self.threshold and not cost_limit_hit,
            "blocking_agents": [],
            "non_compliant_files": non_compliant_files,
            "cost_summary": self.engine.get_cost_summary(),
            "cost_limit_hit": cost_limit_hit,
            "files_processed": len(results),
            "files_total": len(files),
        }
