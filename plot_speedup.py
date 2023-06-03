import re
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# global variables
BASELINE = "baseline"
EXECUTABLES = ["basic-opt", "fast-linalg", "vecplusextraoptim", "aligned-vec", "reduce-precision",]
TEST_CASES =["cube_10", "cube_20", "cube_40"]
COMPARE = "time"  # or "cycles"

def get_statistic(filename, statistic_type):
    with open(filename, 'r') as f:
        content = f.read()
        if statistic_type == "cycles":
            match = re.search(r'(\d+[’\d+]*)\s+cycles', content)
        elif statistic_type == "time":
            match = re.search(r'(\d+.\d+)\s+\+-', content)
        if match:
            value_str = match.group(1)
            # convert '’' separated number or float to a number
            value = float(''.join(value_str.split('’')))
            return value
        else:
            print(f"No {statistic_type} found in file {filename}")
            return None

def create_plot(data):
    # Seaborn style
    sns.set_style("whitegrid")
    colors = sns.color_palette("deep", len(EXECUTABLES))

    # Number of groups and bar width
    n_groups = len(TEST_CASES)
    n_bars = len(EXECUTABLES)
    bar_width = 0.2  # adjust as needed
    gap_width = 0.5  # adjust as needed

    # Create subplots
    fig, ax = plt.subplots()

    # Set bar positions and plot
    for i, (exe, values) in enumerate(data.items()):
        if exe != BASELINE:
            ax.bar(np.arange(n_groups) * (n_bars * bar_width + gap_width) + i * bar_width, values, 
                   width=bar_width, label=exe, color=colors[i])

    # Set x-ticks in the middle of the groups of bars
    ax.set_xticks(np.arange(n_groups) * (n_bars * bar_width + gap_width) + bar_width * (n_bars - 1) / 2)
    ax.set_xticklabels(TEST_CASES)

    # Add labels, title, legend
    ax.set_xlabel('Test Cases')
    ax.set_ylabel('Speedup Ratio')
    ax.set_title(f'Speedup Ratio over "{BASELINE}" ({COMPARE})')
    ax.legend()

    # Increase font sizes for better readability
    plt.rcParams.update({'font.size': 14})

    # Save the figure in higher resolution
    plt.savefig(f'plots/speedup_plots/speedup_over_{BASELINE}_{COMPARE}.png', bbox_inches='tight', dpi=300)

def main():
    data = {exe: [] for exe in EXECUTABLES}
    for test_case in TEST_CASES:
        baseline_filename = f"results/{BASELINE}_polyvol_{test_case}.txt"
        baseline_stat = get_statistic(baseline_filename, COMPARE)

        if baseline_stat is None:
            print(f"Cannot proceed without baseline {COMPARE} for {test_case}")
            continue

        for exe in EXECUTABLES:
            filename = f"results/{exe}_polyvol_{test_case}.txt"
            stat = get_statistic(filename, COMPARE)
            if stat is not None:
                data[exe].append(baseline_stat / stat)

    create_plot(data)

if __name__ == "__main__":
    main()