"""
Gatekeeper configuration loader.

This is the SINGLE public entrypoint for reading and validating
.gatekeeper.yml files.

Public API:
- load_config(path) -> Config
"""

from dataclasses import dataclass
from pathlib import Path
import yaml
import json
import jsonschema


# --------------------------------------------------
# Data models
# --------------------------------------------------
@dataclass
class RuntimeConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1500
    temperature: float = 0.0
    timeout: int = 30
    cost_limit_usd: float = 1.0


@dataclass
class CIConfig:
    enabled: bool = True
    fail_on_confidence_below: float | None = None


@dataclass
class RepairConfig:
    enabled: bool = False
    mode: str = "dry-run"
    max_iterations: int = 1
    confidence_threshold: float | None = None


@dataclass
class PathsConfig:
    include: list[str]


@dataclass
class Config:
    version: int
    profile: str
    paths: PathsConfig
    runtime: RuntimeConfig
    ci: CIConfig
    repair: RepairConfig


# --------------------------------------------------
# Loader
# --------------------------------------------------
def load_config(path: str | Path) -> Config:
    """
    Load, validate, and normalize .gatekeeper.yml.

    Raises:
        Exception on invalid config.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    raw = yaml.safe_load(path.read_text())

    # Load schema
    schema_path = Path("schemas/config_v1.json")
    if not schema_path.exists():
        raise FileNotFoundError("schemas/config_v1.json not found")

    schema = json.loads(schema_path.read_text())

    # Validate
    jsonschema.validate(raw, schema)

    # Normalize
    runtime = raw.get("runtime", {})
    ci = raw.get("ci", {})
    repair = raw.get("repair", {})
    paths = raw.get("paths", {})

    return Config(
        version=raw["version"],
        profile=raw["profile"],
        paths=PathsConfig(
            include=paths.get("include", [])
        ),
        runtime=RuntimeConfig(
            model=runtime.get("model", "claude-sonnet-4-20250514"),
            max_tokens=runtime.get("max_tokens", 1500),
            temperature=runtime.get("temperature", 0.0),
            timeout=runtime.get("timeout", 30),
            cost_limit_usd=runtime.get("cost_limit_usd", 1.0),
        ),
        ci=CIConfig(
            enabled=ci.get("enabled", True),
            fail_on_confidence_below=ci.get("fail_on_confidence_below"),
        ),
        repair=RepairConfig(
            enabled=repair.get("enabled", False),
            mode=repair.get("mode", "dry-run"),
            max_iterations=repair.get("max_iterations", 1),
            confidence_threshold=repair.get("confidence_threshold"),
        ),
    )
