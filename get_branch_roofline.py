import subprocess
import json
import os
import utils

# Change these variables
BRANCHES = ["baseline"]
TEST_FILE = "examples/cube_40"
    
    
def main():
    print("Disabling Turbo Boost")
    utils.toggle_turbo_boost("disable")
    print("Running roofline analysis")
    for root, _, files in os.walk("executables"):
        for executable in files:
            if executable.split("_")[0] in BRANCHES:
                executable_path = os.path.join(root, executable)
                print("Running advisor with ", executable_path)
                print("Testing on ", TEST_FILE)
                utils.run_advisor(executable_path, TEST_FILE)
    print("Enabling Turbo Boost")
    utils.toggle_turbo_boost("enable")


if __name__ == '__main__':
    main()
