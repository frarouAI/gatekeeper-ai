import json
from pathlib import Path
from datetime import datetime, timezone


class UsageMeter:
    def __init__(self, path: str = "usage_log.json"):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("[]")

    def record(self, *, model: str, engine: str, profile: str, agents: int, cache_hit: bool):
        with open(self.path, "r") as f:
            data = json.load(f)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "engine": engine,
            "profile": profile,
            "agents": agents,
            "cache_hit": cache_hit,
        }

        data.append(entry)

        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)
