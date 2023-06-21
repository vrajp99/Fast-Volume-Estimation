import matplotlib.pyplot as plt
from matplotlib import cycler
import utils
import os
import seaborn as sns

#BRANCHES = ["baseline", "polyvest","bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision"]

BRANCHES = ["polyvest-o3-native-fastmath", "baseline"] 
#BRANCHES = ["polyvest-o3-native-fastmath", "baseline", "bound-remove"] 
#BRANCHES = ["polyvest-o3-native-fastmath", "fast-linalg"] 
#BRANCHES = ["polyvest-o3-native-fastmath", "fast-linalg", "vecplusextraoptim"]
#BRANCHES = ["polyvest-o3-native-fastmath", "fast-linalg", "vecplusextraoptim", "reduce-precision-fixed"]
#BRANCHES = ["polyvest-o3-native-fastmath", "fast-linalg", "vecplusextraoptim", "reduce-precision-fixed", "finalopt-x"]
 
#BRANCHES = ["fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision"] # After fast-linalg

#BRANCHES = ["aligned-vec", "reduce-precision"] # After fast-linalg
TEST_DIR = "advanced_tests/cube_tests_simple"
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
#plt.rcParams["figure.figsize"] = (12,9)
plt.rcParams.update({'font.size': 18})
#plt.rcParams["font.weight"] = "bold"
#plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams['text.usetex'] = True
plt.rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

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
    for branch in BRANCHES:
        data[branch] = [float(x) for x in data[branch]]
        plt.plot(dimensions, data[branch], label=utils.BRANCH_NAME_DICT[branch], linewidth=3, color=utils.BRANCH_COLOR_DICT[branch])
    plt.xlabel('Cube Dimensions', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14, shadow=True)
    ax = plt.gca()
    ax.xaxis.get_major_formatter()._usetex = False
    ax.yaxis.get_major_formatter()._usetex = False
    plt.text(0.0, 1, 'Performance Flops/Cycles',
            fontsize=14, color='k',
            ha='left', va='bottom',
            transform=plt.gca().transAxes)
    plt.title(r'\textbf{' + 'Performance on Cubes With Different Sizes' +'}', fontsize=14, y=1.04, loc='left', fontweight="bold")
    plt.savefig(f'plots/performance_plots/performance_' +"_".join(BRANCHES)+'.svg', bbox_inches='tight', dpi=300)
    #plt.savefig(f'plots/performance_plots/performance_baseline_polyvest_bound-remove.png', bbox_inches='tight', dpi=300)


def main():
    print("Branches: ", BRANCHES)
    file_names, data = utils.extract_results(TEST_DIR, RESULTS_DIR, BRANCHES)
    plot_data(data, file_names)

if __name__ == '__main__':
    main()