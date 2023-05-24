#!/usr/bin/env bash

# <description>
#
# Usage:
#  $ ./branches_make_polyvol.sh param1 
# * param1: branch to pull the executable from

# Read branches
IFS=' ' read -r -a desired_branches <<< "$1"
# Make sure to fetch updates, but don't merge yet
git remote rm origin
git remote add origin git@gitlab.inf.ethz.ch:COURSE-ASL/asl23/team29.git
git fetch --all   # origin is default

# list all branches
for branch in $(git branch -r | grep -v HEAD); do
  for desired_branch in "${desired_branches[@]}"; do
    if [[ "$desired_branch" == ${branch#origin/} ]]; then
      echo "Checking out $branch"
      # if the branch is not the same as the remote branch...
      git checkout ${branch#origin/} &&
      git pull origin ${branch#origin/}  &&
      make &&
      cp polyvol /tmp/${branch#origin/}_polyvol;
      make clean
    fi
  done
done

# Copy all PolyVol executables to branch
git checkout benchmarking
DIRECTORY=executables
if ! [ -d "$DIRECTORY" ]; then
  echo "Creating $DIRECTORY"
  mkdir $DIRECTORY
fi
for branch in $(git branch -r | grep -v HEAD); do
  for desired_branch in "${desired_branches[@]}"; do
    if [[ "$desired_branch" == ${branch#origin/} ]]; then
      cp /tmp/${branch#origin/}_polyvol $DIRECTORY;
    fi
  done
done
