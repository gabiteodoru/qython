"""
Clean implementation of mathematical expression translation from Python to q.
Handles only +, -, *, /, and parentheses using proper tree-walking approach.
"""

import parso

# Operator precedence levels (higher number = higher precedence)
PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '**': 3,
}

# Python operators to q operators
PYTHON_TO_Q = {
    '+': '+',
    '-': '-', 
    '*': '*',
    '/': '%',
    '**': ' xexp ',
}

def get_operator_info(node):
    """Extract operator info from a binary expression node."""
    if node.type == 'arith_expr':
        # Find the main operator (should be + or -)
        for child in node.children:
            if child.type == 'operator' and child.value in ['+', '-']:
                return child.value, PRECEDENCE[child.value]
    elif node.type == 'term':
        # Find the main operator (should be * or /)
        for child in node.children:
            if child.type == 'operator' and child.value in ['*', '/', '**']:
                return child.value, PRECEDENCE[child.value]
    elif node.type == 'power':
        # Find the main operator (should be **)
        for child in node.children:
            if child.type == 'operator' and child.value == '**':
                return child.value, PRECEDENCE[child.value]
    return None, 0

def translate_expr(node, parent_op=None, parent_prec=0, is_left_child=False):
    """
    Translate a mathematical expression node to q code.
    
    Args:
        node: The AST node to translate
        parent_op: The parent operator (for precedence decisions)
        parent_prec: The parent precedence level
        is_left_child: Whether this node is the left child of its parent
    """
    if node.type == 'number':
        return node.value
    elif node.type == 'name':
        return node.value
    elif node.type == 'atom':
        # Handle parenthesized expressions
        if len(node.children) == 3 and node.children[0].value == '(':
            # (expr) - translate the inner expression and preserve parentheses
            inner_result = translate_expr(node.children[1])
            return f"({inner_result})"
        else:
            # Other atoms, just translate first child
            return translate_expr(node.children[0], parent_op, parent_prec, is_left_child)
    elif node.type in ['arith_expr', 'term', 'power']:
        return translate_binary_expr(node, parent_op, parent_prec, is_left_child)
    else:
        # Fallback for other node types
        if hasattr(node, 'children') and len(node.children) == 1:
            return translate_expr(node.children[0], parent_op, parent_prec, is_left_child)
        else:
            return str(node)

def translate_binary_expr(node, parent_op=None, parent_prec=0, is_left_child=False):
    """
    Translate a binary expression (arith_expr or term) to q code.
    Handles chained operations like a+b+c or a*b/c.
    """
    children = node.children
    
    if len(children) == 1:
        return translate_expr(children[0], parent_op, parent_prec, is_left_child)
    
    # Get this node's operator and precedence
    my_op, my_prec = get_operator_info(node)
    
    # Handle chained operations: a op b op c op d...
    # We need to build left-to-right for correct evaluation
    result = translate_expr(children[0], my_op, my_prec, True)
    
    # Process each operator-operand pair
    for i in range(1, len(children), 2):
        if i + 1 < len(children):
            op = children[i].value
            right_operand = children[i + 1]
            
            # Translate the right operand
            right_result = translate_expr(right_operand, op, PRECEDENCE[op], False)
            
            # Convert operator to q syntax
            q_op = PYTHON_TO_Q[op]
            
            # For chained operations, we need to group left-to-right
            # But only add parentheses if we have more operations after this
            if i + 2 < len(children):  # More operations follow
                result = f"({result}{q_op}{right_result})"
            else:  # Last operation
                result = f"{result}{q_op}{right_result}"
    
    # Decide if this entire expression needs parentheses
    needs_parens = False
    
    if parent_op is not None:
        # We need parentheses if:
        # 1. Parent has lower precedence and we're the left child
        #    (higher precedence on left needs parens in right-associative q)
        # 2. Same precedence but we're right child (q is right-associative)
        if parent_prec < my_prec and is_left_child:
            needs_parens = True
        elif parent_prec == my_prec and not is_left_child:
            # Right child with same precedence needs parens in right-associative language
            needs_parens = True
    
    if needs_parens:
        return f"({result})"
    else:
        return result

def translate_math_expr(code):
    """
    Translate a mathematical expression from Python to q.
    
    Args:
        code: String containing Python mathematical expression
        
    Returns:
        String containing q code
    """
    # Parse using standard Python grammar
    tree = parso.parse(code)
    
    # Find the expression (skip module wrapper)
    expr_node = tree.children[0]
    
    # Translate the expression
    return translate_expr(expr_node)

def test_translation(expr):
    """Test a translation and compare results."""
    try:
        q_code = translate_math_expr(expr)
        python_result = eval(expr)
        
        print(f"Python: {expr} = {python_result}")
        print(f"Q code: {q_code}")
        
        # Test in q (assuming q function is available)
        try:
            import sys
            sys.path.append('..')
            # This would need to be imported from your q connection
            # q_result = q(q_code)
            # print(f"Q result: {q_result}")
            # print(f"Match: {python_result == q_result}")
        except:
            print("(Q evaluation not available)")
        
        print()
        return q_code
    except Exception as e:
        print(f"Error translating {expr}: {e}")
        return None

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "2+3",
        "2*3", 
        "2+3*5",
        "2*3+5",
        "2+3*5+6",
        "2*3/5*7",
        "1+2-3",
        "1*2*3",
        "1/2/3",
        "(2+3)*5",
        "2*(3+5)",
        "2+3*5-6/2",
        "2**3",
        "2**3**2",
        "2*3**2",
        "2**3*4",
        "2+3**2",
        "2**3+4",
    ]
    
    for expr in test_cases:
        test_translation(expr)