#!/bin/bash

# Take a PolyVol executable and a testcase and run the advisor roofline analysis
#
# Usage:
#  $ ./run_advisor_analysis.sh [param1] [param2] [param3] 
# * param1 (Optional): path to executable
# * param2 (Optional): path to testcase
# * param3 (Optional): path to output dir

ADVISOR_OUTPUT_PATH="advisor_output"

EXECUTABLE=${1:-"executables/finalopt-100-debug_polyvol"}
EXECUTABLE_NAME=(${EXECUTABLE//// })
TEST=${2:-"advanced_tests/cube_tests/cube_100"}
TEST_NAME=(${TEST//// }) 
PROJEC_DIR=${3:-"/home/samuki/git/team29/${ADVISOR_OUTPUT_PATH}/${EXECUTABLE_NAME[1]}_${TEST_NAME[1]}"}

echo "$ARG1"
echo "$ARG2"
echo "$ARG3"

if ! [ -d "$ADVISOR_OUTPUT_PATH" ]; then
  echo "Creating $ADVISOR_OUTPUT_PATH"
  mkdir $ADVISOR_OUTPUT_PATH
fi

if ! [ -d "$PROJEC_DIR" ]; then
  echo "Creating $PROJEC_DIR"
  mkdir $PROJEC_DIR
fi


advixe-cl -collect survey -project-dir $PROJEC_DIR -- $EXECUTABLE $TEST
advixe-cl -collect tripcounts -flop -project-dir $PROJEC_DIR -- $EXECUTABLE $TEST
advixe-cl -collect roofline -project-dir $PROJEC_DIR -- $EXECUTABLE $TEST