"""Test function - passes all gates."""

def test(n: int) -> bool:
    """Test if n is positive.
    
    Args:
        n: Integer input
        
    Returns:
        True if n > 0
    """
    return n > 0

# Example usage
assert test(5)  # True
assert not test(-1)  # False
