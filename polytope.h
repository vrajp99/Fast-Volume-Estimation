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
  const void walk(float* norm, float* x, float* Ax, const float* B, const float* A_negrecp, const float* Agt,  const float* Alt, const float rk, XoshiroCpp::Xoshiro128PlusPlus &rng) const;

public:
  polytope(){};
  void preprocess();
  const double estimateVol() const;
  void readPolytope(const char *const filename);
};

#endif
