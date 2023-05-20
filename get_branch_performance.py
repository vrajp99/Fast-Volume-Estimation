import subprocess
import json
import re
import os
import traceback

branches = ["xoshiro-rng", "baseline"]
test_dir = "reduced_examples"
results_dir = "results"

def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def list_files_sorted(directory):
    file_names = []
    file_paths = []
    for root, dirs, files in os.walk(directory):
        # Sort directories based on the extracted number
        dirs.sort(key=extract_number)
        # Sort files based on the extracted number
        files.sort(key=extract_number)
        for file in files:
            file_names.append(file)
            file_paths.append(os.path.join(root, file))
    return file_names, file_paths


def parse_file(file_name):
    result = {}
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "fp_arith_inst_retired" in line or "cycles" in line:
                parts = line.strip().split()
                key = parts[1]
                value = int(parts[0].replace("’", ""))
                result[key] = value
    return result


def call_executable(executable ,n, file_name):
    """
    Calls a C program with n as a parameter using 'perf' for profiling.

    Arguments:
        n (int): The value to pass as a parameter to the C program.
        name (str): The name to give the output file.

    Returns:
        result: The result of the C program's execution.
    """
    # Define command to call C program with n as parameter
    command = ["sudo", "perf", "stat", "-o", "results/"+executable.split("/")[-1]+"_"+file_name+".txt", "-e",
               "fp_arith_inst_retired.128b_packed_double,fp_arith_inst_retired.256b_packed_double,fp_arith_inst_retired.scalar_double,cycles",
               "-r", "5", "./"+executable, str(n)]
    # Execute command and capture output
    output = subprocess.check_output(command)
    # Decode output from bytes to string
    output_str = output.decode('utf-8').strip()
    print(output_str.split())
    return float(output_str.split('\n')[-1])


def measure_performance(executable, file_paths):
    measurements = []
    for path in file_paths:
        # Call C program and retrieve number of cycles
        file_name = path.split("/")[-1]
        executable_name = executable.split("/")[-1]
        call_executable(executable, path, file_name)
        measurement = parse_file("results/"+executable_name+"_"+file_name+".txt")
        # Calculate performance
        flops = measurement['fp_arith_inst_retired.128b_packed_double']*2 + \
            measurement['fp_arith_inst_retired.256b_packed_double'] * \
            4 + measurement['fp_arith_inst_retired.scalar_double']
        performance = flops/measurement['cycles']
        measurements.append(performance)
    print("Saving measurements for ", executable_name)
    with open("results/"+executable_name+"_"+".json", 'w') as fp:
        json.dump(measurements, fp)
    return measurements

def toggle_turbo_boost(mode):
    try:
        command = ["sudo", "./turbo-boost.sh", mode]
        subprocess.check_output(command)
    except Exception:
        print("Warning! Turbo Boost could not be toggled with mode ", mode)
        traceback.print_exc()

def create_executables(branches):
    branches_str = ' '.join(branches)
    # Call the bash script and pass the string
    try:
        subprocess.call(["bash", "branches_make_polyvol.sh", branches_str])
    except Exception:
        print("Warning! Could not create executables")
        traceback.print_exc()
    
def main():
    print("Disabling Turbo Boost")
    toggle_turbo_boost("disable")
    print("Creating executables from the following branches: ", branches)
    create_executables(branches)
    print("Parsing test files")
    _, test_paths = list_files_sorted(test_dir)
    print("Creating results dir")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    print("Measuring performance")
    for root, _, files in os.walk("executables"):
        print(root)
        print(files)
        for executable in files:
            executable_path = os.path.join(root, executable)
            print("Measuring performance of ", executable_path)
            measure_performance(executable_path, test_paths)
    print("Enabling Turbo Boost")
    toggle_turbo_boost("enable")


if __name__ == '__main__':
    main()
