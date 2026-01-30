"""
Migration Base — Schema Version Upgrade Framework

Provides base classes and utilities for schema migrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathlib import Path
import json
from datetime import datetime, timezone


class Migration(ABC):
    """Base class for all schema migrations."""
    
    @property
    @abstractmethod
    def from_version(self) -> str:
        """Source schema version."""
        pass
    
    @property
    @abstractmethod
    def to_version(self) -> str:
        """Target schema version."""
        pass
    
    @abstractmethod
    def migrate(self, artifact: Dict) -> Dict:
        """
        Perform migration.
        
        Args:
            artifact: Artifact in source schema
        
        Returns:
            Artifact in target schema
        """
        pass
    
    @abstractmethod
    def rollback(self, artifact: Dict) -> Dict:
        """
        Rollback migration (if possible).
        
        Args:
            artifact: Artifact in target schema
        
        Returns:
            Artifact in source schema
        """
        pass
    
    def validate_source(self, artifact: Dict) -> bool:
        """Validate artifact is in expected source version."""
        return artifact.get("schema_version") == self.from_version
    
    def validate_target(self, artifact: Dict) -> bool:
        """Validate artifact is in expected target version."""
        return artifact.get("schema_version") == self.to_version


class MigrationLog:
    """Records all migrations performed."""
    
    def __init__(self, log_dir: Path = Path(".gatekeeper/migrations")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def record_migration(
        self,
        artifact_path: Path,
        from_version: str,
        to_version: str,
        success: bool,
        error: Optional[str] = None
    ) -> Path:
        """Record a migration operation."""
        
        timestamp = datetime.now(timezone.utc).isoformat()
        timestamp_short = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        log_entry = {
            "timestamp": timestamp,
            "artifact_path": str(artifact_path),
            "from_version": from_version,
            "to_version": to_version,
            "success": success,
            "error": error
        }
        
        log_filename = f"{timestamp_short}_migration.json"
        log_path = self.log_dir / log_filename
        
        log_path.write_text(json.dumps(log_entry, indent=2))
        return log_path
    
    def get_migration_history(self, artifact_path: Path) -> list[Dict]:
        """Get all migrations performed on a specific artifact."""
        history = []
        
        for log_file in sorted(self.log_dir.glob("*.json")):
            log_entry = json.loads(log_file.read_text())
            if log_entry["artifact_path"] == str(artifact_path):
                history.append(log_entry)
        
        return history
