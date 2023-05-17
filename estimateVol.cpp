#include "polytope.h"
#include "XoshiroCpp.hpp"
#include <cassert>

double norm_2(vec &x, int n)
{
  // Loop Unrolling for ILP

  double norm = 0;
  double t1 = 0;
  double t2 = 0;
  double t3 = 0;
  double t4 = 0;
  int i;

  for (i = 0; i < n; i = i + 4)
  {
    t1 += x[i] * x[i];
    t2 += x[i + 1] * x[i + 1];
    t3 += x[i + 2] * x[i + 2];
    t4 += x[i + 3] * x[i + 3];
  }

  norm += t1 + t2 + t3 + t4;

  for (; i < n; i++)
  {
    norm += x[i] * x[i];
  }
  return norm;
}

double unitBallVol(size_t n)
{
  // Added a DP-Like structure, avoid function calls.
  double vol[n + 1];

  vol[0] = 1;
  vol[1] = 2;
  double scale = (2 * M_PI);
  for (size_t i = 2; i < n + 1; i++)
  {
    vol[i] = (scale / i) * vol[i - 2];
  }
  return vol[n];
}

double polytope::walk(vec &x, const vector<mat> &Ai, const vector<vec> &B,
                            const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng)
{
  // Choose coordinate direction
  int dir = (rng() % n);

  double r, max, min, C = 0;

  C = norm_2(x, n);
  C -= x[dir] * x[dir];

  r = sqrt(rk - C);
  max = r - x[dir], min = -r - x[dir];

  vec bound = B[dir] - Ai[dir] * x;
  for (size_t i = 0; i < m; i++)
  {
    if (A(i, dir) > 0 && bound[i] < max)
      max = bound[i];
    else if (A(i, dir) < 0 && bound[i] > min)
      min = bound[i];
  }
  
  double randval = (XoshiroCpp::FloatFromBits(rng()))*(max - min) + min;
  double t = x[dir] + randval;
  x[dir] = t;
  assert((min - 0.00001) <= randval && randval <= (max + 0.00001));

  return (C + t * t);
}

double polytope::estimateVol()
{
  double gamma = preprocess();
  // Re Declaring it Here -- Also no need to initialize Alpha Array
  double res = gamma;
  // Moved this from the bottom, got rid of the alpha array - avoid memory accesses full

  long l = ceill(n * log2(2 * n));
  long step_sz = 1600 * l;
  long count = 0;
  vec x;
  x.zeros(n);
  vector<long> t(l + 1, 0);
  // Move factor computation outside.
  double factor = pow(2.0, -1.0 / n);

  // Precomputing Ai and B
  vector<vec> B(n);
  vector<mat> Ai(n);
  rowvec exp(n);
  exp.ones();
  for (size_t i = 0; i < n; ++i)
  {
    Ai[i] = A / (A.col(i) * exp);
    B[i] = b / A.col(i);
  }

  // Precomputing radii
  double r2 [l+1];
  double pow_precomputed = pow ((double) 2.0, (double) 2.0 / n);
  // Replace Power with Just Multiplication at Each Loop
  r2[0] = 1;
  for (long i = 1; i <= l; ++i)
    r2[i] = pow_precomputed*r2[i - 1];

  // Random Generator
  XoshiroCpp::Xoshiro128PlusPlus rng(time(0));

  for (int k = l - 1; k >= 0; k--)
  {
    for (long i = count; i < step_sz; i++)
    {
      double x_norm = walk(x, Ai, B, r2[k + 1], rng);
      if (x_norm <= r2[0])
      {
        t[0]++;
      }
      else if (x_norm <= r2[k])
      {
        // Change divide by 2 to multiply by 0.5
        long m = ceill(((double)n) * 0.5 * log2(x_norm));
        t[m]++;
        assert(m <= k);
      }
    }
    count = 0;
    for (int i = 0; i <= k; i++)
    {
      count += t[i];
    }

    // Alpha has to be >= 1
    count = count > step_sz ? step_sz : count;
    res *= ((double)step_sz) / count;

    size_t i;
    for (i = 0; i < n; i = i + 4){
      x[i] *= factor;
      x[i+1] *= factor;
      x[i+2] *= factor;
      x[i+3] *= factor;
    }
    for (; i<n; i++){
      x[i] *= factor;
    }
  }

  res *= unitBallVol(n);
  return res;
}
