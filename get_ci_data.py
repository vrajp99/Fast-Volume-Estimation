import subprocess
import os
import utils
import time 

# Change these variables
BRANCHES = ["finalopt-x"]
#BRANCHES = ["polyvest-o3-native-fastmath"]
#BRANCHES = ["polyvest"]
TEST_DIR = "advanced_tests/polyvest_paper_cubes"
TEST_DIR = "advanced_tests/other_paper_correctness"
TEST_DIR = "advanced_tests/paper_cubes"
#TEST_DIR = "advanced_tests/polyvest_small_cubes"

RESULTS_DIR = "volumes"
REPEATS = 100

def measure_performance(executable, file_paths):
    for path in file_paths:
        # Call C program and retrieve number of cycles
        file_name = path.split("/")[-1]
        executable_name = executable.split("/")[-1]
        if not os.path.exists(RESULTS_DIR+"/"+executable_name):
            print("Creating executables results dir")
            os.makedirs(RESULTS_DIR+"/"+executable_name)
        outfile = open(RESULTS_DIR+"/"+executable_name+"/"+"volumes_"+executable_name+"|"+file_name+".log", 'w')
        for i in range(REPEATS):
            # Account for different structure of PolyVest
            if executable_name.startswith("polyvest"):
                out = subprocess.run([executable, str(path), "1600"], capture_output = True, check=True).stdout.decode('utf-8')
                out = out.split("\n")[-2]
            else: 
                #out = float(subprocess.run([executable[:-1]+"-".join(path.split("/")[-1].split("_"))+"_polyvol", str(path)], capture_output = True, check=True).stdout.decode('utf-8'))
                out = float(subprocess.run([executable[:-1]+path.split("_")[-1]+"_polyvol", str(path)], capture_output = True, check=True).stdout.decode('utf-8'))
            time.sleep(0.5)
            # Clearing cache like this does not reliably give different results
            #os.system('sudo sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"')
            outfile.write("%s\n" % out)
        outfile.close()


def main():    
    print("Disabling Turbo Boost")
    utils.toggle_turbo_boost("disable")
    #print("Creating executables from the following branches: ", BRANCHES)
    #utils.create_executables(BRANCHES)
    print("Parsing test files")
    _, test_paths = utils.list_files_sorted(TEST_DIR)
    print("Creating results dir")
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    print("Measuring performance")
    for root, _, files in os.walk("executables"):
        for executable in files:
            if executable.split("_")[0] in BRANCHES:
                executable_path = os.path.join(root, executable)
                print("Measuring performance of ", executable_path)
                measure_performance(executable_path, test_paths)
            elif BRANCHES[0] == "finalopt-x":
                utils.toggle_turbo_boost("disable")
                executable_path = os.path.join(root, "finalopt-x")
                print("Measuring performance of ", executable_path)
                measure_performance(executable_path, test_paths)
                break
    print("Enabling Turbo Boost")
    utils.toggle_turbo_boost("enable")


if __name__ == '__main__':
    main()
