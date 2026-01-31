from pathlib import Path

FORBIDDEN_PATHS = {"secrets"}

def scan(root: Path) -> list[str]:
    violations = []
    for p in root.rglob("*"):
        if p.is_file():
            for forbidden in FORBIDDEN_PATHS:
                if forbidden in p.parts:
                    violations.append(str(p))
    return violations
