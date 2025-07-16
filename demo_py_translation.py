import parso
from translate import *

# Read the nmsq.py file
with open('nmsq.py', 'r') as f:
    code = f.read()

# Load custom grammar with converge support
custom_grammar = parso.load_grammar(path='custom_grammar.txt')

# Parse the AST using custom grammar
tree = custom_grammar.parse(code)

# Extract and translate functions
def translate_function(func_name=None):
    core_func = extract_function_core(tree, func_name)
    
    if core_func:
        # Get function name for display
        display_name = None
        for child in core_func.children:
            if child.type == 'name':
                display_name = child.value
                break
        
        print(f"Function: {display_name}")
        print("Core function structure:")
        print(f"  Type: {core_func.type}")
        print(f"  Children: {len(core_func.children)} nodes")
        print("\nTranslated to q:")
        print(translate_to_q(core_func))
        return core_func
    else:
        print(f"No function found{' with name ' + func_name if func_name else ''}")
        return None

# Default: translate first function found
core_func = translate_function()