def nmsq(x, precision=1e-10, max_iterations=100):
    """
    Compute square root using Newton's method.
    
    Args:
        x: Number to find square root of
        precision: Convergence tolerance
        max_iterations: Maximum number of iterations
    
    Returns:
        Square root of x
    """
    if x < 0:
        raise ValueError("Cannot compute square root of negative number")
    if x == 0:
        return 0
    
    # Initial guess
    guess = x / 2
    
    for i in range(max_iterations):
        # Newton's method: new_guess = (guess + x/guess) / 2
        new_guess = (guess + x / guess) / 2
        
        # Check for convergence
        if abs(new_guess - guess) < precision:
            return new_guess
        
        guess = new_guess
    
    return guess

def nmsq_while(x, precision=1e-10):
    """
    Compute square root using Newton's method with while loop.
    
    Args:
        x: Number to find square root of
        precision: Convergence tolerance
    
    Returns:
        Square root of x
    """
    if x < 0:
        raise ValueError("Cannot compute square root of negative number")
    if x == 0:
        return 0
    
    # Initial guess
    guess = x / 2
    
    while True:
        # Newton's method: new_guess = (guess + x/guess) / 2
        new_guess = (guess + x / guess) / 2
        
        # Check for convergence
        if abs(new_guess - guess) < precision:
            return new_guess
        
        guess = new_guess

# Test the function
if __name__ == "__main__":
    print(f"nmsq(4) = {nmsq(4)}")
    print(f"nmsq(9) = {nmsq(9)}")
    print(f"nmsq(16) = {nmsq(16)}")
    print(f"nmsq(2) = {nmsq(2)}")
    print(f"nmsq(10) = {nmsq(10)}")

    # Compare with built-in sqrt
    import math
    print(f"Built-in sqrt(10) = {math.sqrt(10)}")
    print(f"Difference: {abs(nmsq(10) - math.sqrt(10))}")