#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

# Import and test directly
import translate
import parso

print("=== QUICK MATH TRANSLATOR TEST ===")

# Test cases
test_cases = [
    "2+3",
    "2*3+5", 
    "2+3*5",
    "1*2*3",
    "2*3/5*7",
    "(2+3)*5",
    "2**3*4"
]

for expr in test_cases:
    try:
        tree = parso.parse(expr)
        result = translate.translate_math_expr(tree.children[0])
        print(f"✓ {expr:12} -> {result}")
    except Exception as e:
        print(f"✗ {expr:12} -> ERROR: {e}")

# Test mixed expression with function call
try:
    result = translate.translate("1+range(n)")
    print(f"✓ {'1+range(n)':12} -> {result}")
except Exception as e:
    print(f"✗ {'1+range(n)':12} -> ERROR: {e}")

print("\n=== FACTORIAL TEST ===")
code = '''def factorial(n):
    def multiply(x, y):
        return x*y
    return reduce(multiply, 1+range(n))'''

try:
    result = translate.translate(code)
    print("✓ Factorial function translated successfully:")
    print(result)
except Exception as e:
    print(f"✗ Factorial translation failed: {e}")