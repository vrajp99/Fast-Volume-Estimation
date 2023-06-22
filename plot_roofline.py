# Adapted from intel advisor api examples https://www.intel.com/content/www/us/en/developer/articles/training/how-to-use-the-intel-advisor-python-api.html
# Copyright (C) 2017 Intel Corporation

import matplotlib.cm as cm
import click
import seaborn as sns
import matplotlib.pyplot as plt
import math
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

# CONFIG
# Roofs we want to exclude
EXCLUDE = ["Scalar", "Int64", "Int32"]
LOOPS_AND_FUNCTIONS = {"polytope::estimateVol": {"identifiers": ["estimateVol"], "gflop": [], "gflops": [], "bytes": [], "time": []},
                       "polytope::walk": {"identifiers": ["_ZNK8polytope4walkEPfS0"],
                                          "gflop": [], "gflops": [], "bytes": [], "time": []}}
#LOOPS_AND_FUNCTIONS = {"polytope::estimateVol": {"identifiers": ["estimateVol"], "gflop": [], "gflops": [], "bytes": [], "time": []}}

pd.options.display.max_rows = 20
# Set the default font size
plt.rcParams.update({'font.size': 14})
plt.rcParams['text.usetex'] = True
plt.rc('text.latex', preamble=r'\usepackage{cmbright}')
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'

try:
    import advisor
except ImportError:
    print(
        """Import error: Python could not resolve path to Advisor's pythonapi directory.
        To fix, either manually add path to the pythonapi directory into PYTHONPATH environment
        variable, or use advixe-vars.* scripts to set up product environment variables automatically."""
    )
    sys.exit(1)

# Check command-line arguments.
if len(sys.argv) < 2:
    print('Usage: "python {} path_to_project_dir"'.format(__file__))
    sys.exit(2)


@click.command()
@click.option('--name', '-n', required=True, help='The name of the generated'
              'roofline png.')
@click.option('--project', '-o', required=True,
              help='The directory of the Intel Advisor project containing '
                   'a roofline analysis.')
@click.option('--scale', type=float, default=1.0,
              help='Specify by how much should the roofs be '
                   'scaled down due to using fewer cores than '
                   'available (e.g., when running on a single '
                   'socket).')
@click.option('--precision', type=click.Choice(['SP', 'DP', 'all']),
              help='Arithmetic precision.', default='all')
# Open the Advisor Project and load the data.
def roofline(name, project, scale, precision):
    sns.set_style("whitegrid")
    project = advisor.open_project(project)
    # Open the Advisor Project and load the data.
    data = project.load(advisor.ALL)
    # Iterate over the entries in the bottomup table and print a joined version.
    # Access the entries and roof data from the survey data.
    rows = [{col: row[col] for col in row} for row in data.bottomup]
    roofs = data.get_roofs()
    # Get the entries into a data frame.
    df = pd.DataFrame(rows).replace("", np.nan)
    df.to_csv("plots/roofline_plots/"+name+".csv", sep='\t')

    # Arithmetic Intensity and GFLOPS
    df.self_ai = df.self_ai.astype(float)
    df.self_gflops = df.self_gflops.astype(float)

    # Provision plot and determine maxes.
    df.self_ai = df.self_ai.astype(float)
    df.self_gflops = df.self_gflops.astype(float)
    df.self_time = df.self_time.astype(float)

    # Add time weight column
    loop_total_time = df.self_time.sum()
    df['percent_weight'] = df.self_time / loop_total_time * 100
    print(loop_total_time)
    print(df.self_time)
    print(df['percent_weight'])
    print(df.loop_function_id)
    print(df.self_gflops)
    print(df.self_gflop)
    print(df.self_memory_gb)
    _, ax = plt.subplots()
    def key(roof): return roof.bandwidth if 'bandwidth' not in roof.name.lower() else 0
    max_compute_roof = max(roofs, key=key)
    max_compute_bandwidth = max_compute_roof.bandwidth / \
        math.pow(10, 9)  # as GByte/s
    max_compute_bandwidth /= scale  # scale down as requested by the user

    # Scale based only on single thread
    def key2(roof): return roof.bandwidth if 'bandwidth' in roof.name.lower(
    ) and 'single-thread' in roof.name.lower() else 0
    max_memory_roof = max(roofs, key=key2)
    max_memory_bandwidth = max_memory_roof.bandwidth / \
        math.pow(10, 9)  # as GByte/s
    max_memory_bandwidth /= scale  # scale down as requested by the user

    # Parameters to center the chart
    # ai_min = 2**-5
    ai_max = 2**5
    # gflops_min = 2**0
    width = ai_max

    # Declare the two types of rooflines
    memory_roofs = []
    compute_roofs = []

    roofs = filter_roofs(roofs, EXCLUDE)
    for roof in roofs:
        # We only use a single thread
        if 'single-thread' in roof.name:
            # memory roofs
            if 'bandwidth' in roof.name.lower():
                bandwidth = roof.bandwidth / math.pow(10, 9)  # as GByte/s
                bandwidth /= scale  # scale down as requested by the user
                # y = bandwidth * x
                x1, x2 = 0, min(width, max_compute_bandwidth / bandwidth)
                y1, y2 = 0, x2*bandwidth
                label = '{} {:.0f} GB/s'.format(roof.name, bandwidth)
                print(roof.name.lower())

                if "dram" in roof.name.lower():
                    plt.axvline(x=x1, color='darkgrey',
                                ymax=y2, linestyle=(0, (2, 2)))

                ax.plot([x1, x2], [y1, y2], '-', label=label.replace("(single-threaded)", ""))
                memory_roofs.append(((x1, x2), (y1, y2)))

            # compute roofs
            # elif precision == 'all' or precision in roof.name:
            elif not "dp" in roof.name.lower():
                bandwidth = roof.bandwidth / math.pow(10, 9)  # as GFlOPS
                bandwidth /= scale  # scale down as requested by the user
                x1, x2 = max(bandwidth / max_memory_bandwidth, 0), width
                y1, y2 = bandwidth, bandwidth
                label = '{} {:.0f} GFLOPS'.format(roof.name, bandwidth)
                ax.plot([x1, x2], [y1, y2], '-', label=label.replace("(single-threaded)", ""))
                print(roof.name.lower())
                if "l1" in roof.name.lower():
                    plt.axvline(x=x1, color='darkgrey',
                                ymax=y2, linestyle=(0, (2, 2)))
                compute_roofs.append(((x1, x2), (y1, y2)))

    # Draw points using the same axis.
    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)

    # Choose better colors
    colors = cm.viridis(np.linspace(0, 1, len(df.self_ai)))
    markers = [".", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p",
               "P", "*", "h", "H", "+", "x", "X", "D", "d", 4, 5, 6, 7, 8, 9, 10, 11]
    for i in range(len(df.self_ai)):
        if not math.isnan(df.self_ai[i]) and not math.isnan(df.self_gflops[i]):
            print("LOOPS")
            print(df.function_call_sites_and_loops[i], " ", df.loop_function_id[i],
                  " ", df.self_ai[i], " ", df.self_gflops[i], " ", df.self_time[i])
            for entry in LOOPS_AND_FUNCTIONS:
                for indentifier in LOOPS_AND_FUNCTIONS[entry]["identifiers"]:
                    if indentifier in df.function_call_sites_and_loops[i]:
                        LOOPS_AND_FUNCTIONS[entry]["gflop"].append(
                            float(df.self_gflop[i]))
                        LOOPS_AND_FUNCTIONS[entry]["bytes"].append(
                            float(df.self_memory_gb[i]))
                        LOOPS_AND_FUNCTIONS[entry]["time"].append(
                            float(df.self_time[i]))
                        print("Found ", indentifier)
                        break
        else:
            print(df.function_call_sites_and_loops[i], " is nan")
    print(LOOPS_AND_FUNCTIONS)

    for i, entry in enumerate(LOOPS_AND_FUNCTIONS):
        gflop_byte = sum(
            LOOPS_AND_FUNCTIONS[entry]["gflop"])/sum(LOOPS_AND_FUNCTIONS[entry]["bytes"])
        gflops = sum(LOOPS_AND_FUNCTIONS[entry]["gflop"]) / \
            sum(LOOPS_AND_FUNCTIONS[entry]["time"])
        time = sum(LOOPS_AND_FUNCTIONS[entry]["time"])
        name_str = "Name: ".ljust(20, ' ') + str(entry)
        time_str = "Time: ".ljust(22, ' ') + str(round(time, 2)) + " s,  Perf: ".ljust(
            16, ' ') + str(round(gflops, 2)) + " GFLOPs"

        # Combine the strings
        label = name_str + "\n" + time_str 

        ax.plot(gflop_byte, gflops, marker=markers[i],
                color=colors[i], label=label)

    # for i in range(len(df.self_ai)):
    #    ax.plot(df.self_ai[i], df.self_gflops[i], marker=markers[i],
    #            color=colors[i], label=format_label(df.function_call_sites_and_loops[i])+" "+str(df.self_time[i])+"s")

    ax.set_xlabel('Operational intensity (FLOP/Byte)', fontsize=14)

    # Set the legend of the plot.
    plt.legend(loc='lower right', prop={'size': 10}, shadow=True)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    ax = plt.gca()
    ax.xaxis.get_major_formatter()._usetex = False
    ax.yaxis.get_major_formatter()._usetex = False
    plt.text(0.0, 1, 'Performance (GFLOPS)',
             fontsize=14, color='k',
             ha='left', va='bottom',
             transform=plt.gca().transAxes)
    plt.title(r'\textbf{' + 'Roofline for Opt-V' + '}',
              fontsize=14, y=1.04, loc='left', fontweight="bold")

    # Save the plot in PNG format.
    #plt.savefig('plots/roofline_plots/%s_combined.svg' %
    #            name, bbox_extra_artists=(legend,),  bbox_inches='tight', dpi=300)
    plt.savefig('plots/roofline_plots/%s_combined.svg' %
                name,  bbox_inches='tight', dpi=500)


def format_label(label):
    label = label.split("<")[0]
    label = label.replace("apply", "")
    label = label.replace(
        "_ZNK8polytope4walkEPfS0_PKfS2_PKDv8_fS5_fRN10XoshiroCpp18Xoshiro128PlusPlusE", "polytope::walk")
    label = label.strip("[]")
    return label


def filter_roofs(strings, exclude):
    return [s for s in strings if not any(ex in s.name for ex in exclude)]


if __name__ == '__main__':
    roofline()
