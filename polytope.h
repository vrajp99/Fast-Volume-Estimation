#ifndef POLYTOPE_H
#define POLYTOPE_H 1

#include <armadillo>
#include <vector>

// Note : mat and vec are typedefs of the corresponding
// data structures template-instantiated for doubles

using namespace std;
using namespace arma;

class polytope {
  // The convex polytope in Ax <= b format
  size_t m, n;
  mat A;
  vec b;

  // Paramters required for volume computation
  double beta;
  double determinant;

  int randi(int n) { return rand() % n; }

  // Define and use if needed for walk
  // vector < vec > B;
  // vector < mat > Ai;

public:
  polytope(){};

  const double initEllipsoid(vec &ori);
  void preprocess();
  double estimateVol();
  const void walk(vec &x, size_t k);
  bool checkInBall(vec &x, size_t k);

  void readPolytope(const char *const filename);
};

#endif
