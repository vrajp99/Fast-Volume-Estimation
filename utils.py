import re
import os
import traceback
import subprocess
import json
from math import sqrt


def extract_number(filename):
    """
    Helper function to extract the dimension of the polytope from filename to sort files
    
    Args:
        filename (str): The filename from which to extract the number.
        
    Returns:
        str: The extracted number as a string.
        
    Raises:
        AttributeError: If the filename is None or does not contain any digits.
    """
    match = re.search(r'(\d+).txt', filename)
    if match:
        return int(match.group(1))
    return 0


def list_files_sorted(directory):
    """
    Return a sorted list of file names in the specified directory.
    
    Args:
        directory (str): The directory path to search for files.
        
    Returns:
        A list of sorted file names (strings).
        
    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
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


def extract_perf(file_name):
    measurements = {}
    # Dictionary to hold the standard deviations
    stds = {}
    # Read the file
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Match lines of interest
            match = re.search(r'(\d+[’\d]*|<not counted>)\s+(FP_ARITH_INST_RETIRED\.128B_PACKED_DOUBLE|FP_ARITH_INST_RETIRED\.SCALAR_DOUBLE|FP_ARITH_INST_RETIRED\.256B_PACKED_DOUBLE|CPU_CLK_UNHALTED\.THREAD)', line)
            if match:
                # Check if the measurement is '0' or '<not counted>'
                if match.group(1) == '0' or match.group(1) == '<not counted>':
                    measurement = 0
                else:
                    # Remove apostrophe from number and convert to int
                    measurement = int(match.group(1).replace("’", ""))
                # Get the measurement type
                measurement_type = match.group(2)
                # Store the measurements
                measurements[measurement_type] = measurement
            # Match lines for standard deviations
            match = re.search(r'\( \+-\s+(\d+\.\d+)%', line)
            if match:
                # Get the standard deviation and convert to float
                std = float(match.group(1))

                # Store the standard deviations
                stds[measurement_type] = std
    # Compute the performance
    flops = measurements['FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE'] * 2 + \
            measurements['FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE'] * 4 + \
            measurements['FP_ARITH_INST_RETIRED.SCALAR_DOUBLE']
    performance = flops / measurements['CPU_CLK_UNHALTED.THREAD']

    # Compute the total standard deviation
    std_components = []
    for measurement_type in ['FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE', 'FP_ARITH_INST_RETIRED.256B_PACKED_DOUBLE', 'FP_ARITH_INST_RETIRED.SCALAR_DOUBLE', 'CPU_CLK_UNHALTED.THREAD']:
        if measurements.get(measurement_type, 0) != 0:
            std_components.append((stds.get(measurement_type, 0) / measurements[measurement_type])**2)

    std_performance = performance * sqrt(sum(std_components))
    print(performance, std_performance)
    return performance, std_performance

def parse_file(file_name, get_std=False):
    """
    Parses a text file and returns a dictionary of keys with list values.
    
    Args:
        file_name (str): Name of the text file to parse.
        
    Returns:
        A dictionary where each key corresponds to a line in the text file and the
        value is a list of words in that line.
        
    Raises:
        FileNotFoundError: If the specified file is not found.
    """
    measurement = {}
    result = {}
    with open(file_name, 'r') as file:
        read_file = file.read()
    with open(file_name, 'r') as file:
        lines = file.readlines()
    if get_std:
        perf, std = extract_perf(file_name)
        print(file_name)
        print(measurement)
        result["FLOPc"] = perf
        result["FLOPc_std"] = std
    match = re.search(r'FP_ARITH_INST_RETIRED\.128B_PACKED_SINGLE\s*#\s*([0-9.]+)', read_file)
    if match:
        result["FLOPc"] = match.group(1)
    else:
        for line in lines:
            print(line)
            if "fp_arith_inst_retired" in line or "cycles" in line:
                parts = line.strip().split()
                key = parts[1]
                value = int(parts[0].replace("’", ""))
                measurement[key] = value
        print(measurement)
        print(file_name)
        flops = measurement['fp_arith_inst_retired.128b_packed_double']*2 + \
            measurement['fp_arith_inst_retired.256b_packed_double'] * \
            4 + measurement['fp_arith_inst_retired.scalar_double']
        performance = flops/measurement['cycles']
        result["FLOPc"] = performance
    return result


def toggle_turbo_boost(mode):
    """
    Toggles Intel Turbo Boost feature enable or disable for the CPU.
    
    Args:
        mode (str): Mode to set Turbo Boost to. Valid values are 'enable' or 'disable'.
        
    Returns:
        None.
        
    Raises:
        ValueError: If an invalid mode value is provided.
        OSError: If there is an error running the turbo-boost.sh script.
    """
    try:
        command = ["sudo", "./turbo-boost.sh", mode]
        subprocess.check_output(command)
    except Exception:
        print("Warning! Turbo Boost could not be toggled with mode ", mode)
        traceback.print_exc()


def create_executables(branches):
    """
    Create executable files for the specified branches.
    
    Args:
        branches (list): A list of branch names for which to create executable files.
    
    Returns:
        None
    """
    branches_str = ' '.join(branches)
    # Call the bash script and pass the string
    try:
        subprocess.call(["bash", "branches_make_polyvol.sh", branches_str])
    except Exception:
        print("Warning! Could not create executables")
        traceback.print_exc()


def run_advisor(branch, testfile):
    """
    Create executable files for the specified branches.
    
    Args:
        branches (list): A list of branch names for which to create executable files.
    
    Returns:
        None
    """
    # Call the bash script and pass the string
    try:
        subprocess.call(["bash", "run_advisor_analysis.sh", branch, testfile])
    except Exception:
        print("Warning! Could not create executables")
        traceback.print_exc()


def init_adivor_vars():
    """
    Initializes the variables for the Intel Advisor by calling the advisor-vars.sh script.

    This function calls the specified command through the subprocess module.
    
    Args:
        None
    
    Example Usage:
        init_adivor_vars() # initializes the advisor vars
        
    Raises:
        OSError : An error occurred while executing the command.
    """
    try:
        #subprocess.Popen("/bin/sh", "/opt/intel/oneapi/advisor/latest/advisor-vars.sh")
        #subprocess.Popen("/bin/sh", "/opt/intel/oneapi/advisor/latest/advixe-vars.sh")
        subprocess.call(["bash", "source_advisor.sh"])
    except Exception:
        print("Warning! Could not init advisor variables")
        traceback.print_exc()


def load_data(path):
    """
    Load JSON data from a file.
    
    Args:
        path (str): The path to the JSON file.
    
    Returns:
        dict: The contents of the JSON file as a Python dictionary.
    """
    with open(path, 'r') as fp:
        data = json.load(fp)
    return data


BRANCH_COLOR_DICT = {
    "baseline": '#EE6666', 
    "polyvest": '#3388BB',
    "polyvest-o3-native-fastmath": '#3388BB',
    "bound-remove": '#9988DD', 
    "fast-linalg": '#EECC55', 
    "vecplusextraoptim": '#88BB44', 
    "aligned-vec": '#FFBBBB',
    "reduce-precision": '#964B00',
    "reduce-precision-fixed": '#964B00',
    "finalopt": '#ff9966',
    "finalopt-x": '#97d2d4'
}

BRANCH_NAME_DICT = {
    "baseline": 'Baseline', 
    "polyvest": 'PolyVest',
    "polyvest-o3-native-fastmath": 'PolyVest',
    "bound-remove": 'Opt-I', 
    "fast-linalg": 'Opt-II', 
    "vecplusextraoptim": 'Opt-III', 
    "aligned-vec": 'Opt-IV',
    "reduce-precision": 'Opt-IV',
    "reduce-precision-fixed": 'Opt-IV',
    "finalopt": 'Opt-V',
    "finalopt-x": 'Opt-V'
}



def extract_results(test_dir, results_dir, branches, get_std=False):
    """
    Extracts test results (perf) from the given directory.
    
    Arguments:
    test_dir -- the path to the directory containing the test files
    results_dir -- the path to the directory where the extracted results will be saved
    branches -- a list of branches to include in the extracted results
    
    Returns:
    file_names -- a list of file names corresponding to the test cases
    data -- a dictionary containing the extracted results
    """
    # Utility functions
    test_files, _ = list_files_sorted(test_dir)
    
    file_names = []
    data = {}

    # Loop through files in results_dir and subdirectories
    for root, _, files in os.walk(results_dir):
        # Sort files by number extracted from file name
        files.sort(key=extract_number)
        
        # Analyze each file
        for result in files:
            # Only consider .txt files
            if not result.endswith(".txt"):
                continue
            
            # Extract branch and data_file from result
            branch, data_file_with_ext = result.split("_polyvol_")
            data_file = data_file_with_ext.strip(".txt")

            # Check branch and data_file against filters
            if branch in branches and data_file in test_files:
                # Ensure each file name is only added once
                if data_file not in file_names:
                    file_names.append(data_file)
                
                # Initialize branch in data if not already present
                if branch not in data:
                    data[branch] = {"FLOPc": [], "FLOPc_std": []}
                
                # Read FLOPc data from file and add to branch in data
                file_flopc = parse_file(os.path.join(root, result), get_std)
                if branch == "polyvest-o3-native-fastmath":
                    print(result)
                    print(file_flopc)
                #data[branch].append(file_flopc["FLOPc"])
                data[branch]["FLOPc_std"].append(file_flopc["FLOPc_std"])
                data[branch]["FLOPc"].append(file_flopc["FLOPc"])
    
    # Sort file_names by number extracted from file name
    file_names.sort(key=extract_number)
    return file_names, data


def format_number(n, threshold=100000):
    """Format number as float or in scientific notation, based on a threshold."""
    return '{:.2e}'.format(n) if abs(n) >= threshold else '{:.2f}'.format(n)


def extract_number_table(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')