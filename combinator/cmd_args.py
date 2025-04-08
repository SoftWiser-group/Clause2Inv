import argparse

cmd_opt = argparse.ArgumentParser(description='Argparser')
cmd_opt.add_argument('-input_code', default=None, help='path to single input code')
cmd_opt.add_argument('-input_graph', default=None, help='path to single input json graph')
cmd_opt.add_argument('-input_vcs', default=None, help='path to input smt2 format VCs')
cmd_opt.add_argument('-inv_checker', default="c_inv_checker", help='path to solver module')
cmd_opt.add_argument('-replay_memsize', default=100, type=int, help='replay memsize')
cmd_opt.add_argument('-ce_batchsize', default=100, type=int, help='batchsize for counter example check')
cmd_args, _ = cmd_opt.parse_known_args()

start_time = None

import time

def tic():
    global start_time
    start_time = time.time()

def toc():
    global start_time
    cur_time = time.time()
    return cur_time - start_time 