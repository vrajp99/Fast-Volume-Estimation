#ifndef POLYTOPE_H
#define POLYTOPE_H

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

  double gamma;

  const double initEllipsoid(vec &ori);
  const double walk(vec &x, vec &Ax, const double* B, const mat &A_negrecp, const vector < vector < __m256d > >& Agt,  const vector < vector < __m256d > >& Alt, const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng) const;

public:
  polytope(){};
  void preprocess();
  const double estimateVol() const;
  void readPolytope(const char *const filename);
};

#endif
