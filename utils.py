import re 
import os
import traceback
import subprocess

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