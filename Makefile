CXX=g++
CLANG=clang++

BOOST_INCLUDE_FLAG = -I /usr/include

LIB_FLAGS = -larmadillo -llapack -lblas -lglpk -lgfortran
OPT = -O3 -march=native -ffast-math
NODEBUG = -DARMA_NO_DEBUG -DNDEBUG
DEBUG = -g -Wall

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

clean:
	rm -f polyvol
