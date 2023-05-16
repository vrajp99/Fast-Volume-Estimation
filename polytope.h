#ifndef POLYTOPE_H
#define POLYTOPE_H 1

#include <armadillo>
#include <vector>
#include "XoshiroCpp.hpp"

// Note : mat and vec are typedefs of the corresponding
// data structures template-instantiated for doubles

using namespace std;
using namespace arma;

class polytope {
  // The convex polytope in Ax <= b format
  size_t m, n;
  mat A;
  vec b;

  const double initEllipsoid(vec &ori);
  double preprocess();
  const double walk(vec &x, const vector<mat> &Ai, const vector<vec> &B,
                    const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng);

public:
  polytope(){};
  double estimateVol();
  void readPolytope(const char *const filename);
};

#endif
