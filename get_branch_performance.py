import subprocess
import json
import os
import utils

# Change these variables
#BRANCHES = ["xoshiro-rng", "baseline", "basic-opt", "clang-added", "bound-remove"]
BRANCHES = ["vecplusextraoptim", "preoptvec", "vecplusextraoptim", "fast-linalg"]
TEST_DIR = "reduced_examples"
RESULTS_DIR = "results"


def call_executable(executable ,n, file_name):
    """
    Calls a C++ program with n as a parameter using 'perf' for profiling.

    Arguments:
        executable (str): path to C++ program executable
        n (int): The value to pass as a parameter to the C program.
        name (str): The name to give the output file.

    Returns:
        result: The result of the program's execution.
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
    """
    Measures the performance of an executable on a set of input files
    
    Args:
    - executable(str): The path to the executable whose performance is being measured.
    - file_paths(List[str]): A list of paths to the input files for which the performance 
        is being measured.
    Returns:
    - measurements(List[Tuple[str, float]]): A list of tuples containing the filename and 
        the time taken to execute the executable for each file.
    """
    measurements = []
    for path in file_paths:
        # Call C program and retrieve number of cycles
        file_name = path.split("/")[-1]
        executable_name = executable.split("/")[-1]
        call_executable(executable, path, file_name)
        measurement = utils.parse_file("results/"+executable_name+"_"+file_name+".txt")
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
    
    
def main():
    print("Disabling Turbo Boost")
    utils.toggle_turbo_boost("disable")
    print("Creating executables from the following branches: ", BRANCHES)
    utils.create_executables(BRANCHES)
    print("Parsing test files")
    _, test_paths = utils.list_files_sorted(TEST_DIR)
    print("Creating results dir")
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    print("Measuring performance")
    for root, _, files in os.walk("executables"):
        for executable in files:
            if executable.split("_")[0] in BRANCHES:
                executable_path = os.path.join(root, executable)
                print("Measuring performance of ", executable_path)
                measure_performance(executable_path, test_paths)
    print("Enabling Turbo Boost")
    utils.toggle_turbo_boost("enable")


if __name__ == '__main__':
    main()
