from dataclasses import dataclass
from typing import List
import os

from gatekeeper.config.schema_v1 import ConfigV1


# ---------- Core Data Structures ----------

@dataclass(frozen=True)
class Failure:
    kind: str
    rule_id: str
    files: List[str]
    message: str


@dataclass(frozen=True)
class Verdict:
    compliant: bool
    profile: str
    failures: List[Failure]


# ---------- Engine v1 ----------

def _is_forbidden(rel_path: str, forbidden_paths: List[str]) -> bool:
    return any(rel_path.startswith(p) for p in forbidden_paths)


def run(path: str, config: ConfigV1) -> Verdict:
    failures: List[Failure] = []

    for root, _, files in os.walk(path):
        for name in files:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, path)

            if _is_forbidden(rel_path, config.forbidden_paths):
                failures.append(
                    Failure(
                        kind="forbidden_path",
                        rule_id="FORBIDDEN_PATH",
                        files=[rel_path],
                        message="forbidden path touched",
                    )
                )

    if failures:
        return Verdict(
            compliant=False,
            profile=config.profile,
            failures=failures,
        )

    return Verdict(
        compliant=True,
        profile=config.profile,
        failures=[],
    )
