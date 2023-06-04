import pandas as pd

PATH="plots/roofline_plots/reduce-precision_polyvol_cube_80"

# Specify the columns you want to keep
columns_to_keep = ["function_call_sites_and_loops",
                   "self_gflop", "self_gflops", "self_giga_op", "self_giga_ops"]

# Load the csv file
df = pd.read_csv(PATH+'.csv', sep='\t')
#print(df.head)
#for c in df.columns:
#    print(c, "\n")
print(len(df.columns))
# Keep only the columns specified
#df = df[[col for col in df.columns if any(sub in col for sub in columns_to_keep)]]
df = df[columns_to_keep]


# Write the data to a new csv file
df.to_csv(PATH+'_readable.csv', index=False, sep='\t')
