CXX=g++

BOOST_INCLUDE_FLAG = -I /usr/include

LIB_FLAGS = -larmadillo -llapack -lblas -lglpk -lgfortran
OPT = -O2
DEBUG = -DARMA_NO_DEBUG

CXXFLAGS = $(BOOST_INCLUDE_FLAG) $(DEBUG) $(OPT)

all: main

main: main.cpp polytope.h preprocess.cpp estimateVol.cpp readPolytope.cpp
    $(CXX) $(CXXFLAGS) -o polyvol main.cpp preprocess.cpp estimateVol.cpp readPolytope.cpp $(LIB_FLAGS)

clean:
    rm -f polyvol
