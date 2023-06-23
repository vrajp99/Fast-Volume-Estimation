# Team 29 - Volume Estimation
## Team Members:
- Samuel Kiegeland
- S Deepak Narayanan
- Vraj Patel
- Raghu Raman Ravi

## Project Repository Structure:
Here we highlight where the code corresponding to the various stages in the optimizations refered to in our report can be found:
- **Baseline**: Refer to git branch `baseline`
- **Optimization-I**: Refer to git branch `bound-remove`
- **Optimization-II**: Refer to git branch `fast-linalg`
- **Optimization-III**: Refer to git branch `vecplusextraoptim`
- **Optimization-IV**: Refer to git branch `reduce_precision`
- **Optimization-V**: Refer to git branch `main`

All of our benchmarking, profiling, hotspot analysis and roofline analysis was performed on a separate branch:
- **Benchmarks**: Refer to git branch `benchmarking`

## Project Dependencies:
In terms of external dependencies, we require the presence of the following libraries and tools at minimum to be able to build and run the code:
- GCC 11
- Armadillo
- Lapack
- BLAS
- GLPK

## Build instructions:
Once you are in the suitable branch, 
- **GCC Build**: Run `make`
- **Clang Build**: Run `make clang`
- **Debug Build**: Run `make debug`

**Note**: For the branch `main`, if you want to compile with specific input sizes in mind, you need to modify the `#define M m` and `#define N n` lines in the file `estimateVol.cpp` to the desired dimensions.  

## Running the executable:
The executable `polyvol` is generated at the end of the build process. It can then be utilized as follows:
```bash
./polyvol [input-file-name]
```

The format for the input file is as follows:
- The first line contains the space-separated integers $m$ and $n$.
- $m$ lines follow, each containing $n+1$ space-separated numbers (`float` or `int`). The number in the $j$<sup>th</sup> column of the $i$<sup>th</sup> line represents $A_{ij}$ for $1 \le j \le n$ and $B_j$ for $j=n+1$.

## Generation of testcases:
To generate the testcases, you can run `gen.py` as follows:
```bash
python3 gen.py
```

The description and precise definition of the polytopes generated can be found in the report. 

## Testing:
Once you have run the testcase generation script at least once, to populate the `./tests/` directory with the appropriate input files, you can now test the correctness of the built executable. To do so, you can to run `test.py` as follows:
```bash
python3 test.py
```

This above will build and test the output of the default target of the make file. You can choose another build target to test as follows:
```bash
python3 test.py [build-target-name]
```

## Profile Guided Optimization:
The test profile guided optimization, first ensure that you are on the branch `pgo` and have the run the test case generation file. Then you just need to run `make pgo_gen`. This generates the executable `polyvol_pgo` which can then be used as follows:
```bash
./polyvol_pgo [input-file-name]
```

## All code in single file:
To test how the default build target performs when all code is present in a single file instead of being split over several files, you need to be in the branch `pgo` or `onefile`. Then you just need to run `make onefile`. This creates the `polyvol` executable which can then be used as described previously. 

## Benchmarking: 
To recreate our benchmarks or perform roofline analysis head over to the `benchmarking` branch: 
```
git checkout benchmarking

``` 
To pull executables from a different branch run:
```
bash branches_make_polyvol.sh branch_name

``` 
To run the performance analysis on multiple branches and tests with Linux perf, modify `get_branch_performance_FLOPc_polytopes.py` to the desired branches and test cases and then run: 
```
python get_branch_performance_FLOPc_polytopes.py

``` 
Upon execution, the script disables the turbo-boost with `turbo-boost.sh` and measures cycles, runtime and flop counts with Linux perf. The outputs are saves under `results/`  
The performance can be plotted with
```
python plot_branch_performance.py

``` 
The speedup can be plotted with
```
python plot_speedup.py

``` 
To run the intel advisor to create data for the roofline plots, run
```
bash run_advisor_analysis.sh

``` 
The outputs are saved under `advisor_output` and can be plotted using
```
python plot_roofline.py --project advisor_output/project_name --name out_file_name

``` 
