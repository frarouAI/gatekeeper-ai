from pathlib import Path
from typing import Union

from judge import judge_code


def run_gatekeeper(
    *,
    path: Union[str, Path],
    profile: str = "strict",
    repair_live: bool = False,
    repair_dry_run: bool = False,
):
    """
    Thin test helper that calls the real judge engine.

    IMPORTANT:
    - No logic
    - No conditionals
    - No defaults overridden
    - No swallowing results

    Tests rely on the judge to enforce all behavior.
    """

    return judge_code(
        path=Path(path),
        profile=profile,
        repair_live=repair_live,
        repair_dry_run=repair_dry_run,
    )
