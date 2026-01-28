"""Safe division."""
def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
print(safe_divide(10, 2))
