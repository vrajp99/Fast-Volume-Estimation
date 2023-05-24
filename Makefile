CXX=g++
CLANG=clang++

BOOST_INCLUDE_FLAG = -I /usr/include

LIB_FLAGS = -larmadillo -llapack -lblas -lglpk -lgfortran
OPT = -O3 -march=native
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
	$(CLANG) $(CXXFLAGS) -DARMA_NO_DEBUG -std=c++20 -o polyvol main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

clean:
	rm -f polyvol
