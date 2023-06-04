# Adapted from intel advisor api examples https://www.intel.com/content/www/us/en/developer/articles/training/how-to-use-the-intel-advisor-python-api.html
# Copyright (C) 2017 Intel Corporation

import matplotlib.cm as cm
import click
import seaborn as sns
from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt
import math
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")


# This style requires $DISPLAY available.
# Use it instead of matplotlib.use('Agg') if you have GUI environment
# matplotlib.style.use('ggplot')

pd.options.display.max_rows = 20
plt.style.use('seaborn-darkgrid')
plt.figure(dpi=200)
# Set the default font size
plt.rcParams.update({'font.size': 14})

try:

    import advisor
    print("worked")

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
              help='Arithmetic precision.', default='SP')
# Open the Advisor Project and load the data.
def roofline(name, project, scale, precision):
    project = advisor.open_project(project)
    # Open the Advisor Project and load the data.
    data = project.load(advisor.ALL)
    def quotes(value):
        value = value.replace("\n", "")
        value = value.replace("\r", "")
        if "," in value:
            return '"{}"'.format(value)
        return str(value)
    # Iterate over the entries in the bottomup table and print a joined version.
    """
    for idx, entry in enumerate(data.bottomup):
        # Process the header.
        if idx == 0:
            print(",".join([quotes(key) for key in entry]))
        # Process the entires.
        print(",".join([quotes(entry[key]) for key in entry]))
    """
    # Access the entries and roof data from the survey data.
    rows = [{col: row[col] for col in row} for row in data.bottomup]
    roofs = data.get_roofs()

    # Get the entries into a data frame.
    df = pd.DataFrame(rows).replace("", np.nan)
    df.to_csv("plots/roofline_plots/"+name+".csv", sep='\t')

    df.self_ai = df.self_ai.astype(float)
    df.self_gflops = df.self_gflops.astype(float)

    # Provision plot and determine maxes.
    df.self_ai = df.self_ai.astype(float)
    df.self_gflops = df.self_gflops.astype(float)
    df.self_time = df.self_time.astype(float)

    # Add time weight column
    loop_total_time = df.self_time.sum()
    df['percent_weight'] = df.self_time / loop_total_time * 100

    _, ax = plt.subplots()
    def key(roof): return roof.bandwidth if 'bandwidth' not in roof.name.lower() else 0
    max_compute_roof = max(roofs, key=key)
    max_compute_bandwidth = max_compute_roof.bandwidth / \
        math.pow(10, 9)  # as GByte/s
    max_compute_bandwidth /= scale  # scale down as requested by the user

    def key2(roof): return roof.bandwidth if 'bandwidth' in roof.name.lower() else 0
    max_memory_roof = max(roofs, key=key2)
    max_memory_bandwidth = max_memory_roof.bandwidth / \
        math.pow(10, 9)  # as GByte/s
    max_memory_bandwidth /= scale  # scale down as requested by the user

    # Parameters to center the chart
    ai_min = 2**-5
    ai_max = 2**5
    gflops_min = 2**0
    width = ai_max

    # Declare the two types of rooflines dictionaries
    memory_roofs = []
    compute_roofs = []

    for roof in roofs:
        # by default drawing multi-threaded roofs only
        if 'single-thread' not in roof.name:
            # memory roofs
            if 'bandwidth' in roof.name.lower():
                bandwidth = roof.bandwidth / math.pow(10, 9)  # as GByte/s
                bandwidth /= scale  # scale down as requested by the user
                # y = bandwidth * x
                x1, x2 = 0, min(width, max_compute_bandwidth / bandwidth)
                y1, y2 = 0, x2*bandwidth
                label = '{} {:.0f} GB/s'.format(roof.name, bandwidth)
                ax.plot([x1, x2], [y1, y2], '-', label=label)
                memory_roofs.append(((x1, x2), (y1, y2)))

            # compute roofs
            elif precision == 'all' or precision in roof.name:
                bandwidth = roof.bandwidth / math.pow(10, 9)  # as GFlOPS
                bandwidth /= scale  # scale down as requested by the user
                x1, x2 = max(bandwidth / max_memory_bandwidth, 0), width
                y1, y2 = bandwidth, bandwidth
                label = '{} {:.0f} GFLOPS'.format(roof.name, bandwidth)
                ax.plot([x1, x2], [y1, y2], '-', label=label)
                plt.axvline(x=x1, color='darkgrey', ymax=y2, linestyle=(0, (2, 2)))
                compute_roofs.append(((x1, x2), (y1, y2)))
    # Draw points using the same axis.
    ax.set_xscale('log', base=2)
    ax.set_yscale('log', base=2)
    ax.set_xlabel('Operational intensity (FLOP/Byte)')
    ax.set_ylabel('Performance (GFLOPS)')

    colors = cm.viridis(np.linspace(0, 1, len(df.self_ai)))
    markers = [".",",","o","v","^","<",">","1","2","3","4","8","s","p","P","*","h","H","+","x","X","D","d","|","_",0,1,2,3,4,5,6,7,8,9,10,11]
    print(df.function_call_sites_and_loops[i])
    print()
    print(df.self_gflops[i])
    for i in range(len(df.self_ai)):
        # TODO why are main and estimateVol nan?
        if not math.isnan(df.self_ai[i]) and not math.isnan(df.self_gflops[i]):
            ax.plot(df.self_ai[i], df.self_gflops[i], marker=markers[i],
                    color=colors[i], label=df.function_call_sites_and_loops[i])
            
    # Set the legend of the plot.
    legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),
                            prop={'size': 10}, title='Rooflines/Loops')
    plt.title("Roofline for "+" ".join([n.capitalize() for n in name.split("_")]))
    # Save the plot in PNG format.
    plt.savefig('plots/roofline_plots/%s.png' %
                name, bbox_extra_artists=(legend,), bbox_inches='tight')


if __name__ == '__main__':
    roofline()
