import functools
from typing import Callable
# Source files (in order of appending
source_files = ["polytope.h", "readPolytope.cpp", "preprocess.cpp", 
                "estimateVol.cpp" , "main.cpp"]

is_file_header: Callable[[str], bool] = lambda l : not l.strip().startswith("#include \"")

with open("polyvol_single_file.cpp", "w") as final_file:
    # Add back GLPK and XoshiroCpp
    final_lines = ['#include "glpk.h"\n', '#include "XoshiroCpp.hpp"']
    for file in source_files:
        final_lines.append(f'\n // FILE: {file} \n')
        with open(file, "r") as input_file:
            lines = input_file.readlines()
            for line in filter(is_file_header, lines):
                final_lines.append(line)
    final_file.writelines(final_lines)