import os
import re

time = 0 
solve = 0
solve_1 = 0
solve_2 = 0

for i in range(1, 52):
    if os.path.exists(f'output_nonlinear/{i}.out'):
            with open (f'output_nonlinear/{i}.out', 'r') as file:
                content = file.read()
                pattern = "time cost (\d+\.\d+)"
                match = re.search(pattern, content)
                if match:
                    if i <= 30:
                        solve_1 += 1
                    else:
                        solve_2 += 1
                    time += float(match.group(1))
                    solve += 1

print("solved:", solve)
print("average time:", f'{time/solve}s')
print("initial 30:", solve_1)
print("additional 20:", solve_2)