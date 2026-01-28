# verdict_cache.py

import os
import json
import hashlib
from typing import Any, Dict


class VerdictCache:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _path(self, key: str) -> str:
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{h}.json")

    def get(self, key: str) -> Dict[str, Any] | None:
        path = self._path(key)
        if not os.path.exists(path):
            return None

        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, key: str, verdict: Dict[str, Any]) -> None:
        path = self._path(key)
        with open(path, "w") as f:
            json.dump(verdict, f, indent=2)
