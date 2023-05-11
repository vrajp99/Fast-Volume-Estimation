#include "polytope.h"
#include <cassert>

double norm_2(vec &x) {
  double norm = 0;
  for (size_t i = 0; i < x.n_elem; i++) {
    norm = norm + x(i) * x(i);
  }
  return norm;
}

double unitBallVol(size_t n) {
  if (n >= 2) {
    return ((2 * M_PI) / n) * unitBallVol(n - 2);
  } else if (n == 1) {
    return 2;
  } else {
    return 1;
  }
}

const double polytope::walk(vec &x, const vector<mat> &Ai, const vector<vec> &B,
                            const double rk) {
  // Choose coordinate direction
  int dir = (rand() % n);

  double r, max, min, C = 0;

  C = norm_2(x);
  C -= x(dir) * x(dir);

  r = sqrt(rk - C);
  max = r - x(dir), min = -r - x(dir);

  vec bound = B[dir] - Ai[dir] * x;
  for (size_t i = 0; i < m; i++) {
    if (A(i, dir) > 0 && bound(i) < max)
      max = bound(i);
    else if (A(i, dir) < 0 && bound(i) > min)
      min = bound(i);
  }

  double randval = (((double)rand() * (max - min)) / RAND_MAX) + min;
  double t = x(dir) + randval;
  x(dir) = t;
  assert(min <= randval && randval <= max);

  return (C + t * t);
}

double polytope::estimateVol() {
  double gamma = preprocess();
  long l = ceill(n * log2(2 * n));
  long step_sz = 1600 * l;
  long count = 0;
  vec x;
  x.zeros(n);
  vector<long> t(l + 1, 0);
  vector<double> alpha(l, 0);

  // Precomputing Ai and B
  vector<vec> B(n);
  vector<mat> Ai(n);
  rowvec exp(n);
  exp.ones();
  for (size_t i = 0; i < n; ++i) {
    Ai[i] = A / (A.col(i) * exp);
    B[i] = b / A.col(i);
  }

  // Precomputing radii
  vector<double> r2(l + 1);
  for (size_t i = 0; i <= l; ++i)
    r2[i] = pow((double)2.0, (double)(2.0 * i) / n);

  for (int k = l - 1; k >= 0; k--) {
    for (long i = count; i < step_sz; i++) {
      double x_norm = walk(x, Ai, B, r2[k + 1]);
      if (x_norm <= r2[0]) {
        t[0]++;
      } else if (x_norm <= r2[k]) {
        long m = ceill(((double)n) / 2 * log2(x_norm));
        t[m]++;
        assert(m <= k);
      }
    }
    count = 0;
    for (size_t i = 0; i <= k; i++) {
      count += t[i];
    }

    // Alpha has to be >= 1
    if (count > step_sz) {
      count = step_sz;
      cout << "WTF" << endl;
    }
    alpha[k] = ((double)step_sz) / count;
    double factor = pow(2.0, -1.0 / n);
    for (size_t i = 0; i < n; i++) {
      x(i) = x(i) * factor;
    }
  }

  double res = gamma;
  for (size_t i = 0; i < l; i++) {
    res *= alpha[i];
  }
  res *= unitBallVol(n);
  return res;
}
