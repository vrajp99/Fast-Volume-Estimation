# Adapted from intel advisor api examples https://www.intel.com/content/www/us/en/developer/articles/training/how-to-use-the-intel-advisor-python-api.html
# Copyright (C) 2017 Intel Corporation

import math
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import click
# This style requires $DISPLAY available.
# Use it instead of matplotlib.use('Agg') if you have GUI environment
# matplotlib.style.use('ggplot')

pd.options.display.max_rows = 20

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
@click.option('--mode', '-m', type=click.Choice(['overview', 'top-loops', 'all']),
              default='overview', required=True,
              help='overview: Display a single point with the total GFLOPS and '
                   'arithmetic intensity of the program.\n top-loops: Display all the '
                   'top time consuming loops within one order of magnitude (x10) from '
                   'the most time consuming loop.')
@click.option('--th', default=0, help='Percentage threshold (e.g. 95) such that loops '
                                      'under this value in execution time consumed will '
                                      'not be displayed/collected.'
                                      'Only valid for --top-loops.')
# Open the Advisor Project and load the data.
def roofline(project, scale, precision, mode, th):
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
    for idx, entry in enumerate(data.bottomup):
        # Process the header.
        if idx == 0:
            print(",".join([quotes(key) for key in entry]))

        # Process the entires.
        print(",".join([quotes(entry[key]) for key in entry]))
    # Access the entries and roof data from the survey data.
    rows = [{col: row[col] for col in row} for row in data.bottomup]
    roofs = data.get_roofs()

    # Get the entries into a data frame.
    df = pd.DataFrame(rows).replace("", np.nan)
    print(df[["self_ai", "self_gflops"]].dropna())
    print(df.head(5))
    df.self_ai = df.self_ai.astype(float)
    df.self_gflops = df.self_gflops.astype(float)
    #print(df.function)
    print(df.function_call_sites_and_loops)

    # Provision plot and determine maxes.
    df.self_ai = df.self_ai.astype(float)
    df.self_gflops = df.self_gflops.astype(float)
    df.self_time = df.self_time.astype(float)

    # Add time weight column
    loop_total_time = df.self_time.sum()
    df['percent_weight'] = df.self_time / loop_total_time * 100

    fig, ax = plt.subplots()
    key = lambda roof: roof.bandwidth if 'bandwidth' not in roof.name.lower() else 0
    max_compute_roof = max(roofs, key=key)
    max_compute_bandwidth = max_compute_roof.bandwidth / math.pow(10, 9)  # as GByte/s
    max_compute_bandwidth /= scale  # scale down as requested by the user

    key = lambda roof: roof.bandwidth if 'bandwidth' in roof.name.lower() else 0
    max_memory_roof = max(roofs, key=key)
    max_memory_bandwidth = max_memory_roof.bandwidth / math.pow(10, 9)  # as GByte/s
    max_memory_bandwidth /= scale  # scale down as requested by the user

    # Parameters to center the chart
    ai_min = 2**-5
    ai_max = 2**5
    gflops_min = 2**0
    width = ai_max

    # Declare the dictionary that will hold the JSON information
    roofline_data = {}

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
                compute_roofs.append(((x1, x2), (y1, y2)))
    palette = sns.color_palette("Paired")
    # Draw points using the same axis.
    ax.set_xscale("log")
    ax.set_yscale("log")
    # color=palette[df.index.astype(int)]
    ax.plot(df.self_ai, df.self_gflops, "o", label=df.function_call_sites_and_loops)
    # Set the legend of the plot.
    legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),
                            prop={'size': 7}, title='Rooflines')
    # Save the plot in PNG format.
    plt.savefig("roofline_plots/roofline.png", bbox_inches='tight')

    print("Roofline chart has been generated and saved into roofline.png and roofline.svg files in the current directory.")
    
if __name__ == '__main__':
    roofline()
