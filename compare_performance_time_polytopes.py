import os
import re
import pandas as pd
import utils

# Define test cases and executables
simplices = ["simplex_1", "simplex_5", "simplex_10", "simplex_15", "simplex_20", "simplex_30", "simplex_40", "simplex_50", "simplex_60", "simplex_70", "simplex_80"]
cuboids = ["cuboid_1", "cuboid_5", "cuboid_10", "cuboid_15", "cuboid_20", "cuboid_30", "cuboid_40"]
crosses = ["cross_1", "cross_2", "cross_3", "cross_4", "cross_5", "cross_6", "cross_7", "cross_8", "cross_9", "cross_10", "cross_13"]
rh = ["rh_1_2", "rh_1_3", "rh_2_5", "rh_4_10", "rh_5_10", "rh_5_12", "rh_10_20", "rh_10_25", "rh_10_30", "rh_15_30", "rh_15_50", "rh_20_50", "rh_20_100", "rh_30_100", "rh_40_100"]

test_cases = cuboids+simplices+crosses+rh

executables = ["finalopt-x", "polyvest-o3-native-fastmath"]

# Define directory
dir_path = "results"

# Prepare a dictionary to hold the data
data_dict = {tc: {} for tc in test_cases}

# Regular expression patterns to find the relevant lines in the file
flops_pattern = re.compile(r".*FP_ARITH_INST_RETIRED.128B_PACKED_SINGLE\s+#\s+(\d+\.\d+)\s+FLOPc")
time_pattern = re.compile(r".*(\d+\.\d+)\s+\+\-\s+\d+\.\d+\s+seconds time elapsed")

# Loop over executables and test cases
for executable in executables:
    for test_case in test_cases:
        # Generate the file name
        filename = f"{executable}_polyvol_{test_case}.txt"
        full_path = os.path.join(dir_path, filename)

        # Check if file exists
        if not os.path.isfile(full_path):
            print(f"File {filename} not found.")
            continue

        # Open the file and read the lines
        with open(full_path, 'r') as f:
            lines = f.readlines()

        # Find the lines with the measurements
        flops_line = next((line for line in lines if flops_pattern.match(line)), None)
        time_line = next((line for line in lines if time_pattern.match(line)), None)

        # Extract the measurements
        if flops_line and time_line:
            flops = float(flops_pattern.match(flops_line).group(1))
            time = float(time_pattern.match(time_line).group(1))

            # Save the data
            data_dict[test_case][(utils.BRANCH_NAME_DICT[executable], "FLOPc")] = flops
            data_dict[test_case][(utils.BRANCH_NAME_DICT[executable], "Time")] = round(time, 2)

# Convert the dictionary to a pandas DataFrame and reorganize columns
df = pd.DataFrame(data_dict).T
df.columns = pd.MultiIndex.from_tuples(df.columns)

# Print the data
print(df)

# Convert the DataFrame to a booktabs latex table
latex_table = df.to_latex(index=True, multirow=True)

print(latex_table)

