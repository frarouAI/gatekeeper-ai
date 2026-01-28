"""
Gatekeeper Judge — Code Quality Assessment

This module contains the core judging logic that evaluates Python code
against quality standards.
"""

def judge_code(code: str, profile: str = "strict") -> dict:
    """
    Judge Python code against quality standards.
    
    Args:
        code: Python source code to evaluate
        profile: Strictness level (strict, balanced, permissive)
    
    Returns:
        Dictionary with:
        - compliant: bool
        - failures: list of failure descriptions
        - score: optional quality score
    """
    
    failures = []
    
    # Basic checks (expand these based on your standards)
    
    # Check 1: Spacing around operators
    if profile in ["strict", "balanced"]:
        if "=" in code and "= " not in code and " =" not in code:
            # Simple heuristic - could be improved
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if '=' in line and not any(x in line for x in [' = ', '==', '!=', '<=', '>=']):
                    failures.append(f"Line {i}: Missing spaces around assignment operator")
    
    # Check 2: Function parameter spacing
    if profile == "strict":
        if "def " in code:
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if 'def ' in line and ',' in line and ', ' not in line:
                    failures.append(f"Line {i}: Missing space after comma in function parameters")
    
    # Check 3: Missing docstrings
    if profile in ["strict", "balanced"]:
        if "def " in code:
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('def '):
                    # Check if next non-empty line is a docstring
                    next_lines = lines[i:]
                    has_docstring = False
                    for next_line in next_lines:
                        stripped = next_line.strip()
                        if stripped:
                            if stripped.startswith('"""') or stripped.startswith("'''"):
                                has_docstring = True
                            break
                    if not has_docstring:
                        failures.append(f"Line {i}: Function missing docstring")
    
    return {
        "compliant": len(failures) == 0,
        "failures": failures,
        "failure_count": len(failures),
        "profile": profile
    }
