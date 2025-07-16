"""
Test suite for mathematical expression translation from Python to q.
"""

import sys
sys.path.insert(0, '.')

import translate
from qmcp.qlib import connect_to_q

# Connect to q
q = connect_to_q(5001)

def test_expression(expr, description="", variables=None):
    """Test a single mathematical expression."""
    try:
        # Parse the expression and translate it
        import parso
        tree = parso.parse(expr)
        expr_node = tree.children[0]
        q_code = translate.translate_math_expr(expr_node)
        
        # For expressions with variables, we can't evaluate in Python
        if variables:
            print(f"✓ {expr}")
            if description:
                print(f"   {description}")
            print(f"   Q code: {q_code}")
            print(f"   (Variable test - translation only)")
            print()
            return True
        else:
            python_result = eval(expr)
            q_result = q(q_code)
            
            match = abs(python_result - q_result) < 1e-10
            status = "✓" if match else "✗"
            
            print(f"{status} {expr}")
            if description:
                print(f"   {description}")
            print(f"   Python: {python_result}")
            print(f"   Q code: {q_code}")
            print(f"   Q result: {q_result}")
            if not match:
                print(f"   ERROR: Results don't match!")
            print()
            
            return match
    except Exception as e:
        print(f"✗ {expr}")
        if description:
            print(f"   {description}")
        print(f"   ERROR: {e}")
        print()
        return False

def run_test_suite():
    """Run comprehensive test suite for mathematical expressions."""
    print("=" * 60)
    print("MATHEMATICAL EXPRESSION TRANSLATOR TEST SUITE")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # Test categories
    test_categories = [
        ("Basic Operations", [
            ("2+3", "Simple addition"),
            ("2-3", "Simple subtraction"), 
            ("2*3", "Simple multiplication"),
            ("2/3", "Simple division"),
            ("2**3", "Simple power"),
        ]),
        
        ("Operator Precedence", [
            ("2+3*5", "Addition and multiplication"),
            ("2*3+5", "Multiplication and addition"),
            ("2+3**2", "Addition and power"),
            ("2**3+4", "Power and addition"),
            ("2*3**2", "Multiplication and power"),
            ("2**3*4", "Power and multiplication"),
        ]),
        
        ("Chained Operations - Same Precedence", [
            ("1+2+3", "Addition chain"),
            ("1-2-3", "Subtraction chain (left-associative)"),
            ("1*2*3", "Multiplication chain"),
            ("1/2/3", "Division chain (left-associative)"),
            ("2**3**2", "Power chain (right-associative)"),
        ]),
        
        ("Chained Operations - Mixed Precedence", [
            ("2+3*5+6", "Addition with multiplication"),
            ("2*3/5*7", "Multiplication and division chain"),
            ("2+3*5-6/2", "Complex mixed operations"),
            ("1+2*3**2", "Addition, multiplication, and power"),
            ("2**3*4+5", "Power, multiplication, and addition"),
        ]),
        
        ("Parentheses", [
            ("(2+3)*5", "Parentheses override precedence"),
            ("2*(3+5)", "Parentheses in right operand"),
            ("(2+3)*(4+5)", "Parentheses in both operands"),
            ("2**(3+2)", "Parentheses with power"),
            ("(2*3)**2", "Parentheses with power base"),
        ]),
        
        ("Complex Expressions", [
            ("2+3*4-5/2", "Four operations"),
            ("(2+3)*4-5**2", "Parentheses and power"),
            ("2**3**2+4*5", "Multiple high precedence operations"),
            ("((2+3)*4)**2", "Nested parentheses"),
            ("2*3+4*5-6/2", "Multiple terms"),
        ]),
        
        ("Edge Cases", [
            ("1", "Single number"),
            ("x", "Single variable", True),
            ("x+y", "Two variables", True),
            ("2*x+3*y", "Variables with coefficients", True),
            ("x**2+y**2", "Variables with powers", True),
        ]),
    ]
    
    for category_name, test_cases in test_categories:
        print(f"\n{category_name}")
        print("-" * len(category_name))
        
        for test_case in test_cases:
            if len(test_case) == 2:
                expr, description = test_case
                variables = None
            else:
                expr, description, variables = test_case
            
            total_tests += 1
            if test_expression(expr, description, variables):
                passed_tests += 1
    
    # Summary
    print("=" * 60)
    print(f"TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    run_test_suite()