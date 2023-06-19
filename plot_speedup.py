import re
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import seaborn as sns
import utils 

# global variables
BASELINE = "baseline"
#BASELINE = "polyvest"
#EXECUTABLES = ["basic-opt", "bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision",]

#BRANCHES = ["polyvest", "bound-remove"] 
#BRANCHES = ["polyvest", "bound-remove", "fast-linalg"] 
#BRANCHES = ["polyvest", "bound-remove", "fast-linalg", "vecplusextraoptim"]
#BRANCHES = ["polyvest", "bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec"]
BRANCHES = ["polyvest","bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision"]
#BRANCHES = ["bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision"]


TEST_CASES =["cube_20", "cube_40", "cube_60", "cube_80"]
COMPARE = "time"  # or "cycles"

# Set up LaTeX and font family
plt.rcParams['text.usetex'] = True
plt.rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

def get_statistic(filename, statistic_type):
    with open(filename, 'r') as f:
        content = f.read()
        if statistic_type == "cycles":
            match = re.search(r'(\d+[’\d+]*)\s+cycles\s*\(\s*\+-\s*(\d+\.\d+)%', content)
        elif statistic_type == "time":
            match = re.search(r'(\d+.\d+)\s+\+-\s*(\d+.\d+)\s+seconds', content)
        if match:
            value_str = match.group(1)
            # convert '’' separated number or float to a number
            value = float(''.join(value_str.split('’')))
            deviation = float(match.group(2)) / 100  # Convert percentage to decimal
            return value, value * deviation
        else:
            print(f"No {statistic_type} found in file {filename}")
            return None, None

def create_plot(data, errors):
    # Seaborn style
    sns.set_style("whitegrid")

    # Number of groups and bar width
    n_groups = len(TEST_CASES)
    n_bars = len(BRANCHES)
    bar_width = 0.2  # adjust as needed
    gap_width = 0.5  # adjust as needed
    # Create subplots
    fig, ax = plt.subplots()
    print(data)
    # Set bar positions and plot
    for i, (exe, values) in enumerate(data.items()):
        if exe != BASELINE:
            print(exe, values)
            ax.bar(np.arange(n_groups) * (n_bars * bar_width + gap_width) + i * bar_width, values, 
                   width=bar_width, label=exe, color=utils.BRANCH_COLOR_DICT[exe], yerr=errors[exe], 
                   capsize=5, error_kw={'elinewidth':1, 'capthick':1})

    
    ax.set_xticks(np.arange(n_groups) * (n_bars * bar_width + gap_width) + bar_width * (n_bars - 1) / 2, font='serif')
    ax.set_xticklabels(TEST_CASES)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.xaxis.get_major_formatter()._usetex = False
    ax.yaxis.get_major_formatter()._usetex = False

    plt.text(0.0, 1, 'Speedup Ratio',
            fontsize=14, color='k',
            ha='left', va='bottom',
            transform=plt.gca().transAxes)
    # Add labels, title, legend
    ax.set_xlabel(r'Test Cases', fontsize=14)
    #ax.set_ylabel(r'Speedup Ratio', fontsize=16)
    
    ax.set_title(r'\textbf{' + 'Speedup Ratio over "{}" ({})'.format(BASELINE, COMPARE)+'}', fontsize=14, y=1.04, loc='left', fontweight="bold")
    ax.legend(shadow=True, fontsize=14)
    # Increase font sizes for better readability
    plt.rcParams.update({'font.size': 16})

    # Save the figure in higher resolution
    plt.savefig(f'plots/speedup_plots/better_speedup_of_'+'_'.join(BRANCHES)+'_over_'+BASELINE+'_'+COMPARE+'.svg', bbox_inches='tight', dpi=300)

   
def main():
    data = {exe: [] for exe in BRANCHES}
    errors = {exe: [] for exe in BRANCHES}

    for test_case in TEST_CASES:
        baseline_filename = f"results/{BASELINE}_polyvol_{test_case}.txt"
        baseline_stat, _ = get_statistic(baseline_filename, COMPARE)

        if baseline_stat is None:
            print(f"Cannot proceed without baseline {COMPARE} for {test_case}")
            continue

        for exe in BRANCHES:
            
            filename = f"results/{exe}_polyvol_{test_case}.txt"
            #stat = get_statistic(filename, COMPARE)
            stat, stat_error = get_statistic(filename, COMPARE)
            print(stat, stat_error)
            if stat is not None:
                speedup = baseline_stat / stat
                speedup_error = speedup * (stat_error / stat)

                data[exe].append(speedup)
                errors[exe].append(speedup_error)
    print(data)
    print(errors)

    create_plot(data, errors)

if __name__ == "__main__":
    main()