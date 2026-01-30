import yaml
from pathlib import Path

SKILL_DIR = Path("schemas/skills")

class SkillRegistryError(Exception):
    pass


def load_skill(skill_id: str) -> dict:
    path = SKILL_DIR / f"{skill_id}.yaml"
    if not path.exists():
        raise SkillRegistryError(f"Skill not found: {skill_id}")
    return yaml.safe_load(path.read_text())
