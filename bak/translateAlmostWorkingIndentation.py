import parso

def format_q_args(args):
    """Format a list of arguments/parameters for q syntax using semicolons"""
    return ';'.join(args)

def translate_suite(suite_node, indent_level=0):
    """Translate a suite (block of code) with proper semicolons and whitespace"""
    body_parts = []
    for stmt in suite_node.children:
        translated = translate_to_q(stmt, indent_level)
        if translated:
            body_parts.append(translated)
    return ''.join(body_parts)

def format_block_with_proper_closing(suite_node, indent_level, open_bracket, close_bracket):
    """Format a code block with proper indentation and closing bracket"""
    body_parts = []
    for stmt in suite_node.children:
        translated = translate_to_q(stmt, indent_level + 1)
        if translated:
            if stmt.type not in ['newline', 'indent', 'dedent'] and translated.strip():
                body_parts.append(translated)
            else:
                body_parts.append(translated)
    
    # Add semicolons after statements (except the last one)
    processed_parts = []
    stmt_parts = [p for p in body_parts if p.strip()]  # Get all statements
    
    for i, part in enumerate(body_parts):
        if part.strip():  # This is a statement
            # Find which statement number this is
            stmt_number = len([p for p in body_parts[:i+1] if p.strip()])
            is_last_stmt = stmt_number == len(stmt_parts)
            
            # Check if next part is a newline
            if i + 1 < len(body_parts) and body_parts[i + 1].strip() == '':
                if is_last_stmt:
                    processed_parts.append(part)  # No semicolon for last statement
                else:
                    processed_parts.append(part + ';')
            else:
                processed_parts.append(part)
        else:  # This is whitespace/newline
            processed_parts.append(part)
    
    body = ''.join(processed_parts)
    closing_indent = '    ' * (indent_level + 1)  # Same as body indent level
    return f"{body}\n{closing_indent}{close_bracket}"

def translate_statement_with_suite(node, keyword, template, indent_level=0):
    """Generic handler for statements that have a condition/expr and a suite"""
    condition = None
    suite_node = None
    
    for child in node.children:
        if child.type == 'keyword' and child.value == keyword:
            continue
        elif child.type == 'operator' and child.value == ':':
            continue
        elif child.type == 'suite':
            suite_node = child
        elif condition is None:
            condition = translate_to_q(child, indent_level)
    
    if suite_node:
        body = format_block_with_proper_closing(suite_node, indent_level, '[', '];')
        indent = '    ' * indent_level
        
        if keyword == 'if':
            return f"{indent}if[{condition}; {body}"
        elif keyword == 'while':
            return f"{indent}while[{condition}; {body}"
        else:
            return indent + template.format(condition=condition, body=body)
    
    indent = '    ' * indent_level
    return indent + template.format(condition=condition, body="")

def analyze_closure_variables(suite_node, convergence_var):
    """
    Analyze a suite (block of code) to find variables that need to be captured from closure.
    
    Args:
        suite_node: The AST suite node containing the converge block
        convergence_var: The variable we're converging on (should be excluded)
        
    Returns:
        Set of variable names that need to be captured from the outer scope
    """
    referenced_vars = set()
    assigned_vars = set()
    
    def collect_variables(node):
        if hasattr(node, 'type'):
            if node.type == 'name':
                # This is a variable reference
                referenced_vars.add(node.value)
            elif node.type == 'expr_stmt' and hasattr(node, 'children'):
                # Check for assignments: var = expr
                if (len(node.children) >= 3 and 
                    node.children[1].type == 'operator' and 
                    node.children[1].value == '=' and
                    node.children[0].type == 'name'):
                    assigned_vars.add(node.children[0].value)
        
        # Recursively process children
        if hasattr(node, 'children'):
            for child in node.children:
                collect_variables(child)
    
    # Analyze the suite
    collect_variables(suite_node)
    
    # Remove the convergence variable and any locally assigned variables
    closure_vars = referenced_vars - assigned_vars - {convergence_var}
    
    return closure_vars

def translate_file(filename):
    """
    Translate a Qython (.qy) file to q code.
    
    Args:
        filename: Path to the .qy file to translate
        
    Returns:
        String containing the translated q code
    """
    # Read the file
    with open(filename, 'r') as f:
        code = f.read()
    
    # Load custom grammar with extended syntax support
    import os
    grammar_path = os.path.join(os.getcwd(), 'custom_grammar.txt')
    custom_grammar = parso.load_grammar(path=grammar_path)
    
    # Parse the AST using custom grammar
    tree = custom_grammar.parse(code)
    
    # Find only top-level functions (direct children of file_input)
    translated_functions = []
    
    for child in tree.children:
        if hasattr(child, 'type') and child.type == 'funcdef':
            translated = translate_to_q(child, 0)  # Start with indent level 0
            if translated and translated.strip():
                translated_functions.append(translated)
    
    # Join all translated functions
    return '\n\n'.join(translated_functions)

# Arithmetic expression translator for q
def getQOp(op_value):
    return {'+': '+', '*': '*', '-': '-', '/': '%'}[op_value]

def hasOperators(node):
    return hasattr(node, 'type') and 'expr' in node.type and any(
        child.type == 'operator' and child.value in ['+', '*', '-', '/']
        for child in getattr(node, 'children', [])
    )

def toQCode(node):
    if hasattr(node, 'type'):
        if node.type == 'number':
            return node.value
        elif node.type == 'string':
            return node.value
        elif node.type == 'name':
            return node.value
        elif node.type == 'atom' and hasattr(node, 'children'):
            # Handle parenthesized expressions: (expr)
            if len(node.children) == 3 and node.children[0].value == '(' and node.children[2].value == ')':
                # Return the inner expression with parentheses
                inner = toQCode(node.children[1])
                return f"({inner})"
            elif len(node.children) == 1:
                return toQCode(node.children[0])
            else:
                # Other atom types, process all children
                return ''.join(toQCode(child) for child in node.children if child.type != 'operator' or child.value not in ['(', ')'])
        elif node.type in ['term', 'arith_expr'] and hasattr(node, 'children'):
            # Handle binary operations
            children = node.children
            if len(children) == 1:
                return toQCode(children[0])
            elif len(children) >= 3:
                left = toQCode(children[0])
                op = children[1].value if children[1].type == 'operator' else '?'
                right = toQCode(children[2])
                
                if op in ['+', '*', '-', '/']:
                    q_op = getQOp(op)
                    # Check if left side needs parentheses
                    if hasOperators(children[0]):
                        left = f"({left})"
                    return f"{left}{q_op}{right}"
                else:
                    return f"{left}{op}{right}"
            else:
                return toQCode(children[0]) if children else str(node)
        elif node.type == 'operator':
            return node.value
        elif hasattr(node, 'children') and node.children:
            # For other node types with children, try to process them
            if len(node.children) == 1:
                return toQCode(node.children[0])
            else:
                parts = []
                for child in node.children:
                    part = toQCode(child)
                    if part:
                        parts.append(part)
                return ''.join(parts)
    
    return str(node)

# Find the function definition and extract it without docstring and defaults
def find_nodes_by_type(node, target_type, results=None):
    if results is None:
        results = []
    
    if hasattr(node, 'type') and node.type == target_type:
        results.append(node)
    
    if hasattr(node, 'children'):
        for child in node.children:
            find_nodes_by_type(child, target_type, results)
    
    return results

def extract_function_core(tree, func_name=None):
    # Find all function definitions
    funcdefs = find_nodes_by_type(tree, 'funcdef')
    
    for funcdef in funcdefs:
        # Get function name
        current_func_name = None
        for child in funcdef.children:
            if hasattr(child, 'type') and child.type == 'name':
                current_func_name = child.value
                break
        
        # If func_name is specified, only return that function
        if func_name and current_func_name != func_name:
            continue
            
        return funcdef
    
    return None

# Individual translator functions for each node type
def translate_funcdef(node, indent_level=0):
    """Function definition: nmsq:{[x;precision;max_iterations] ...}"""
    func_name = None
    params = []
    suite = None
    
    for child in node.children:
        if child.type == 'name':
            func_name = child.value
        elif child.type == 'parameters':
            # Extract parameter names
            for param_child in child.children:
                if param_child.type == 'param':
                    for param_part in param_child.children:
                        if param_part.type == 'name':
                            params.append(param_part.value)
        elif child.type == 'suite':
            suite = child
    
    if func_name and suite:
        args = format_q_args(params)
        
        # Skip docstring if present
        filtered_suite = []
        first_real_stmt = True
        for stmt in suite.children:
            if first_real_stmt and stmt.type == 'simple_stmt':
                # Check if this simple_stmt contains just a string (docstring)
                if (hasattr(stmt, 'children') and len(stmt.children) >= 1 and 
                    stmt.children[0].type == 'string'):
                    first_real_stmt = False
                    continue
            first_real_stmt = False
            filtered_suite.append(stmt)
        
        # Create a mock suite node with filtered children
        class MockSuite:
            def __init__(self, children):
                self.children = children
                self.type = 'suite'
        
        mock_suite = MockSuite(filtered_suite)
        body = format_block_with_proper_closing(mock_suite, indent_level, '{', '}')
        indent = '    ' * indent_level
        return f"{indent}{func_name}:{{[{args}] {body}"

def translate_if_stmt(node, indent_level=0):
    """if condition: body -> if[condition; body]"""
    return translate_statement_with_suite(node, 'if', 'if[{condition}; {body}]', indent_level)

def translate_while_stmt(node, indent_level=0):
    """while condition: body -> while[condition; body]"""
    return translate_statement_with_suite(node, 'while', 'while[{condition}; {body}]', indent_level)

def translate_converge_call(args):
    """Handle converge(step_func, starting_from=initial_value) -> step_func/[initial_value]"""
    if len(args) != 2:
        return "// Error: converge() requires exactly 2 arguments: step_func and starting_from"
    
    step_func = args[0]
    starting_from = args[1]
    
    # Extract the starting_from value if it's a keyword argument
    if '=' in starting_from:
        # Handle starting_from=value syntax
        parts = starting_from.split('=', 1)
        if parts[0].strip() == 'starting_from':
            starting_from = parts[1].strip()
    
    # Generate q code: step_func/[starting_from]
    return f"{step_func}/[{starting_from}]"

def translate_do_stmt(node, indent_level=0):
    """do <expr> times: body -> do[expr; body]"""
    repetitions = None
    body = ""
    
    for child in node.children:
        if child.type == 'keyword' and child.value in ['do', 'times']:
            continue
        elif child.type == 'operator' and child.value == ':':
            continue
        elif child.type == 'suite':
            body = translate_suite(child, indent_level + 1)
        elif repetitions is None:
            repetitions = translate_to_q(child, indent_level)
    
    if not repetitions:
        return "// Error: do statement missing repetition count"
    
    return f"do[{repetitions}; {body}]"

def translate_simple_stmt(node, indent_level=0):
    """Handle simple statements that contain other statements and their newlines"""
    if hasattr(node, 'children') and len(node.children) > 0:
        parts = []
        for child in node.children:
            translated = translate_to_q(child, indent_level)
            if translated:
                # Collect non-whitespace statements
                if child.type not in ['newline', 'indent', 'dedent'] and translated.strip():
                    parts.append(translated)
                # Keep whitespace as-is
                else:
                    parts.append(translated)
        
        # Process statements and add semicolons before newlines
        processed_parts = []
        indent = '    ' * indent_level
        for i, part in enumerate(parts):
            if part.strip():  # This is a statement
                # Check if next part is a newline
                if i + 1 < len(parts) and parts[i + 1].strip() == '':
                    processed_parts.append(indent + part + ';')
                else:
                    processed_parts.append(indent + part)
            else:  # This is whitespace/newline
                processed_parts.append(part)
        return ''.join(processed_parts)
    return ""

def translate_expr_stmt(node):
    """Handle expression statements (assignments, etc.)"""
    if hasattr(node, 'children') and len(node.children) >= 3:
        # Look for assignment pattern: name = expr
        if node.children[1].type == 'operator' and node.children[1].value == '=':
            target = translate_to_q(node.children[0])
            value = translate_to_q(node.children[2])
            return f"{target}:{value}"
    return translate_to_q(node.children[0]) if node.children else ""

def translate_return_stmt(node):
    """return expr -> :expr"""
    if hasattr(node, 'children') and len(node.children) > 1:
        return f":{translate_to_q(node.children[1])}"
    else:
        return ":"

def translate_name(node):
    """Variable names"""
    return node.value

def translate_number(node):
    """Numbers"""
    return node.value

def translate_string(node):
    """Strings"""
    return node.value

def translate_keyword(node):
    """Keywords like True, False"""
    if node.value == 'True':
        return '1b'
    elif node.value == 'False':
        return '0b'
    else:
        return node.value

def translate_comparison(node):
    """Handle comparison expressions"""
    if hasattr(node, 'children') and len(node.children) >= 3:
        left = translate_to_q(node.children[0])
        op = node.children[1].value
        right = translate_to_q(node.children[2])
        
        if op == '<':
            return f"{left}<{right}"
        elif op == '==':
            return f"{left}={right}"
        else:
            return f"{left}{op}{right}"
    return str(node)

def translate_raise_stmt(node):
    """raise ValueError("msg") -> `$"msg" """
    if hasattr(node, 'children') and len(node.children) > 1:
        # Look for the error message
        for child in node.children:
            if child.type == 'atom' or child.type == 'power':
                # This is a function call like ValueError("message")
                # Extract the string argument
                for grandchild in child.children:
                    if hasattr(grandchild, 'children'):
                        for ggchild in grandchild.children:
                            if ggchild.type == 'string':
                                return f"`${ggchild.value}"
    return '`$"Error"'

def translate_term(node):
    """Handle arithmetic terms like x/2, (guess + x/guess) / 2"""
    return toQCode(node)

def translate_power(node):
    """Handle power expressions and function calls"""
    if hasattr(node, 'children') and len(node.children) > 0:
        base = translate_to_q(node.children[0])
        if len(node.children) > 1 and node.children[1].type == 'trailer':
            # This might be a function call like abs(...) or converge(...)
            trailer = node.children[1]
            if hasattr(trailer, 'children') and len(trailer.children) >= 2:
                if trailer.children[0].value == '(':
                    # Function call: base(args) -> base[args]
                    args = []
                    for child in trailer.children:
                        if child.type == 'arglist':
                            for arg_child in child.children:
                                if arg_child.type != 'operator' or arg_child.value != ',':
                                    args.append(translate_to_q(arg_child))
                        elif child.type not in ['operator'] or child.value not in ['(', ')']:
                            translated = translate_to_q(child)
                            if translated:
                                args.append(translated)
                    # Filter out empty args
                    args = [arg for arg in args if arg and arg.strip()]
                    
                    # Special handling for converge function
                    if base == 'converge':
                        return translate_converge_call(args)
                    
                    return f"{base}[{format_q_args(args)}]"
        return base
    return str(node)

def translate_atom_expr(node):
    """Handle function calls like abs(x)"""
    if hasattr(node, 'children') and len(node.children) >= 2:
        # Should have name + trailer for function calls
        func_name = translate_to_q(node.children[0])
        
        for child in node.children[1:]:
            if child.type == 'trailer':
                # Function call trailer: (args)
                if hasattr(child, 'children') and len(child.children) >= 2:
                    if child.children[0].value == '(':
                        # Extract arguments
                        args = []
                        for trailer_child in child.children:
                            if trailer_child.type not in ['operator']:
                                args.append(translate_to_q(trailer_child))
                        # Filter out empty args
                        args = [arg for arg in args if arg and arg.strip()]
                        return f"{func_name}[{format_q_args(args)}]"
        
        # If not a function call, just return the first child
        return func_name
    
    return str(node)

def translate_atom(node):
    """Handle atomic expressions including lists [a, b, ...] -> (a; b; ...)"""
    if hasattr(node, 'children') and len(node.children) > 0:
        # Check if this is a list: [...]
        if (len(node.children) >= 3 and 
            node.children[0].type == 'operator' and node.children[0].value == '[' and
            node.children[-1].type == 'operator' and node.children[-1].value == ']'):
            
            # Extract list elements
            elements = []
            for child in node.children[1:-1]:  # Skip [ and ]
                if child.type == 'testlist_comp':
                    # Handle comma-separated list elements
                    for elem in child.children:
                        if elem.type != 'operator' or elem.value != ',':
                            elements.append(translate_to_q(elem))
                elif child.type not in ['operator']:
                    elements.append(translate_to_q(child))
            
            # Return q list format: (a; b; c)
            return f"({';'.join(elements)})"
        
        return translate_to_q(node.children[0])
    return str(node)

# Main translator function - now just a dispatcher
def translate_to_q(node, indent_level=0):
    if not hasattr(node, 'type'):
        return str(node)
    
    # Handle whitespace/formatting nodes
    if node.type == 'newline':
        return '\n'
    elif node.type == 'indent':
        return '  '  # 2 spaces for indent
    elif node.type == 'dedent':
        return ''
        
    translators = {
        'funcdef': translate_funcdef,
        'if_stmt': translate_if_stmt,
        'while_stmt': translate_while_stmt,
        'do_stmt': translate_do_stmt,
        'simple_stmt': translate_simple_stmt,
        'expr_stmt': translate_expr_stmt,
        'return_stmt': translate_return_stmt,
        'raise_stmt': translate_raise_stmt,
        'name': translate_name,
        'number': translate_number,
        'string': translate_string,
        'keyword': translate_keyword,
        'comparison': translate_comparison,
        'term': translate_term,
        'power': translate_power,
        'atom_expr': translate_atom_expr,
        'atom': translate_atom,
    }
    
    if node.type in translators:
        if node.type in ['funcdef', 'if_stmt', 'while_stmt', 'do_stmt', 'simple_stmt']:
            return translators[node.type](node, indent_level)
        else:
            return translators[node.type](node)
    elif 'expr' in node.type:
        return toQCode(node)
    else:
        return f"// Unsupported: {node.type}"

