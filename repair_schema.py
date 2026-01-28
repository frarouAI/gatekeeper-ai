"""
Repair Schema — Structured Diff Format

Defines the contract for repair proposals.
All repairs must conform to this schema.
"""

from typing import TypedDict, List


# Schema versioning for backward compatibility
SCHEMA_VERSION = "1.0"


# Controlled vocabulary for repair categories
ALLOWED_CATEGORIES = {
    "spacing",
    "docstring",
    "naming",
    "typing",
    "logic",
    "security",
}


class RepairPatch(TypedDict):
    """Single repair operation."""
    line: int              # Line number (1-indexed)
    old: str              # Original line content
    new: str              # Replacement line content
    reason: str           # Why this change is needed
    category: str         # Must be from ALLOWED_CATEGORIES
    blocking: bool        # Is this a blocking failure?


class RepairProposal(TypedDict):
    """Complete repair proposal for a file."""
    schema_version: str
    filepath: str
    patches: List[RepairPatch]
    total_changes: int
    blocking_changes: int
    non_blocking_changes: int


def validate_patch(patch: dict) -> bool:
    """
    Validate that a patch conforms to schema.
    
    Returns:
        True if valid, False otherwise
    """
    required_keys = {"line", "old", "new", "reason", "category", "blocking"}
    
    if not all(key in patch for key in required_keys):
        return False
    
    if not isinstance(patch["line"], int) or patch["line"] < 1:
        return False
    
    if not all(isinstance(patch[k], str) for k in ["old", "new", "reason", "category"]):
        return False
    
    if not isinstance(patch["blocking"], bool):
        return False
    
    # Soft validation: warn if category not in allowed set
    if patch["category"] not in ALLOWED_CATEGORIES:
        print(f"WARNING: Category '{patch['category']}' not in ALLOWED_CATEGORIES. Allowed: {ALLOWED_CATEGORIES}")
    
    return True


def apply_patches_preview(original_code: str, patches: List[RepairPatch]) -> str:
    """
    Preview what code would look like after applying patches.
    Does NOT modify files - returns transformed code as string.
    
    Args:
        original_code: Original source code
        patches: List of patches to apply
    
    Returns:
        Code with patches applied (preview only)
    """
    lines = original_code.split('\n')
    
    # Sort patches by line number (descending) to avoid index shifts
    sorted_patches = sorted(patches, key=lambda p: p["line"], reverse=True)
    
    for patch in sorted_patches:
        line_idx = patch["line"] - 1  # Convert to 0-indexed
        
        if 0 <= line_idx < len(lines):
            # Verify old content matches (safety check - prevents silent corruption)
            if lines[line_idx].strip() == patch["old"].strip():
                lines[line_idx] = patch["new"]
            else:
                # Mismatch - skip this patch and log warning
                print(f"WARNING: Line {patch['line']} mismatch. Expected: {patch['old']}, Found: {lines[line_idx]}")
    
    return '\n'.join(lines)


# Example usage (for testing)
if __name__ == "__main__":
    example_patch = {
        "line": 1,
        "old": "def add(x,y):",
        "new": "def add(x, y):",
        "reason": "PEP 8: Space after comma in parameters",
        "category": "spacing",
        "blocking": False
    }
    
    print("Valid patch:", validate_patch(example_patch))
    
    original = "def add(x,y):\n    return x+y"
    preview = apply_patches_preview(original, [example_patch])
    print("\nOriginal:")
    print(original)
    print("\nPreview:")
    print(preview)


def generate_diff_preview(original_code: str, patches: List[RepairPatch]) -> str:
    """
    Generate a unified diff showing what would change.
    
    Args:
        original_code: Original source code
        patches: List of patches to apply
    
    Returns:
        Unified diff string
    """
    import difflib
    
    # Apply patches to get new code
    new_code = apply_patches_preview(original_code, patches)
    
    # Generate unified diff
    original_lines = original_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile='original',
        tofile='proposed',
        lineterm=''
    )
    
    return ''.join(diff)


def display_preview(original_code: str, patches: List[RepairPatch]) -> None:
    """
    Display a human-readable preview of changes.
    
    Args:
        original_code: Original source code
        patches: List of patches to apply
    """
    print("\n" + "="*60)
    print("REPAIR PREVIEW")
    print("="*60)
    
    print(f"\nTotal patches: {len(patches)}")
    print(f"Blocking: {sum(1 for p in patches if p.get('blocking', False))}")
    print(f"Non-blocking: {sum(1 for p in patches if not p.get('blocking', False))}")
    
    print("\n" + "-"*60)
    print("PROPOSED CHANGES:")
    print("-"*60)
    
    for i, patch in enumerate(patches, 1):
        print(f"\n{i}. Line {patch['line']} - {patch['category']}")
        print(f"   Reason: {patch['reason']}")
        print(f"   - OLD: {patch['old']}")
        print(f"   + NEW: {patch['new']}")
    
    print("\n" + "-"*60)
    print("UNIFIED DIFF:")
    print("-"*60)
    print(generate_diff_preview(original_code, patches))
    
    print("\n" + "="*60)


def apply_patches_to_file(
    filepath: str,
    patches: List[RepairPatch],
    dry_run: bool = True,
    create_backup: bool = True
) -> dict:
    """
    Apply patches to a file with safety checks.
    
    Args:
        filepath: Path to file
        patches: List of patches to apply
        dry_run: If True, don't actually write (default: True for safety)
        create_backup: If True, create .bak file before modifying
    
    Returns:
        Dict with status and details
    """
    import shutil
    from pathlib import Path
    
    # Read original file
    with open(filepath, 'r') as f:
        original_code = f.read()
    
    # Apply patches
    new_code = apply_patches_preview(original_code, patches)
    
    # If dry-run, just return preview
    if dry_run:
        return {
            "status": "dry-run",
            "filepath": filepath,
            "patches_applied": 0,
            "backup_created": False,
            "preview": new_code
        }
    
    # Create backup if requested
    backup_path = None
    if create_backup:
        backup_path = f"{filepath}.bak"
        shutil.copy2(filepath, backup_path)
    
    # Write new code
    with open(filepath, 'w') as f:
        f.write(new_code)
    
    return {
        "status": "applied",
        "filepath": filepath,
        "patches_applied": len(patches),
        "backup_created": create_backup,
        "backup_path": backup_path,
        "original_size": len(original_code),
        "new_size": len(new_code)
    }
