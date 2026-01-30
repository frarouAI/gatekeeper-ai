"""
Gatekeeper Configuration — Project-Level Settings

Loads and validates .gatekeeper.yml configuration files.
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class CIConfig:
    """CI/CD integration settings."""
    enabled: bool = True
    fail_on_non_compliant: bool = True
    fail_on_confidence_below: float = 0.85


@dataclass
class RepairConfig:
    """Repair behavior settings."""
    enabled: bool = True
    mode: str = "dry-run"  # dry-run | live
    max_iterations: int = 3
    confidence_threshold: float = 0.9


@dataclass
class ArtifactsConfig:
    """Artifact storage settings."""
    retention_days: int = 180
    store_diff: bool = True
    validate_schema: bool = True


@dataclass
class PathsConfig:
    """File path filtering."""
    include: List[str] = field(default_factory=lambda: ["**/*.py"])
    exclude: List[str] = field(default_factory=lambda: ["tests/**", "vendor/**"])


@dataclass
class GatekeeperConfig:
    """Complete Gatekeeper configuration."""
    version: int = 1
    profile: str = "strict"
    ci: CIConfig = field(default_factory=CIConfig)
    repair: RepairConfig = field(default_factory=RepairConfig)
    artifacts: ArtifactsConfig = field(default_factory=ArtifactsConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'GatekeeperConfig':
        """Create config from dictionary."""
        return cls(
            version=config_dict.get('version', 1),
            profile=config_dict.get('profile', 'strict'),
            ci=CIConfig(**config_dict.get('ci', {})),
            repair=RepairConfig(**config_dict.get('repair', {})),
            artifacts=ArtifactsConfig(**config_dict.get('artifacts', {})),
            paths=PathsConfig(**config_dict.get('paths', {}))
        )
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'GatekeeperConfig':
        """
        Load configuration from file.
        
        Args:
            config_path: Path to .gatekeeper.yml (or None to search)
        
        Returns:
            GatekeeperConfig instance
        """
        if config_path is None:
            # Search for config in current directory and parents
            config_path = cls.find_config()
        
        if config_path is None or not config_path.exists():
            print("No .gatekeeper.yml found, using defaults")
            return cls()
        
        print(f"Loading config from: {config_path}")
        
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls.from_dict(config_dict)
    
    @staticmethod
    def find_config(start_dir: Optional[Path] = None) -> Optional[Path]:
        """Search for .gatekeeper.yml in current dir and parents."""
        if start_dir is None:
            start_dir = Path.cwd()
        
        current = start_dir
        
        # Search up to 5 parent directories
        for _ in range(5):
            config_path = current / ".gatekeeper.yml"
            if config_path.exists():
                return config_path
            
            # Move to parent
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        
        return None
    
    def validate(self) -> List[str]:
        """
        Validate configuration values.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if self.version != 1:
            errors.append(f"Unsupported config version: {self.version}")
        
        if self.profile not in ["strict", "balanced", "permissive"]:
            errors.append(f"Invalid profile: {self.profile}")
        
        if self.repair.mode not in ["dry-run", "live"]:
            errors.append(f"Invalid repair mode: {self.repair.mode}")
        
        if not 0.0 <= self.ci.fail_on_confidence_below <= 1.0:
            errors.append(f"CI confidence threshold must be 0.0-1.0")
        
        if not 0.0 <= self.repair.confidence_threshold <= 1.0:
            errors.append(f"Repair confidence threshold must be 0.0-1.0")
        
        if self.repair.max_iterations < 1:
            errors.append(f"Max iterations must be >= 1")
        
        if self.artifacts.retention_days < 1:
            errors.append(f"Retention days must be >= 1")
        
        return errors
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        return {
            "version": self.version,
            "profile": self.profile,
            "ci": {
                "enabled": self.ci.enabled,
                "fail_on_non_compliant": self.ci.fail_on_non_compliant,
                "fail_on_confidence_below": self.ci.fail_on_confidence_below
            },
            "repair": {
                "enabled": self.repair.enabled,
                "mode": self.repair.mode,
                "max_iterations": self.repair.max_iterations,
                "confidence_threshold": self.repair.confidence_threshold
            },
            "artifacts": {
                "retention_days": self.artifacts.retention_days,
                "store_diff": self.artifacts.store_diff,
                "validate_schema": self.artifacts.validate_schema
            },
            "paths": {
                "include": self.paths.include,
                "exclude": self.paths.exclude
            }
        }


def create_default_config(output_path: Path = Path(".gatekeeper.yml")):
    """Create a default configuration file."""
    config = GatekeeperConfig()
    
    yaml_content = yaml.dump(config.to_dict(), default_flow_style=False, sort_keys=False)
    
    output_path.write_text(yaml_content)
    print(f"✅ Created default config: {output_path}")


# CLI for config management
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        create_default_config()
    else:
        # Load and validate current config
        config = GatekeeperConfig.load()
        errors = config.validate()
        
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("✅ Configuration valid")
            print(yaml.dump(config.to_dict(), default_flow_style=False))
