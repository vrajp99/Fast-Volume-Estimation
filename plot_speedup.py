import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import utils 

# global variables
BASELINE = "baseline"
#BASELINE = "polyvest"
#EXECUTABLES = ["basic-opt", "bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision",]

BRANCHES = ["bound-remove"] 
BRANCHES = ["bound-remove", "fast-linalg"] 
BRANCHES = ["bound-remove", "fast-linalg", "vecplusextraoptim"]
BRANCHES = ["bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec"]
BRANCHES = ["bound-remove", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision"]


TEST_CASES =["cube_20", "cube_40", "cube_60", "cube_80"]
COMPARE = "time"  # or "cycles"

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
    colors = sns.color_palette("deep", len(BRANCHES))

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
            #ax.bar(np.arange(n_groups) * (n_bars * bar_width + gap_width) + i * bar_width, values, 
            #       width=bar_width, label=exe, color=utils.BRANCH_COLOR_DICT[exe])
            print(exe, values)
            ax.bar(np.arange(n_groups) * (n_bars * bar_width + gap_width) + i * bar_width, values, 
                   width=bar_width, label=exe, color=utils.BRANCH_COLOR_DICT[exe], yerr=errors[exe], 
                   capsize=5, error_kw={'elinewidth':1, 'capthick':1})

    # Set x-ticks in the middle of the groups of bars
    ax.set_xticks(np.arange(n_groups) * (n_bars * bar_width + gap_width) + bar_width * (n_bars - 1) / 2)
    ax.set_xticklabels(TEST_CASES)

    # Add labels, title, legend
    ax.set_xlabel('Test Cases')
    ax.set_ylabel('Speedup Ratio')
    ax.set_title(f'Speedup Ratio over "{BASELINE}" ({COMPARE})', y=-0.2)
    ax.legend()

    # Increase font sizes for better readability
    plt.rcParams.update({'font.size': 14})

    # Save the figure in higher resolution
    plt.savefig(f'plots/speedup_plots/speedup_of_'+'_'.join(BRANCHES)+'_over_'+BASELINE+'_'+COMPARE+'.png', bbox_inches='tight', dpi=300)

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