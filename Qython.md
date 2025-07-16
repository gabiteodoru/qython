# Qython Language Specification

Qython is a Python-like language that compiles to q/kdb+ code. It maintains Python's familiar syntax while adding specialized constructs for iterative algorithms and mathematical computations.

## Supported Python Features

Qython supports most core Python constructs:

- **Functions**: `def function_name(param1, param2):`
- **Variables**: Standard assignment with `=`
- **Arithmetic**: `+`, `-`, `*`, `/`, `**` (power)
- **Comparisons**: `<`, `>`, `<=`, `>=`, `==`, `!=`
- **Conditionals**: `if condition:` and `if condition: ... if condition:`
- **Loops**: `while condition:`
- **Lists**: `[a, b, c]`
- **Function calls**: `function(arg1, arg2)`
- **Return statements**: `return value`

## Removed Python Features

The following Python constructs are **not supported**:

- `for` loops
- `else:` clauses (with colon - ternary `else` is fine)
- `elif` statements
- `break` and `continue` statements
- **Tuples**: Use lists `[a, b, c]` instead of tuples `(a, b, c)`
- **Tuple assignment**: No support for `a, b = 3, 4` - use explicit assignment instead

## Qython Extensions

### 1. `do n times:` Control Structure

Qython adds a `do n times:` construct for simple iteration:

```python
do 10 times:
    print("Hello")
```

This is equivalent to Python's `for _ in range(10):` but more concise.

### 2. `converge()` Function

The `converge()` function repeatedly applies a step function until convergence:

```python
final_result = converge(step_function, starting_from=initial_value)
```

**Parameters:**
- `step_function`: A function that takes the current state and returns the next state
- `starting_from`: The initial value to start the iteration

**Behavior:**
- Applies `step_function` repeatedly until the result converges
- Uses built-in tolerance to determine convergence
- Returns the final converged value

### 3. `reduce()` Function

The `reduce()` function applies a binary function cumulatively to items in a list:

```python
result = reduce(binary_function, iterable)
```

**Parameters:**
- `binary_function`: A function that takes two arguments and returns one result
- `iterable`: A list of values to reduce

**Behavior:**
- Applies `binary_function` cumulatively from left to right
- Equivalent to `binary_function(binary_function(list[0], list[1]), list[2])...`
- Returns the final accumulated result

**Example:**
```python
def add(x, y):
    return x + y

numbers = [1, 2, 3, 4, 5]
total = reduce(add, numbers)  # Results in 15
```

### 4. `range()` Function

The `range()` function generates sequences of integers:

```python
numbers = range(5)  # Equivalent to [0, 1, 2, 3, 4]
```

**Parameters:**
- `n`: The upper bound (exclusive) - generates integers from 0 to n-1

**Behavior:**
- Generates a sequence of integers starting from 0
- Useful for creating numeric sequences and iteration bounds
- Translates directly to q's `til` function

## Example

```python
def golden_section_search(f, a, b):
    phi = (1 + 5**0.5) / 2
    resphi = 2 - phi

    x1 = a + resphi * (b - a)
    x2 = b - resphi * (b - a)
    f1 = f(x1)
    f2 = f(x2)

    def step(state):
        # Extract state values
        state_a = state[0]
        state_b = state[1]
        state_x1 = state[2]
        state_x2 = state[3]
        state_f1 = state[4]
        state_f2 = state[5]
        
        if state_f1 > state_f2:
            new_a = state_x1
            new_x1 = state_x2
            new_f1 = state_f2
            new_x2 = state_b - resphi * (state_b - new_a)
            new_f2 = f(new_x2)
            new_b = state_b
        
        if state_f1 <= state_f2:
            new_b = state_x2
            new_x2 = state_x1
            new_f2 = state_f1
            new_x1 = state_a + resphi * (new_b - state_a)
            new_f1 = f(new_x1)
            new_a = state_a
        
        return [new_a, new_b, new_x1, new_x2, new_f1, new_f2]

    initial_state = [a, b, x1, x2, f1, f2]
    final_state = converge(step, starting_from=initial_state)
    result_a = final_state[0]
    result_b = final_state[1]
    return (result_a + result_b) / 2
```

## Translation to q/kdb+

Qython compiles to q/kdb+ code with the following mappings:

- **Functions**: `def name(args):` → `name:{[args] ...}`
- **Power operator**: `**` → `xexp`
- **Division**: `/` → `%`
- **Assignment**: `=` → `:`
- **Lists**: `[a, b, c]` → `(a; b; c)`
- **Function calls**: `func(args)` → `func[args]`
- **Converge**: `converge(step, starting_from=init)` → `step/[init]`
- **Reduce**: `reduce(func, iterable)` → `func/[iterable]`
- **Range**: `range(n)` → `til[n]`

The language is designed to make mathematical and iterative algorithms more readable while maintaining the performance characteristics of q/kdb+.