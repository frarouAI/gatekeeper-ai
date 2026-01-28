def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    if a is None or b is None:
        raise ValueError("Inputs must not be None")
    return a + b
