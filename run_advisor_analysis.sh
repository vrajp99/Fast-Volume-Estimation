#!/bin/bash

EXECUTABLE="executables/bound-remove_polyvol"
TEST="examples/cube_10"
PROJEC_DIR="/home/samuki/git/team29/"


advixe-cl -collect survey -project-dir $PROJEC_DIR -- $EXECUTABLE $TEST
advixe-cl -collect tripcounts -flop -project-dir $PROJEC_DIR -- $EXECUTABLE $TEST
advixe-cl -collect roofline -project-dir $PROJEC_DIR -- $EXECUTABLE $TEST