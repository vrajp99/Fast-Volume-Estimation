import subprocess
import os
import utils

# Change these variables
#BRANCHES = ["xoshiro-rng", "basic-opt", "clang-added", "bound-remove", "fast-linalg", "vecplusextraoptim", "onefile", "reduce-precision", "aligned-vec"]
#BRANCHES = ["polyvest-o3-native-fastmath"]
#BRANCHES = ["reduce-precision-fixed"]
#BRANCHES = ["baseline"]
#BRANCHES = ["finalopt-x"]
BRANCHES = ["reduce-precision-fixed"]
#TEST_DIR = "advanced_tests/polyvest_cross_and_simplex"
#TEST_DIR = "advanced_tests/cube_tests"
#TEST_DIR = "advanced_tests/polyvest_cross_simplex"
TEST_DIR = "advanced_tests/cube_1"
#TEST_DIR = "cubes_70_80"
#TEST_DIR = "advanced_tests/polyvest_cube_tests"
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
    print("Measuring performance on ", file_name)
    # Define command to call C program with n as parameter
    # Edge case for finalopt-x, where we Define M and N for each test case
    if executable.split("/")[-1] == "finalopt-x":
        if "cube_" not in file_name:
            command = ["sudo", "perf", "stat", "-o", "results/"+executable.split("/")[-1]+"_polyvol_"+file_name+".txt",  "-M", "FLOPc", "-e",
               "cache-misses, cache-references, L1-dcache-load-misses, L1-dcache-loads, L1-dcache-stores, L1-icache-load-misses, LLC-loads, LLC-load-misses, LLC-stores, LLC-store-misses", 
               "-r", "5", "./"+executable[:-1]+"-".join(n.split("/")[-1].split("_"))+"_polyvol", str(n)]
        else:
            command = ["sudo", "perf", "stat", "-o", "results/"+executable.split("/")[-1]+"_polyvol_"+file_name+".txt",  "-M", "FLOPc", "-e",
                "cache-misses, cache-references, L1-dcache-load-misses, L1-dcache-loads, L1-dcache-stores, L1-icache-load-misses, LLC-loads, LLC-load-misses, LLC-stores, LLC-store-misses", 
                "-r", "5", "./"+executable[:-1]+n.split("_")[-1]+"_polyvol", str(n)]
    else: 
        command = ["sudo", "perf", "stat", "-o", "results/"+executable.split("/")[-1]+"_"+file_name+".txt",  "-M", "FLOPc", "-e",
               "cache-misses, cache-references, L1-dcache-load-misses, L1-dcache-loads, L1-dcache-stores, L1-icache-load-misses, LLC-loads, LLC-load-misses, LLC-stores, LLC-store-misses", 
               "-r", "5", "./"+executable, str(n)]
    print(command)
    # Execute command and capture output
    output = subprocess.check_output(command)
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
    for path in file_paths:
        # Call C program and retrieve number of cycles
        file_name = path.split("/")[-1]
        call_executable(executable, path, file_name)
    
def main():
    print("Disabling Turbo Boost")
    utils.toggle_turbo_boost("disable")
    #print("Creating executables from the following branches: ", BRANCHES)
    #utils.create_executables(BRANCHES)
    print("Parsing test files")
    _, test_paths = utils.list_files_sorted(TEST_DIR)
    print(test_paths)
    print("Creating results dir")
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    print("Measuring performance")
    for root, _, files in os.walk("executables"):
        for executable in files:
            if executable.split("_")[0] in BRANCHES:
                utils.toggle_turbo_boost("disable")
                executable_path = os.path.join(root, executable)
                print("Measuring performance of ", executable_path)
                measure_performance(executable_path, test_paths)
            elif BRANCHES[0] == "finalopt-x":
                utils.toggle_turbo_boost("disable")
                executable_path = os.path.join(root, "finalopt-x")
                print("Measuring performance of ", executable_path)
                measure_performance(executable_path, test_paths)
                break
                
    print("Enabling Turbo Boost")
    utils.toggle_turbo_boost("enable")


if __name__ == '__main__':
    main()
