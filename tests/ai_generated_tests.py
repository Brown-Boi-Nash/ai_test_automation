import pytest

def divide(a, b):
    """ This function divides two numbers. If b is zero, it raises an exception. """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide():
    # Test normal division
    assert divide(10, 2) == 5
    
    # Test division by zero
    with pytest.raises(ValueError):
        divide(10, 0)
    
    # Test with non-numeric inputs
    with pytest.raises(TypeError):
        divide('10', 2)
    
    # Test with negative numbers
    assert divide(-10, -2) == 5
    
    # Test with floating point numbers
    assert divide(10.5, 2) == 5.25

# Run the test case
if __name__ == "__main__":
    pytest.main()