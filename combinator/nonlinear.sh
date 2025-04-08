#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <number>"
    exit 1
fi

input_code="Benchmarks/NL/c/NL$1.c"
input_graph="Benchmarks/NL/c_graph/NL$1.c.json"
input_vcs="Benchmarks/NL/c_smt/NL$1.c_smt"
grammar_file="c_spec"

if [ $# -gt 1 ]; then
python -u main.py \
    $1 \
    -input_code "$input_code" \
    -input_graph "$input_graph" \
    -input_vcs "$input_vcs"
else
touch log/NL$1.log
code log/NL$1.log
python -u main.py \
    $1 \
    -input_code "$input_code" \
    -input_graph "$input_graph" \
    -input_vcs "$input_vcs" \
    > log/NL$1.log 2>&1
fi