"""
Migration v1.0 → v1.1

Changes:
- Add "repair_method" field to summary (value: "iterative" or "single-pass")
- Add "token_usage" to metadata (for cost tracking)
- Add "git_context" to metadata (for commit tracking)
"""

from typing import Dict
from migrations.migration_base import Migration


class MigrationV1_0_to_V1_1(Migration):
    """Migrate artifacts from v1.0 to v1.1."""
    
    @property
    def from_version(self) -> str:
        return "gatekeeper-artifact-v1.0"
    
    @property
    def to_version(self) -> str:
        return "gatekeeper-artifact-v1.1"
    
    def migrate(self, artifact: Dict) -> Dict:
        """Upgrade v1.0 → v1.1."""
        
        if not self.validate_source(artifact):
            raise ValueError(f"Artifact is not version {self.from_version}")
        
        # Create new artifact with v1.1 schema
        migrated = artifact.copy()
        
        # Update schema version
        migrated["schema_version"] = self.to_version
        
        # Add new fields to summary
        summary = migrated.get("summary", {})
        
        # Infer repair method from iterations
        iterations = summary.get("iterations_used", 0)
        summary["repair_method"] = "iterative" if iterations > 1 else "single-pass"
        
        migrated["summary"] = summary
        
        # Add new fields to metadata
        metadata = migrated.get("metadata", {})
        
        # Add token usage (unknown for historical data)
        metadata["token_usage"] = {
            "total_tokens": None,
            "estimated": False,
            "note": "Token tracking not available in v1.0"
        }
        
        # Add git context (unknown for historical data)
        metadata["git_context"] = {
            "branch": None,
            "commit": None,
            "note": "Git tracking not available in v1.0"
        }
        
        migrated["metadata"] = metadata
        
        return migrated
    
    def rollback(self, artifact: Dict) -> Dict:
        """Downgrade v1.1 → v1.0."""
        
        if not self.validate_target(artifact):
            raise ValueError(f"Artifact is not version {self.to_version}")
        
        # Create rolled-back artifact
        rolled_back = artifact.copy()
        
        # Revert schema version
        rolled_back["schema_version"] = self.from_version
        
        # Remove v1.1 fields from summary
        summary = rolled_back.get("summary", {})
        summary.pop("repair_method", None)
        rolled_back["summary"] = summary
        
        # Remove v1.1 fields from metadata
        metadata = rolled_back.get("metadata", {})
        metadata.pop("token_usage", None)
        metadata.pop("git_context", None)
        rolled_back["metadata"] = metadata
        
        return rolled_back
