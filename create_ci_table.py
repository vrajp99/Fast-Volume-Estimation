import os
import numpy as np
import scipy.stats as stats
import re
import utils

# Set the directory containing your log files
DIRECTORY = "volumes"


# Get a list of all log files in that directory
log_files = [f for f in os.listdir(DIRECTORY) if f.endswith('.log')]
log_files.sort(key=utils.extract_number_table)

# Function to compute confidence interval


def confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return m-h, m+h


# Start the LaTeX document
latex_doc = "\\documentclass{article}\n"
latex_doc += "\\usepackage{booktabs}\n"
latex_doc += "\\usepackage{tabularx}\n"
latex_doc += "\\usepackage{makecell}\n"
latex_doc += "\\renewcommand\\theadfont{\\scriptsize}\n"
latex_doc += "\\begin{document}\n"

# Title
executable_name = "volumes\\_aligned\\-vec"
latex_doc += "\\title{CI for " + executable_name + "}\n"
latex_doc += "\\maketitle\n"

# Start the LaTeX table
latex_doc += "\\begin{table}[ht]\n"
latex_doc += "\\centering\scriptsize\n"
latex_doc += "\\begin{tabularx}{\\textwidth}{Xlllll}\n"
latex_doc += "\\toprule\n"
latex_doc += "\\thead[l]{Test} & \\thead[l]{Avg. vol \\\\ $\\hat{v}$} &"
latex_doc +=  "\\thead[l]{Std Dev \\\\ $\\sigma$} & \\thead[l]{95\\% CI \\\\ $\\mathcal{I}=[p,q]$} & "
latex_doc += "\\thead[l]{Freq on \\\\ $\\mathcal{I}$} & \\thead[l]{Error \\\\ $\\epsilon = \\frac{q-p}{\\hat{v}}$} \\\\\n"
latex_doc += "\\midrule\n"

# Iterate over the log files
for log_file in log_files:
    # Escape underscores in filenames
    test_name = log_file.split("|")[1].strip(".log").replace("_", "\\_")
    with open(os.path.join(DIRECTORY, log_file), 'r') as file:
        # Read the numeric values
        data = [float(line.strip()) for line in file]
        # Compute the statistics
        avg = np.mean(data)
        std_dev = np.std(data)
        conf_int = confidence_interval(data)
        freq = np.mean((data >= conf_int[0]) & (data <= conf_int[1]))
        error = (conf_int[1] - conf_int[0]) / avg

        # Add a row to the LaTeX table
        latex_doc += f"{test_name} & {utils.format_number(avg)} & \
            {utils.format_number(std_dev)} & [{utils.format_number(conf_int[0])}, {utils.format_number(conf_int[1])}] & \
                {utils.format_number(freq)} & {utils.format_number(error)} \\\\\n"

# End the LaTeX table
latex_doc += "\\bottomrule\n"
latex_doc += "\\end{tabularx}\n"
latex_doc += "\\end{table}\n"
# End the LaTeX document
latex_doc += "\\end{document}\n"

# Save the LaTeX document to a file
with open(DIRECTORY+"/"+executable_name+'.tex', 'w') as file:
    file.write(latex_doc)
