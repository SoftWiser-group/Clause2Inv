#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <number>"
    exit 1
fi

input_code="Benchmarks/Linear/c/$1.c"
input_graph="Benchmarks/Linear/c_graph/$1.c.json"
input_vcs="Benchmarks/Linear/c_smt2/$1.c.smt"
grammar_file="c_spec"

if [ $# -gt 1 ]; then
python -u main.py \
    -input_code "$input_code" \
    -input_graph "$input_graph" \
    -input_vcs "$input_vcs"
else
touch log/$1.log
code log/$1.log
python -u main.py \
    -input_code "$input_code" \
    -input_graph "$input_graph" \
    -input_vcs "$input_vcs" \
    > log/$1.log 2>&1
fi