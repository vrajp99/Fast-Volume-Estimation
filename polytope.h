#ifndef POLYTOPE_H
#define POLYTOPE_H 1

#include <armadillo>
#include <vector>
#include "XoshiroCpp.hpp"
#include <immintrin.h>

// Note : mat and vec are typedefs of the corresponding
// data structures template-instantiated for doubles

using namespace std;
using namespace arma;

class polytope {
  // The convex polytope in Ax <= b format
  size_t m, n;
  mat A;
  vec b;

  double initEllipsoid(vec &ori);
  double preprocess();
  double walk(vec &x, vec &Ax, const vector<vec> &B, const vector < vector < __m256d > >& Agt,  const vector < vector < __m256d > >& Alt,
                    const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng);

public:
  polytope(){};
  double estimateVol();
  void readPolytope(const char *const filename);
};

#endif
