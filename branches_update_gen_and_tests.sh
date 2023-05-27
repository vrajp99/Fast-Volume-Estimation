#!/usr/bin/env bash

# Branches update tests

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
      git branch --set-upstream-to=origin/${branch#origin/} ${branch#origin/} &&
      git pull origin ${branch#origin/}  &&
      cp /tmp/gen.py . &&
      rm -r tests &&
      cp -r /tmp/tests . &&
      git add tests &&
      git add gen.py &&
      git commit -m "Update tests and gen.py" &&
      git push --set-upstream origin ${branch#origin/}
    fi
  done
done

