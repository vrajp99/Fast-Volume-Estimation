import re
import os
import traceback
import subprocess
import json


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
    match = re.search(r'(\d+)', filename)
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


def parse_file(file_name):
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
