"""
Migration Manager — Automatic Schema Upgrades

Handles automatic migration of artifacts between schema versions.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from migrations.migration_base import Migration, MigrationLog
from migrations.v1_0_to_v1_1 import MigrationV1_0_to_V1_1


class MigrationManager:
    """Manages schema migrations for artifacts."""
    
    def __init__(self):
        self.migrations: List[Migration] = [
            MigrationV1_0_to_V1_1(),
            # Add more migrations here as schema evolves
        ]
        self.log = MigrationLog()
    
    def get_migration_path(
        self,
        from_version: str,
        to_version: str
    ) -> Optional[List[Migration]]:
        """
        Find migration path between versions.
        
        Returns:
            List of migrations to apply, or None if no path exists
        """
        # Simple linear path for now
        # In production, implement graph-based pathfinding
        
        path = []
        current_version = from_version
        
        for migration in self.migrations:
            if migration.from_version == current_version:
                path.append(migration)
                current_version = migration.to_version
                
                if current_version == to_version:
                    return path
        
        return None
    
    def migrate_artifact(
        self,
        artifact_path: Path,
        target_version: str,
        backup: bool = True
    ) -> Dict:
        """
        Migrate artifact to target version.
        
        Args:
            artifact_path: Path to artifact file
            target_version: Desired schema version
            backup: Create backup before migration
        
        Returns:
            Migrated artifact
        """
        # Load artifact
        artifact = json.loads(artifact_path.read_text())
        current_version = artifact.get("schema_version")
        
        if current_version == target_version:
            print(f"Artifact already at version {target_version}")
            return artifact
        
        # Find migration path
        migration_path = self.get_migration_path(current_version, target_version)
        
        if not migration_path:
            raise ValueError(
                f"No migration path from {current_version} to {target_version}"
            )
        
        # Create backup if requested
        if backup:
            backup_path = artifact_path.with_suffix(".json.bak")
            backup_path.write_text(artifact_path.read_text())
            print(f"Backup created: {backup_path}")
        
        # Apply migrations
        migrated = artifact
        
        for migration in migration_path:
            print(f"Applying: {migration.from_version} → {migration.to_version}")
            
            try:
                migrated = migration.migrate(migrated)
                
                # Log successful migration
                self.log.record_migration(
                    artifact_path=artifact_path,
                    from_version=migration.from_version,
                    to_version=migration.to_version,
                    success=True
                )
                
            except Exception as e:
                # Log failed migration
                self.log.record_migration(
                    artifact_path=artifact_path,
                    from_version=migration.from_version,
                    to_version=migration.to_version,
                    success=False,
                    error=str(e)
                )
                raise
        
        # Write migrated artifact
        artifact_path.write_text(json.dumps(migrated, indent=2))
        print(f"✅ Migration complete: {current_version} → {target_version}")
        
        return migrated
    
    def rollback_artifact(
        self,
        artifact_path: Path,
        target_version: str
    ) -> Dict:
        """
        Rollback artifact to previous version.
        
        Args:
            artifact_path: Path to artifact file
            target_version: Desired schema version
        
        Returns:
            Rolled-back artifact
        """
        # Load artifact
        artifact = json.loads(artifact_path.read_text())
        current_version = artifact.get("schema_version")
        
        if current_version == target_version:
            print(f"Artifact already at version {target_version}")
            return artifact
        
        # Find rollback path (reverse of migration path)
        migration_path = self.get_migration_path(target_version, current_version)
        
        if not migration_path:
            raise ValueError(
                f"No rollback path from {current_version} to {target_version}"
            )
        
        # Apply rollbacks in reverse order
        rolled_back = artifact
        
        for migration in reversed(migration_path):
            print(f"Rolling back: {migration.to_version} → {migration.from_version}")
            
            try:
                rolled_back = migration.rollback(rolled_back)
                
            except Exception as e:
                print(f"❌ Rollback failed: {e}")
                raise
        
        # Write rolled-back artifact
        artifact_path.write_text(json.dumps(rolled_back, indent=2))
        print(f"✅ Rollback complete: {current_version} → {target_version}")
        
        return rolled_back
    
    def migrate_all_artifacts(
        self,
        artifacts_dir: Path,
        target_version: str
    ) -> Dict:
        """
        Migrate all artifacts in directory to target version.
        
        Returns:
            Summary of migrations
        """
        artifacts = list(artifacts_dir.glob("*.json"))
        
        summary = {
            "total": len(artifacts),
            "migrated": 0,
            "already_current": 0,
            "failed": 0,
            "errors": []
        }
        
        for artifact_path in artifacts:
            try:
                artifact = json.loads(artifact_path.read_text())
                current_version = artifact.get("schema_version")
                
                if current_version == target_version:
                    summary["already_current"] += 1
                else:
                    self.migrate_artifact(artifact_path, target_version)
                    summary["migrated"] += 1
                    
            except Exception as e:
                summary["failed"] += 1
                summary["errors"].append({
                    "file": str(artifact_path),
                    "error": str(e)
                })
        
        return summary


# CLI for running migrations
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
Usage:
  python migration_manager.py migrate <artifact> <target_version>
  python migration_manager.py migrate-all <target_version>
  python migration_manager.py rollback <artifact> <target_version>
        """)
        sys.exit(1)
    
    manager = MigrationManager()
    command = sys.argv[1]
    
    if command == "migrate" and len(sys.argv) >= 4:
        artifact_path = Path(sys.argv[2])
        target_version = sys.argv[3]
        manager.migrate_artifact(artifact_path, target_version)
        
    elif command == "migrate-all" and len(sys.argv) >= 3:
        target_version = sys.argv[2]
        artifacts_dir = Path(".gatekeeper/artifacts")
        summary = manager.migrate_all_artifacts(artifacts_dir, target_version)
        print("\n" + json.dumps(summary, indent=2))
        
    elif command == "rollback" and len(sys.argv) >= 4:
        artifact_path = Path(sys.argv[2])
        target_version = sys.argv[3]
        manager.rollback_artifact(artifact_path, target_version)
        
    else:
        print("Invalid command")
        sys.exit(1)
