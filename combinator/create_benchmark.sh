#!/bin/bash

# 检查是否传入了第一个参数
if [ -z "$1" ]; then
    echo "请提供文件编号作为第一个参数。例如：./create_benchmark.sh 31"
    exit 1
fi

# 第一个参数作为编号
file_number=$1

# 将文件复制到容器
docker cp /home/cwn/expr2inv/Benchmarks/NL/c/NL"$file_number".c code2inv:/code2inv/clang-fe/file.c

# 在容器内部执行命令（非交互式）
docker exec code2inv bash -c "
    cd /code2inv/clang-fe/ &&
    ./a.sh
"

# 将生成的文件从容器复制出来
docker cp code2inv:/code2inv/clang-fe/file.c.json /home/cwn/expr2inv/Benchmarks/NL/c_graph/NL"$file_number".c.json
docker cp code2inv:/code2inv/clang-fe/file.c.smt2 /home/cwn/expr2inv/Benchmarks/NL/c_smt/NL"$file_number".c_smt
