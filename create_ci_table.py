import os
import numpy as np
import scipy.stats as stats
import utils
import scipy.stats
import scipy 
# Script to create a LaTeX table with the precomputed data for confidence intervals


# Set the directory containing your log files
DIRECTORY = "volumes/polyvest-o3-native-fastmath"
DIRECTORY = "volumes/finalopt-x"
#DIRECTORY = "volumes/reduce-precision_polyvol"
#EXECUTABLE = "reduced\\_precision"
#EXECUTABLE = "\\_aligned\\-vec"
EXECUTABLE = "finalopt-x"


# Get a list of all log files in that directory
log_files = [f for f in os.listdir(DIRECTORY) if f.endswith('.log')]
log_files.sort(key=utils.extract_number_table)

# Function to compute confidence interval


def other_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    print("a ", a)
    n = len(a)
    print("n ", n)
    
    m, se = np.mean(a), stats.sem(a)
    print("m, se ", m, se)
    print("DATA ", data)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    stats.norm.interval(0.95, loc=m, scale=std_dev)
    return m-h, m+h

def confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    confidence_interval = stats.norm.interval(0.95, loc=np.mean(a), scale=std_dev)
    print(confidence_interval[0])
    print(confidence_interval[1])
    print(confidence_interval)
    return confidence_interval[0], confidence_interval[1]

# Start the LaTeX document
latex_doc = "\\documentclass{article}\n"
latex_doc += "\\usepackage{booktabs}\n"
latex_doc += "\\usepackage{tabularx}\n"
latex_doc += "\\usepackage{makecell}\n"
latex_doc += "\\renewcommand\\theadfont{\\scriptsize}\n"
latex_doc += "\\begin{document}\n"

# Title
executable_name = EXECUTABLE
latex_doc += "\\title{CI for " + executable_name + "}\n"
latex_doc += "\\maketitle\n"

# Start the LaTeX table
latex_doc += "\\begin{table}[ht]\n"
latex_doc += "\\centering\scriptsize\n"
latex_doc += "\\begin{tabular}{\\textwidth}{llllll}\n"
latex_doc += "\\toprule\n"
latex_doc += "\\thead[l]{Test} & \\thead[l]{Avg. vol \\\\ $\\hat{v}$} &"
latex_doc +=  "\\thead[l]{Std Dev \\\\ $\\sigma$} & \\thead[l]{95\\% CI \\\\ $\\mathcal{I}=[p,q]$} & "
latex_doc += "\\thead[l]{Error \\\\ $\\epsilon = \\frac{q-p}{\\hat{v}}$} \\\\\n"
latex_doc += "\\midrule\n"

# Iterate over the log files
for log_file in log_files:
    # Escape underscores in filenames
    test_name = log_file.split("|")[1].strip(".log").replace("_", "\\_")
    with open(os.path.join(DIRECTORY, log_file), 'r') as file:
        # Read the numeric values
        print(log_file)
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
                 {utils.format_number(error)} \\\\\n"

# End the LaTeX table
latex_doc += "\\bottomrule\n"
latex_doc += "\\end{tabular}\n"
latex_doc += "\\end{table}\n"
# End the LaTeX document
latex_doc += "\\end{document}\n"

# Save the LaTeX document to a file
with open(DIRECTORY+"/"+executable_name+'.tex', 'w') as file:
    file.write(latex_doc)
