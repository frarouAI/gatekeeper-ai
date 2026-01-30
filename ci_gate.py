"""
Gatekeeper CI Entry Point

Used by GitHub Actions to gate pull requests.
Respects .gatekeeper.yml configuration.
"""

import sys
import json
from pathlib import Path
from gatekeeper_config import GatekeeperConfig
from batch_processor import process_batch


def main():
    # Load configuration
    config = GatekeeperConfig.load()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print(f"✅ Loaded Gatekeeper config")
    print(f"   Profile: {config.profile}")
    print(f"   CI enabled: {config.ci.enabled}")
    print(f"   Repair mode: {config.repair.mode}")
    print(f"   Include patterns: {config.paths.include}")
    print(f"   Exclude patterns: {config.paths.exclude}")
    
    if not config.ci.enabled:
        print("⚠️  CI is disabled in config - skipping")
        sys.exit(0)
    
    # Process all files matching include/exclude patterns
    result = process_batch(
        paths=config.paths.include,
        profile=config.profile,
        enable_repair=config.repair.enabled,
        apply_repairs=False,  # CI NEVER mutates code
        recursive=True,
        exclude_patterns=config.paths.exclude
    )
    
    # Print results
    print("\n" + "="*70)
    print("GATEKEEPER CI RESULTS")
    print("="*70)
    print(json.dumps(result, indent=2))
    
    # Check CI pass conditions
    ci_pass = True
    
    if config.ci.fail_on_non_compliant:
        if not result.get("ci_pass", False):
            print(f"\n❌ CI Gate FAILED: {result['non_compliant_files']} non-compliant files detected")
            ci_pass = False
    
    if config.ci.fail_on_confidence_below > 0:
        repair_confidence = result.get("repair_confidence", 1.0)
        if repair_confidence < config.ci.fail_on_confidence_below:
            print(f"\n❌ CI Gate FAILED: Repair confidence {repair_confidence} below threshold {config.ci.fail_on_confidence_below}")
            ci_pass = False
    
    if ci_pass:
        print("\n✅ Gatekeeper CI PASSED")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
