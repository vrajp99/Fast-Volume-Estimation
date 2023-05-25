import matplotlib.pyplot as plt
from matplotlib import cycler
import utils
import os

BRANCHES = ["xoshiro-rng", "baseline", "basic-opt", "clang-added", "bound-remove", "polyvest", "vectorization"]
TEST_DIR = "reduced_examples"
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
    dimensions = [file_name.split("_")[1] for file_name in file_names]
    plt.plot(dimensions, list(zip(*data.values())), label=data.keys())
    plt.xlabel('Dimensions', fontsize=12)
    plt.xticks(fontsize=12)
    plt.title("Performance [flops/cycles] for Cubes With Varying Dimensions", fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=12)
    plt.text(0.0, 1, 'Flops/Cycles',
            fontsize=12, color='k',
            ha='left', va='bottom',
            transform=plt.gca().transAxes)
    plt.savefig('branches_combined_cubes.png')
    plt.show()


def main():
    file_names, _ = utils.list_files_sorted(TEST_DIR)
    data = {}
    for root, _, files in os.walk(RESULTS_DIR):
        for result in files:
            if result.endswith(".json"):
                branch = result.split("_")[0]
                print("branch ", branch)
                if branch in BRANCHES:
                    data[branch] = utils.load_data(os.path.join(root, result))
    plot_data(data, file_names)

if __name__ == '__main__':
    main()