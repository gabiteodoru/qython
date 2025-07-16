import parso

# Read the test file with converge syntax
with open('test_converge.py', 'r') as f:
    code = f.read()

# Load custom grammar with converge support
try:
    custom_grammar = parso.load_grammar(path='custom_grammar.txt')
    print("✓ Custom grammar loaded successfully")
except Exception as e:
    print(f"✗ Error loading custom grammar: {e}")
    exit(1)

# Parse the AST using custom grammar
try:
    tree = custom_grammar.parse(code)
    print("✓ Code parsed successfully")
except Exception as e:
    print(f"✗ Error parsing code: {e}")
    exit(1)

# Load the translator functions (but skip the file loading part)
with open('translate.py', 'r') as f:
    translator_code = f.read()

# Remove the file loading lines from translate.py
lines = translator_code.split('\n')
filtered_lines = []
skip_next = False
for line in lines:
    if 'with open(' in line and 'nmsq.py' in line:
        skip_next = True
        continue
    elif skip_next and 'code = f.read()' in line:
        skip_next = False
        continue
    elif 'custom_grammar = parso.load_grammar' in line:
        continue  # Skip this line, we already loaded it
    elif 'tree = custom_grammar.parse(code)' in line:
        continue  # Skip this line, we already parsed it
    filtered_lines.append(line)

exec('\n'.join(filtered_lines))

# Find and translate the converge function
def find_converge_function(tree):
    """Find the function with converge statement"""
    funcdefs = find_nodes_by_type(tree, 'funcdef')
    
    for funcdef in funcdefs:
        # Check if this function contains a converge statement
        converge_stmts = find_nodes_by_type(funcdef, 'converge_stmt')
        if converge_stmts:
            return funcdef
    return None

converge_func = find_converge_function(tree)
if converge_func:
    print("\n✓ Found function with converge statement")
    translated = translate_to_q(converge_func)
    print(f"\nTranslated q code:\n{translated}")
else:
    print("\n✗ No function with converge statement found")

# Also check if converge statements are parsed correctly
converge_stmts = find_nodes_by_type(tree, 'converge_stmt')
if converge_stmts:
    print(f"\n✓ Found {len(converge_stmts)} converge statement(s)")
    for i, stmt in enumerate(converge_stmts):
        print(f"\nConverge statement {i+1}:")
        print(f"  Type: {stmt.type}")
        print(f"  Children: {[child.type for child in stmt.children]}")
        translated = translate_converge_stmt(stmt)
        print(f"  Translated: {translated}")
else:
    print("\n✗ No converge statements found")