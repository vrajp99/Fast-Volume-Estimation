import matplotlib.pyplot as plt
from matplotlib import cycler
import numpy as np
import subprocess
import json
import re
import os

colors = cycler('color',
                ['#EE6666', '#3388BB', '#9988DD',
                '#EECC55', '#88BB44', '#FFBBBB'])
color_list = ['#EE6666', '#3388BB', '#9988DD',
                '#EECC55', '#88BB44', '#FFBBBB']
plt.rc('axes', facecolor='#E6E6E6', edgecolor='none',
        axisbelow=True, grid=True, prop_cycle=colors)
plt.rc('grid', color='w', linestyle='solid')
plt.rc('xtick', direction='out', color='gray')
plt.rc('ytick', direction='out', color='gray')
plt.rc('patch', edgecolor='#E6E6E6')
plt.rc('lines', linewidth=2)
plt.rcParams["figure.figsize"] = (12,6)


def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

def list_files_sorted(directory):
    file_names = []
    file_paths = []

    for root, dirs, files in os.walk(directory):
        dirs.sort(key=extract_number)  # Sort directories based on the extracted number
        files.sort(key=extract_number)  # Sort files based on the extracted number

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

def call(n, name):
    # Define command to call C program with n as parameter
    command = ["sudo", "perf","stat","-o", "results/"+name+".txt", "-e", "fp_arith_inst_retired.128b_packed_double,fp_arith_inst_retired.256b_packed_double,fp_arith_inst_retired.scalar_double,cycles", "-r", "5", "./polyvol", str(n)]
     # Execute command and capture output
    output = subprocess.check_output(command)
    # Decode output from bytes to string
    output_str = output.decode('utf-8').strip()
    print(output_str.split())  
    return float(output_str.split('\n')[-1])  
    
def measure_performance(file_paths):
    # Loop through matrix sizes
    measurements = []
    for path in file_paths:
        # Call C program and retrieve number of cycles
        name = path.split("/")[-1]
        call(path, name)
        measurement = parse_file("results/"+name+".txt")
        print("Measurement ", measurement)
            
        # Calculate performance
        # measurement = get_flops(n) / measurement
        flops= measurement['fp_arith_inst_retired.128b_packed_double']*2 + measurement['fp_arith_inst_retired.256b_packed_double']*4+ measurement['fp_arith_inst_retired.scalar_double']
        performance = flops/measurement['cycles']
        print(performance)
        measurements.append(performance)
    with open('data.json', 'w') as fp:
        json.dump(measurements, fp)
    return measurements

def load_data():
    with open('data.json', 'r') as fp:
        data = json.load(fp)
    return data

def plot_data(data, file_names):  
    # Create plot
    # midpoint = int(len(file_paths)/2)
    dimensions = [file_name.split("_")[1] for file_name in file_names]
    plt.plot(dimensions, data)
    plt.xlabel('Dimensions', fontsize=12)
    plt.xticks(fontsize=12)
    plt.title("Performance [flops/cycles] for Cubes With Varying Dimensions", fontsize=14)
    plt.yticks(fontsize=14)
    #plt.legend(fontsize=12)


    #plt.ylabel('        Performance [flops/cycle]', rotation='horizontal', horizontalalignment='left', y=1, fontsize=12)
    # plt.text(0.0, 1, 'Performance [flops/cycle]',
    plt.text(0.0, 1, 'Flops/Cycles',
            fontsize=12, color='k',
            ha='left', va='bottom',
            transform=plt.gca().transAxes)

    plt.savefig('cubes.png')
    plt.show()

def main():
    directory = "examples"
    file_names, file_paths = list_files_sorted(directory)
    measure_performance(file_paths)
    data = load_data()
    plot_data(data, file_names)

if __name__ == '__main__':
    main()