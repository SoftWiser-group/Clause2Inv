from cmd_args import cmd_args
import random
import z3
import numpy as np
from tqdm import tqdm
import importlib
from inv_gen import random_clause
import sys
import json

sys.path.append("../generator")
from utils import setup_logger
from re_clause_generater import Re_Clause_generater
from llm_factory import LLMConfig,LLMFactory,SupportLLM

checker_module = importlib.import_module(cmd_args.inv_checker)

code_ce_dict = {}
ICE_KEYS = ("T:", "I:", "F:")

class CounterExample(object):
    def __init__(self, src = None, ice = None):
        pass
    
    def __repr__(self):
        return self.ice_str

    def to_ice_str(self):
        res = None
        if self.kind == "pre":
            res = "T:{" + ",".join( ["%s=%s" % (k,self.config[k]) for k in sorted(self.config.keys()) if k not in ["inv-f", "pre-f", "post-f", "trans-f"] ] ) + "}"
        elif self.kind == "post":
            res = "F:{" + ",".join( ["%s=%s" % (k,self.config[k]) for k in sorted(self.config.keys()) if k not in ["inv-f", "pre-f", "post-f", "trans-f"] ] ) + "}"
        elif self.kind == "loop":
            res = "I:{" + ",".join( ["%s=%s" % (k,self.config[0][k]) for k in sorted(self.config[0].keys()) if k not in ["inv-f", "pre-f", "post-f", "trans-f"] ] ) + ";"
            res += ",".join( ["%s=%s" % (k,self.config[1][k]) for k in sorted(self.config[1].keys()) ] ) +"}"
        return res

    def helper(self, dat, expr_root):
        assignments = []
        for var in dat:
            assignments.append((var, dat[var]))
        r = checker_module.inv_checker(cmd_args.input_vcs, str(expr_root), assignments)
        return r

    def check(self, expr_root):
        if self.kind == "pre":
            # we should get a SAT result for positive example
            if self.helper(self.config, expr_root):
                return "good"
            else:
                return "bad"

        elif self.kind == "post":
            # we should get an UNSAT result for negative example
            if not self.helper(self.config, expr_root):
                return "good"
            else:
                return "bad"
        elif self.kind == "loop":
            if not self.helper(self.config[0], expr_root):
                # the first part is not sat, we don't care the other part
                return "good"
            else:
                #now the other part has to be sat
                if self.helper(self.config[1], expr_root):
                    return "good"
                else:
                    return "bad"
                
        raise Exception("check crashed")

class ReplayMem(object):
    def __init__(self, memory_size):
        self.memory_size = memory_size

        self.ce_list = []

        self.count = 0
        self.current = 0
        self.hist_set = set()

    def add(self, ce):
        if ce.ice_str in self.hist_set:
            return
        self.hist_set.add(ce.ice_str)
        if len(self.ce_list) <= self.current:
            self.ce_list.append(ce)
        else:
            self.hist_set.remove(self.ce_list[self.current].ice_str)
            self.ce_list[self.current] = ce
        
        self.count = max(self.count, self.current + 1)
        self.current = (self.current + 1) % self.memory_size
    
    def sample(self, num_samples):
        if num_samples >= self.count:
            return self.ce_list

        sampled_ce = []

        for i in range(num_samples):
            idx = random.randint(0, self.count - 1)
            sampled_ce.append(self.ce_list[idx])
        
        return sampled_ce
    
    def __repr__(self):
        return str(self.ce_list)

class CEHolder(object):
    def __init__(self):
        self.ce_per_key = {}

    def add_ce(self, key, ce):                
        if not key in self.ce_per_key:
            self.ce_per_key[key] = ReplayMem(cmd_args.replay_memsize)
        
        mem = self.ce_per_key[key]
        mem.add(ce)

    def ce_print(self):
        for key in self.ce_per_key:
            print("key:", key)
            print(self.ce_per_key[key])

    def eval(self, key, expr_root):
        if not key in self.ce_per_key:
            return 0.0
        mem = self.ce_per_key[key]
        samples = mem.sample(cmd_args.ce_batchsize)
        assert len(samples)
        s = 0.0
        for ce in samples:            
            if ce.check(expr_root) == "good":
                s += 1.0
        return s / len(samples)

    def eval_score(self, expr_root):
        scores = []
        for key in ICE_KEYS:
            scores.append( self.eval(key, expr_root) )
        return scores
    
    def solve_list(self, expr_root):
        ret = []
        for key in self.ce_per_key:
            mem = self.ce_per_key[key]
            samples = mem.sample(cmd_args.ce_batchsize)
            assert len(samples)
            for ce in samples:            
                if ce.check(expr_root) == "good":
                    ret = ret + [1]
                else:
                    ret = ret + [0]
        return ret

def get_z3_ice(expr_root):
    input_vcs = cmd_args.input_vcs
    inv = str(expr_root)
    sol = z3.Solver()
    sol.set(auto_config=False)

    keys = ICE_KEYS
    kinds = ["pre", "loop", "post"]

    order = [2, 0, 1]

    cexs = checker_module.inv_solver(input_vcs, inv)
    res = []
    for i in order:
        if cexs[i] == "EXCEPT":
            print("EXCEPTION")
            return (-1, None, None)
        elif cexs[i] is not None:
            cex = CounterExample()
            if i == 0:
                cex.kind = "pre"
            elif i == 1:
                cex.kind = "loop"
            elif i == 2:
                cex.kind = "post"
            cex.config = cexs[i]
            cex.ice_str = cex.to_ice_str()
            res.append((0, keys[i], cex))
            break

    if len(res) == 0:
        return (1, None, None)
    return res[0]

model = "gpt-4o_mini"
llm=LLMConfig(SupportLLM(model), debug_mode=True, temperature=0.8)
print(model)

with open(cmd_args.input_code, 'r') as file:
    generator = Re_Clause_generater(
        program=file.read(),
        existing_clauses=set(),
        generate_llm=LLMFactory.create(llm)
)

def check_and_add_ce(holder, expr_root):
    result, key, ce = get_z3_ice(expr_root)
    if key is not None:
        holder.add_ce(key, ce)
        if key == "T:":
            generator.attention = "pre-conditions"
        elif key == "I:":
            generator.attention = "loop-body"
        elif key == "F:":
            generator.attention = "post-conditions"
    return result, key

def expr_split(expr):
    expr = expr.strip()
    expr = str(expr)
    count = 0
    for i in range(len(expr)):
        if(expr[i] == '('):
            count += 1
        if(expr[i] == ')'):
            count -= 1
        if((expr[i] == '&' or expr[i] == '|') and count == 0):
            return expr_split(expr[: i]) + expr_split(expr[i + 2 :])
    if(expr[0] == '(' and expr[-1] == ')' and ( "&" in expr or "|" in expr )):
        expr = expr[1:-1]
        return expr_split(expr)
    return [expr]
    
exprList = []
exprStore = set()
expr_ans = None
expr_failed = set()

def exprList_update(holder, exprList):
    for i in range(len(exprList)):
        expr = exprList[i][1]
        exprList[i] = (sum(holder.eval_score(expr)), expr, holder.solve_list(expr))
    exprList = sorted(exprList, key=lambda x: (x[0], -len(x[1])), reverse = True)
    return exprList

def exprList_delete(exprList):
    i = 0 
    while(i < len(exprList) and sum(exprList[i][2]) == len(exprList[i][2])):
        i += 1
    exprList = exprList[ : i]
    return exprList

def combine_check(holder):
    global exprList
    global exprStore
    while(1):
        clause_list = generator.generate()
        for expr in clause_list:
            generator.existing_clauses.add(expr)
        print(generator.existing_clauses)
        global exprList
        for clause in clause_list:
            if clause not in exprStore:
                exprList.append((sum(holder.eval_score(clause)), clause, holder.solve_list(clause)))
                for expr in exprStore:
                    expr_and = "( " + expr + " && " + clause + " )"
                    expr_or = "( " + expr + " || " + clause + " )"
                    exprList.append((sum(holder.eval_score(expr_and)), expr_and, holder.solve_list(expr_and)))
                    exprList.append((sum(holder.eval_score(expr_or)), expr_or, holder.solve_list(expr_or)))
                exprStore.add(clause)
        exprList = sorted(exprList, key=lambda x: (x[0], -len(x[1])), reverse = True)
        exprList = exprList_delete(exprList)

        global expr_failed
        while(len(exprList) > 0 and exprList[0][1] not in expr_failed):
            res, key = check_and_add_ce(holder, exprList[0][1])
            if res == -1:
                expr_failed.add(exprList[0][1])
                exprStore.discard(exprList[0][1])
            elif res > 0:
                global expr_ans
                expr_ans = exprList[0][1]
                # clause_ans = expr_split(expr_ans)
                # for clause in clause_ans:
                #     print(clause, holder.eval_score(clause), sum(holder.eval_score(clause)))
                return res
            else:
                expr_failed.add(exprList[0][1])
                exprStore.add(exprList[0][1])
                for expr in exprStore:
                    if expr not in exprList[0][1]:
                        if key != "T:":
                            expr_and = "( " + expr + " && " + exprList[0][1] + " )"
                            exprList.append((sum(holder.eval_score(expr_and)), expr_and, holder.solve_list(expr_and)))
                        if key != "F:":
                            expr_or = "( " + expr + " || " + exprList[0][1] + " )"
                            exprList.append((sum(holder.eval_score(expr_or)), expr_or, holder.solve_list(expr_or)))
            exprList = exprList_update(holder, exprList)
            exprList = exprList_delete(exprList)
        exprList = []

def boogie_result():
    # expr_str = ""
    # result, key, ce=get_z3_ice(expr_str)
    # print(ce)
    # exit(0)
    holder = CEHolder()

    global expr_ans
    res = combine_check(holder)
    if res > 0:
        tqdm.write("found a solution: " + str(expr_ans))

    return res