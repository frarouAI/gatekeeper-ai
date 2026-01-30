"""
Shared utility helpers for Gatekeeper.
Stable, dependency-free, CI-safe.
"""

def print_header(title: str, width: int = 70) -> None:
    """
    Print a standardized section header to stdout.

    Used by CI, CLI tools, and future UI adapters.
    """
    line = "=" * width
    print("\n" + line)
    print(title.center(width))
    print(line)
