import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Create the output directory if it does not exist
output_dir = 'output/'
os.makedirs(output_dir, exist_ok=True)

def run_command(i):
    if os.path.exists(f'output/{i}.out'):
        with open (f'output/{i}.out', 'r') as file:
            if "found a solution" in file.read():
                print("File exists, skipping", i)
                return
    print(f"Running command for {i}")
    
    command = ['./nonlinear.sh', str(i), "no-log"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        
        output_file = os.path.join(output_dir, f'{i}.out')
        
        with open(output_file, 'w') as file:
            file.write(f"Output for {i}:\n{result.stdout}\n")
            if result.stderr:
                file.write(f"Errors for {i}:\n{result.stderr}\n")
                
    except subprocess.TimeoutExpired as e:
        # pass
        output_file = os.path.join(output_dir, f'{i}.err')
        stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else 'No output'
        stderr = e.stderr.decode('utf-8', errors='replace') if e.stderr else None
        
        with open(output_file, 'w') as file:
            file.write(f"Output for {i} (timeout):\n{stdout}\n")
            if stderr:
                file.write(f"Errors for {i}:\n{stderr}\n")
            file.write(f"Command {command} timed out after {e.timeout} seconds.\n")

max_workers = 32

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []

    for i in range(1, 52):
        futures.append(executor.submit(run_command, i))

    for future in as_completed(futures):
        future.result()

print("All commands have been executed and outputs saved.")