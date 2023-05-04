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

def load_data(path):
    with open(path, 'r') as fp:
        data = json.load(fp)
    return data

def plot_data(polyvol_data,polyvest_data, file_names):  
    # Create plot
    # midpoint = int(len(file_paths)/2)
    dimensions = [file_name.split("_")[1] for file_name in file_names]
    print(dimensions)
    print(list(zip(polyvol_data, polyvest_data)))
    plt.plot(dimensions, list(zip(polyvol_data, polyvest_data)), label=["Polyvol","Polyvest"])
    plt.xlabel('Dimensions', fontsize=12)
    plt.xticks(fontsize=12)
    plt.title("Performance [flops/cycles] for Cubes With Varying Dimensions", fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=12)


    #plt.ylabel('        Performance [flops/cycle]', rotation='horizontal', horizontalalignment='left', y=1, fontsize=12)
    # plt.text(0.0, 1, 'Performance [flops/cycle]',
    plt.text(0.0, 1, 'Flops/Cycles',
            fontsize=12, color='k',
            ha='left', va='bottom',
            transform=plt.gca().transAxes)

    plt.savefig('combined_cubes.png')
    plt.show()

def main():
    directory = "examples"
    file_names, file_paths = list_files_sorted(directory)
    polyvol_data = load_data("polyvol_data.json")
    polyvest_data = load_data("polyvest_data.json")
    plot_data(polyvol_data,polyvest_data, file_names)

if __name__ == '__main__':
    main()