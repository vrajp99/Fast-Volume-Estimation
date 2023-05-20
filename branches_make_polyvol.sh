# Make sure to fetch updates, but don't merge yet
git remote rm origin
git remote add origin git@gitlab.inf.ethz.ch:COURSE-ASL/asl23/team29.git
git fetch --all   # origin is default

# list all branches
for branch in $(git branch -r | grep -v HEAD); do
    echo "Checking out $branch"
    # if the branch is not the same as the remote branch...
    git checkout ${branch#origin/} &&
    git pull origin ${branch#origin/}  &&
    make &&
    cp polyvol /tmp/${branch#origin/}_polyvol;
    make clean
done

# Copy all PolyVol executables to branch
git checkout benchmarking
DIRECTORY=executables
if [ -d "$DIRECTORY" ]; then
  echo "$DIRECTORY does exist."
  rm -r $DIRECTORY
fi
mkdir $DIRECTORY
for branch in $(git branch -r | grep -v HEAD); do
    cp /tmp/${branch#origin/}_polyvol $DIRECTORY;
done
