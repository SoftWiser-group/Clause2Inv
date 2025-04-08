import os
import re

solve = 0
time = 0
query = 0
solve_1 = 0
solve_2 = 0
solve_3 = 0

for i in range(1, 317):
    if os.path.exists(f'output_linear/{i}.out'):
            with open (f'output_linear/{i}.out', 'r') as file:
                content = file.read()
                pattern = "time cost (\d+\.\d+)"
                match = re.search(pattern, content)
                pattern2 = "inv "
                match2 = re.findall(pattern2, content)
                if match:
                    solve += 1
                    time += float(match.group(1))
                    query += int(len(match2) / 2)
                    if i <= 133:
                        solve_1 += 1
                    elif i <= 217:
                        solve_2 += 1
                    else:
                        solve_3 += 1
print(solve, "solved")
print(time / solve, "s")
print(query / solve, "queries")
print(solve_1, solve_2, solve_3)