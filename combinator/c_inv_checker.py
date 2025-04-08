import z3
import tokenize
import io
import logging
from z3 import *
import re
import random

p = {}
p["%"] = 4
p["*"] = 4
p["/"] = 4
p["+"] = 3
p["-"] = 3
p[">="] = 2
p[">"] = 2
p["=="] = 2
p["<="] = 2
p["<"] = 2
p["!="] = 2
p["and"] = 1
p['or'] = 1
p["("] = 0
p[")"] = 0

# def condense(inv_tokens):
#     op_list = ["+", "-", "*", "/", "%", "<", "<=", ">", ">=", "==", "!=", "and", "or"]
#     un_op_list = ["+", "-"]
#     old_list = list(inv_tokens)
#     new_list = list(inv_tokens)
#     while True:
#         for idx in range(len(old_list)):
#             if old_list[idx] in un_op_list:
#                 if idx == 0 or old_list[idx-1] in op_list or old_list[idx-1] == "(":
#                     new_list[idx] = old_list[idx] + old_list[idx+1]
#                     new_list[idx+1:] = old_list[idx+2:]
#                     break
#         if old_list == new_list:
#             break
#         else:
#             old_list = list(new_list)
#     print(old_list)
#     print(new_list)
#     # exit(0)
#     return new_list

# def infix_postfix(infix_token_list):
#     opStack = []
#     postfix = []
#     opStack.append("(")
#     infix_token_list.append(")")

#     for t in infix_token_list:
#         if t not in p:
#             postfix.append(t)
#         elif t == "(":
#             opStack.append(t)
#         elif t == ")":
#             while opStack[-1] != "(":
#                 postfix.append(opStack.pop(-1))
#             opStack.pop(-1)
#         elif t in p:
#             while len(opStack) > 0 and p[opStack[-1]] >= p[t]:
#                 postfix.append(opStack.pop(-1))
#             opStack.append(t)
#     print(postfix)
#     return postfix

def infix_postfix(infix_token_list):
    # print(infix_token_list)
    # exit(0)
    opStack = []
    postfix = []

    for t in infix_token_list:
        if t not in p and t != "(" and t != ")":
            postfix.append(t)
        elif t == "(":
            opStack.append(t)
        elif t == ")":
            while len(opStack) > 0 and opStack[-1] != "(":
                postfix.append(opStack.pop())
            if len(opStack) > 0 and opStack[-1] == "(":
                opStack.pop()
            else:
                raise ValueError(") matching false")
        elif t in p:
            while len(opStack) > 0 and p[opStack[-1]] >= p[t]:
                postfix.append(opStack.pop())
            opStack.append(t)
        else:
            raise ValueError(f"Undefined: {t}")

    while len(opStack) > 0:
        top = opStack.pop()
        if top == "(":
            raise ValueError("( matching false")
        postfix.append(top)

    # print(postfix)
    # exit(0)

    return postfix

def postfix_prefix(postfix_token_list):
    # print(postfix_token_list)
    # exit(0)
    stack = []
    for t in postfix_token_list:
        if t not in p:
            stack.append(t)
        else:
            sub_stack = []
            sub_stack.append("(")
            sub_stack.append(t)
            op1 = stack.pop(-1)
            op2 = stack.pop(-1)
            sub_stack.append(op2)
            sub_stack.append(op1)
            
            sub_stack.append(")")
            stack.append(sub_stack)
    return stack

def stringify_prefix_stack(prefix_stack):
    s = ""
    for e in prefix_stack:
        if type(e) == list:
            s += stringify_prefix_stack(e)
        else:
            s += e + " "
    return s.strip()

def inv_checker(vc_file: str, inv: str, assignments):
    inv = inv.replace("&&", "and").replace("||", "or")
    b = io.StringIO(inv)
    inv_tokenized = [token for token in tokenize.generate_tokens(b.readline) if token.string != ""]
    
    # var_list = {token for token in inv_tokenized if token.isalpha() and token not in ("and", "or")}
    var_list = {token.string for token in inv_tokenized if token.type == tokenize.NAME and token.string not in ("and", "or")}
    
    var_dict = {var: 1 for var in var_list}
    for v, val in assignments:
        if v in var_dict:
            var_dict[v] = int(val)
    try:
        res = eval(inv, {}, var_dict) # using an empty global context and var_dict as local context
        return res
    except:
        return False

def parse_expression(expr):
    stack = []
    i = 0
    while i < len(expr):
        if expr[i] == '(':
            sub_expr, length = parse_expression(expr[i+1:])
            stack.append(f"( {sub_expr} )")
            i += length + 1
        elif expr[i] == ')':
            return process_stack(stack), i + 1
        else:
            stack.append(expr[i])
            i += 1
    return process_stack(stack), i

def process_stack(stack):
    expr = ''.join(stack).strip()

    # if expr.startswith('!='):
    #     left_paren_idx = expr.find('(')
    #     right_expr = expr[left_paren_idx:]
    #     return f"not ( = {right_expr.strip()} )"

    if expr.startswith('!='):
        return f"not ( = {expr[2:].strip()} )"
        # print("expr", expr)
        # if expr.count('(') > 0:
        #     left_paren_idx = expr.find('(')
        #     right_expr = expr[left_paren_idx:]
        #     return f"not ( = {right_expr.strip()} )"
        # else:
        #     parts = expr.split()
        #     # print("parts", parts)
        #     return f"not ( = {parts[1]} {parts[2]} )"

    return expr

def inv_solver(vc_file: str, inv: str):
    print("inv", inv)
    inv = inv.replace("&&", "and", -1)
    inv = inv.replace("||", "or", -1)
    b = io.StringIO(inv)
    t = tokenize.generate_tokens(b.readline)
    tokens = list(t)
    inv_tokenized = []
    # for a in t:
    #     if a.string != "":
    #         inv_tokenized.append(a.string)
    previous_token = None
    # print(tokens)
    # exit(0)
    for index, token in enumerate(tokens):
        if token.string.strip() == "":
            previous_token = None
        if token.string.strip() != "":
            if token.string == "-" and tokens[index + 1].start[1] == token.end[1] and (tokens[index - 1].type != tokenize.NAME or tokens[index - 1].string == "or" or tokens[index - 1].string == "and") :
                previous_token = token
            elif previous_token is not None:
                if token.type == tokenize.NUMBER:
                    inv_tokenized.append(previous_token.string + token.string)
                elif token.type == tokenize.NAME:
                    inv_tokenized.append("(" + previous_token.string + " " + token.string + ")")
                previous_token = None
            else:
                inv_tokenized.append(token.string)
    # print(inv)
    # print(infix_postfix(inv_tokenized))
    # print(postfix_prefix(infix_postfix(inv_tokenized)))
    # inv = stringify_prefix_stack(postfix_prefix(infix_postfix(condense(inv_tokenized))))
    # print(inv_tokenized)
    inv = stringify_prefix_stack(postfix_prefix(infix_postfix(inv_tokenized)))
    # print(inv)
    # exit(0)
    inv = inv.replace("==", "=", -1)
    inv = inv.replace("%", "mod", -1)
    # pattern = r"\(([^()]*)\s*!=\s*([^()]*)\)"
    # replacement = r"( not (\1= \2) )"
    # inv = re.sub(pattern, replacement, inv)
    inv, _ = parse_expression(inv)

    print("inv", inv)
    # exit(0)

    sol = z3.Solver()
    sol.set(auto_config=False)
    res = []

    vc_sections = [""]
    with open(vc_file, 'r') as vc:
        for vc_line in vc.readlines():
            if "SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop" in vc_line:
                vc_sections.append("")
            else:
                vc_sections[-1] += vc_line
    assert len(vc_sections) == 5

    tpl = [vc_sections[0]]

    # vc = []
    # for i in range(2, 5):
    # vc.append(vc_sections[1] + vc_sections[i])
    # vc = random.shuffle(vc)
    # tpl.extend(vc)
    # tpl.append(vc_sections[1] + vc_sections[4])
    # tpl.append(vc_sections[1] + vc_sections[2])
    # tpl.append(vc_sections[1] + vc_sections[3])

    for i in range(2, 5):
        tpl.append(vc_sections[1] + vc_sections[i])
    res = []
    for i in range(3):
        s = tpl[0] + inv + tpl[i+1]
        # print("s", s)
        sol.reset()
        sol.set("timeout", 600000)
        try:
            decl = z3.parse_smt2_string(s)
        except Exception as e:
            print(s)
            raise e
        # print("decl", decl)
        sol.add(decl)
        r = sol.check()
        if z3.sat == r:
            m = sol.model()
            # print("m", m)
            ce = {}
            if i == 0 or i == 2:
                for x in m:
                    v = str(x)
                    pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*_\d+\b'
                    if re.fullmatch(pattern, v):
                        continue
                    # if "_" in v:
                        # continue
                    ce[str(x)] = str(m[x])
            else:
                m1, m2 = {}, {}
                for x in m:
                    v = str(x)
                    const = str(m[x])
                    pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*_\d+\b'
                    if re.fullmatch(pattern, v):
                        continue
                    # if "_" in v:
                    #     continue
                    elif v.endswith("!"):
                        m2[ v[:-1] ] = const
                    else:
                        m1[v] = const
                ce = (m1, m2)
            res.append(ce)
        elif z3.unknown == r:
            if i == 0:
                w = "pre"
            elif i == 1:
                w = "loop"
            elif i == 2:
                w = "post"
            logging.warning("inv- " + inv + " solution unknown in " + w)
            res.append("EXCEPT")
            print("inv", inv)
            raise Exception("SOL UNKNOWN")
        else:
            res.append(None)
    # exit(0)
    return res