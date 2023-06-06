import matplotlib.pyplot as plt
from matplotlib import cycler
import utils
import os
import seaborn as sns


BRANCHES = ["baseline", "polyvest", "basic-opt","bound-remove"] # Before fast-linalg
#BRANCHES = ["fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision"] # After fast-linalg

#BRANCHES = ["aligned-vec", "reduce-precision"] # After fast-linalg
TEST_DIR = "advanced_tests/cube_tests"
#TEST_DIR = "tests/"

RESULTS_DIR = "results"

colors = cycler('color',['#EE6666', '#3388BB', '#9988DD','#EECC55', '#88BB44', '#FFBBBB'])
color_list = ['#EE6666', '#3388BB', '#9988DD','#EECC55', '#88BB44', '#FFBBBB']
plt.rc('axes', facecolor='#E6E6E6', edgecolor='none',
        axisbelow=True, grid=True, prop_cycle=colors)
plt.rc('grid', color='w', linestyle='solid')
plt.rc('xtick', direction='out', color='gray')
plt.rc('ytick', direction='out', color='gray')
plt.rc('patch', edgecolor='#E6E6E6')
plt.rc('lines', linewidth=2)
plt.rcParams["figure.figsize"] = (12,6)
plt.rcParams.update({'font.size': 14})

def plot_data(data, file_names):  
    """
    Plots the given data using the specified file names and
    returns the dimensions of each file name.
    
    Args:
        data: A list of data to be plotted.
        file_names: A list of file names to use for plotting.

    Returns:
        A list of dimensions extracted from each file name.
    """
    sns.set_style("whitegrid")
    dimensions = [file_name.split("_")[1] for file_name in file_names]
    print(data)
    print(list(zip(*data.values())))
    for branch in data:
        data[branch] = [float(x) for x in data[branch]]
    plt.plot(dimensions, list(zip(*data.values())), label=data.keys())
    plt.xlabel('Dimensions', fontsize=12)
    plt.xticks(fontsize=11)
    plt.title("Performance [flops/cycles] for Cubes With Varying Dimensions", fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=12)
    plt.text(0.0, 1, 'Flops/Cycles',
            fontsize=12, color='k',
            ha='left', va='bottom',
            transform=plt.gca().transAxes)
    plt.savefig(f'plots/performance_plots/performance_before_fast-linalg.png', bbox_inches='tight', dpi=300)


def main():
    print("Branches: ", BRANCHES)
    file_names, _ = utils.list_files_sorted(TEST_DIR)
    print(file_names)
    data = {}
    for root, _, files in os.walk(RESULTS_DIR):
        files.sort(key=utils.extract_number)
        for result in files:
            if result.endswith(".txt"):
                branch = result.split("_")[0].strip()
                if branch in BRANCHES:
                    if branch not in data:
                        data[branch] = []
                    file_flopc = utils.parse_file(os.path.join(root, result))
                    data[branch].append(file_flopc["FLOPc"])
    plot_data(data, file_names)

if __name__ == '__main__':
    main()