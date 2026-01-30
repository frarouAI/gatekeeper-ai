"""
Phase 5B — Safe Auto-Fix Rule

Rule:
- missing_required_header

Purpose:
- Insert a managed header at the top of Python files
- Strict profile only
- Fully auditable
- Dry-run safe
"""

HEADER_RULE_ID = "missing_required_header"

HEADER = (
    "# Gatekeeper: Managed File\n"
    "# Owner: unknown\n"
    "# Policy: strict\n\n"
)


def has_header(content: str) -> bool:
    """
    Detect whether the managed header already exists.

    This must be conservative:
    - Never false-negative
    - Never duplicate headers
    """
    return content.startswith("# Gatekeeper: Managed File")
