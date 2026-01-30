from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Profile:
    name: str
    fail_on_warnings: bool
    max_warnings: int


# Canonical profiles
PROFILES: Dict[str, Profile] = {
    "default": Profile(
        name="default",
        fail_on_warnings=False,
        max_warnings=999,
    ),
    "strict": Profile(
        name="strict",
        fail_on_warnings=True,
        max_warnings=0,
    ),
    "lenient": Profile(
        name="lenient",
        fail_on_warnings=False,
        max_warnings=5,
    ),
}


# Ownership mapping: path prefix → profile
OWNERSHIP_RULES = [
    ("/secrets", "strict"),
    ("/private", "strict"),
    ("/src", "default"),
]


def resolve_profile(path: str) -> Profile:
    """
    Resolve profile based on ownership rules.
    First match wins.
    """
    for prefix, profile_name in OWNERSHIP_RULES:
        if f"/{prefix.strip('/')}/" in f"/{path}/":
            return PROFILES[profile_name]
    return PROFILES["default"]
