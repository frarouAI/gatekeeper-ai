import os
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # fallback if ever needed

from gatekeeper.config.schema_v1 import ConfigV1


CONFIG_FILENAME = ".gatekeeper.toml"


class ConfigError(RuntimeError):
    pass


def load_config(repo_path: str) -> ConfigV1:
    config_path = os.path.join(repo_path, CONFIG_FILENAME)

    if not os.path.exists(config_path):
        raise ConfigError(
            f"Missing required config file: {CONFIG_FILENAME}"
        )

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    version = data.get("version")
    if version != 1:
        raise ConfigError(
            f"Unsupported config version: {version!r} (expected 1)"
        )

    profile = data.get("profile", {}).get("name", "default")

    forbidden = data.get("paths", {}).get("forbidden")
    if not isinstance(forbidden, list) or not all(isinstance(p, str) for p in forbidden):
        raise ConfigError("paths.forbidden must be a list of strings")

    return ConfigV1(
        version=1,
        profile=profile,
        forbidden_paths=forbidden,
    )
