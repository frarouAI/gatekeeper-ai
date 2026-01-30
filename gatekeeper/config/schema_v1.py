from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ConfigV1:
    version: int
    profile: str
    forbidden_paths: List[str]
