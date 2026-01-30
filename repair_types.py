from dataclasses import dataclass


@dataclass(frozen=True)
class RepairPlan:
    rule_id: str
    file_path: str
    action: str
    description: str = ""
