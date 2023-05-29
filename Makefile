CXX=g++
CLANG=clang++

BOOST_INCLUDE_FLAG = -I /usr/include

LIB_FLAGS = -larmadillo -llapack -lblas -lglpk -lgfortran
OPT = -O3 -march=native -ffast-math
NODEBUG = -DARMA_NO_DEBUG -DNDEBUG
DEBUG = -g -Wall
PGO_MEASURE = -fprofile-dir=./profile_data/pgo -fprofile-generate=./profile_data/pgo
PGO_GEN = -fprofile-dir=./profile_data/pgo -fprofile-use=./profile_data/pgo -fprofile-correction

CXXFLAGS = $(BOOST_INCLUDE_FLAG) $(NODEBUG) $(OPT)
CXXDEBUGFLAGS = $(BOOST_INCLUDE_FLAG) $(DEBUG) $(OPT)

all: main

main: main.cpp polytope.h preprocess.cpp estimateVol.cpp readPolytope.cpp
	$(CXX) $(CXXFLAGS) -o polyvol main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

debug: main.cpp polytope.h preprocess.cpp estimateVol.cpp readPolytope.cpp
	$(CXX) $(CXXDEBUGFLAGS) -o polyvol main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

clang: main.cpp polytope.h preprocess.cpp estimateVol.cpp readPolytope.cpp
	$(CLANG) $(CXXFLAGS) -std=c++20 -o polyvol main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

onefile: main.cpp polytope.h preprocess.cpp estimateVol.cpp readPolytope.cpp onefiler.py
	python3 onefiler.py
	$(CXX) $(CXXFLAGS) -o polyvol_onefile polyvol_single_file.cpp $(LIB_FLAGS)

pgo_measure: main.cpp polytope.h preprocess.cpp estimateVol.cpp readPolytope.cpp pgo_clean
	$(CXX) $(CXXFLAGS) $(PGO_MEASURE) -o polyvol_pgo main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

pgo_measure_run: pgo_measure
	./polyvol_pgo ./tests/cube_20
	./polyvol_pgo ./tests/cube_30
	./polyvol_pgo ./tests/cube_40
	./polyvol_pgo ./tests/cube_50
	./polyvol_pgo ./tests/cube_60
	./polyvol_pgo ./tests/cube_70
	./polyvol_pgo ./tests/cube_80
	./polyvol_pgo ./tests/simplex_20
	./polyvol_pgo ./tests/simplex_30
	./polyvol_pgo ./tests/simplex_40
	./polyvol_pgo ./tests/cross_8
	./polyvol_pgo ./tests/cross_9
	./polyvol_pgo ./tests/cross_10
	./polyvol_pgo ./tests/cross_13
	./polyvol_pgo ./tests/cuboid_7
	./polyvol_pgo ./tests/cuboid_8
	./polyvol_pgo ./tests/cuboid_9
	./polyvol_pgo ./tests/cuboid_10



pgo_gen: pgo_measure pgo_measure_run
	$(CXX) $(CXXFLAGS) $(PGO_GEN) -o polyvol_pgo main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

pgo_clean: 
	rm -rf ./profile_data

clean:
	rm -f polyvol
