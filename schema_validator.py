"""
Schema Validator — Enforce Data Contracts

Validates all artifacts and patches against versioned JSON schemas.
Fails closed on any schema violation.
"""

import json
from pathlib import Path
from typing import Dict, Optional
import jsonschema
from jsonschema import validate, ValidationError


SCHEMA_DIR = Path("schemas")


class SchemaValidator:
    """Validates data against versioned JSON schemas."""
    
    def __init__(self):
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Load all schema files."""
        for schema_file in SCHEMA_DIR.glob("*.json"):
            schema_name = schema_file.stem
            self.schemas[schema_name] = json.loads(schema_file.read_text())
    
    def validate_artifact(self, artifact: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate repair artifact against schema.
        
        Returns:
            (is_valid, error_message)
        """
        schema_version = artifact.get("schema_version", "")
        
        if not schema_version.startswith("gatekeeper-artifact-v1"):
            return False, f"Unsupported schema version: {schema_version}"
        
        schema = self.schemas.get("artifact_v1")
        if not schema:
            return False, "Schema artifact_v1.json not found"
        
        try:
            validate(instance=artifact, schema=schema)
            return True, None
        except ValidationError as e:
            return False, f"Schema validation failed: {e.message}"
    
    def validate_repair_patch(self, patch: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate repair patch against schema.
        
        Returns:
            (is_valid, error_message)
        """
        schema = self.schemas.get("artifact_v1")
        if not schema:
            return False, "Schema not found"
        
        patch_schema = schema.get("definitions", {}).get("repair_patch")
        if not patch_schema:
            return False, "Repair patch schema definition not found"
        
        try:
            validate(instance=patch, schema=patch_schema)
            return True, None
        except ValidationError as e:
            return False, f"Patch validation failed: {e.message}"


# Global validator instance
_validator = None


def get_validator() -> SchemaValidator:
    """Get or create global validator instance."""
    global _validator
    if _validator is None:
        _validator = SchemaValidator()
    return _validator


def validate_artifact_schema(artifact: Dict) -> None:
    """
    Validate artifact and raise exception if invalid.
    Fail-closed approach for safety.
    """
    validator = get_validator()
    is_valid, error = validator.validate_artifact(artifact)
    
    if not is_valid:
        raise ValueError(f"Artifact schema validation failed: {error}")


def validate_patch_schema(patch: Dict) -> None:
    """
    Validate patch and raise exception if invalid.
    Fail-closed approach for safety.
    """
    validator = get_validator()
    is_valid, error = validator.validate_repair_patch(patch)
    
    if not is_valid:
        raise ValueError(f"Patch schema validation failed: {error}")


# CLI for testing schemas
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python schema_validator.py <artifact.json>")
        sys.exit(1)
    
    artifact_path = Path(sys.argv[1])
    
    if not artifact_path.exists():
        print(f"Error: File not found: {artifact_path}")
        sys.exit(1)
    
    artifact = json.loads(artifact_path.read_text())
    
    try:
        validate_artifact_schema(artifact)
        print(f"✅ Valid artifact: {artifact_path}")
        print(f"   Schema: {artifact['schema_version']}")
        print(f"   Confidence: {artifact['summary']['repair_confidence']}")
    except ValueError as e:
        print(f"❌ Invalid artifact: {e}")
        sys.exit(1)
