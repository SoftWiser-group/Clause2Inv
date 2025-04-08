import re
import random

def extract_constants_and_variables(code):
    declaration_pattern = re.compile(r'\b(?:unsigned\s+|signed\s+)?(?:long\s+|short\s+)?(?:int|float|double|char)\s+((?:\*?\s*[a-zA-Z_]\w*\s*(?:=\s*[^;,]+)?\s*,\s*)*\*?\s*[a-zA-Z_]\w*\s*(?:=\s*[^;,]+)?\s*)\s*;')
    constant_pattern = re.compile(r'\b\d+\b')
    var_pattern = re.compile(r'[a-zA-Z_]\w*')

    variables = []
    constants = []

    for declaration in declaration_pattern.findall(code):
        for var in var_pattern.findall(declaration):
            variables.append(var)
    constants = constant_pattern.findall(code)

    return variables, constants

def random_var(variables):
    return random.choice(variables)

def random_const(constants):
    return random.choice(constants)

def random_cmp():
    cmp_operators = ['<', '>', '==', '<=', '>=']
    return random.choice(cmp_operators)

def random_op():
    math_operators = ['+', '-', '*', '/', '%']
    return random.choice(math_operators)

def generate_random_expr(variables, constants):
    expr_types = [
        f"( {random_var(variables)} {random_op()} {random_var(variables)} )",
        f"( {random_var(variables)} {random_op()} {random_const(constants)} )",
        f"( {random_const(constants)} {random_op()} {random_var(variables)} )",
        f"( {random_const(constants)} {random_op()} {random_const(constants)} )",
        f"{random_var(variables)}",
        f"{random_const(constants)}"
    ]
    return random.choice(expr_types)

def generate_random_p(variables, constants):
    return f"{random_var(variables)} {random_cmp()} {generate_random_expr(variables, constants)}"
    # return f"{generate_random_expr(variables, constants)} {random_cmp()} {generate_random_expr(variables, constants)}"

def generate_random_C(variables, constants):
    C_types = [
        f"( {generate_random_p(variables, constants)} )",
        f"( {generate_random_p(variables, constants)} || {generate_random_p(variables, constants)} )"
    ]
    return random.choice(C_types)

def generate_random_S(variables, constants):
    S_types = [
        f"( {generate_random_C(variables, constants)} )",
        f"( {generate_random_C(variables, constants)} && {generate_random_C(variables, constants)} )",
        f"( {generate_random_C(variables, constants)} && {generate_random_C(variables, constants)} && {generate_random_C(variables, constants)} )"
    ]
    return random.choice(S_types)

variables = []
constants = []

def random_clause(file_path):
    global variables, constants
    if variables == [] or constants == []:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        variables, constants = extract_constants_and_variables(code)
        print("Constants:", constants)
        print("Variables:", variables)
    random_string = generate_random_p(variables, constants)
    return random_string
