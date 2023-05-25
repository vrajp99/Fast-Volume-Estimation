#ifndef POLYTOPE_H
#include "polytope.h"
#endif
#include "XoshiroCpp.hpp"
#include <cassert>
#include <algorithm>

inline
double vec_hadd(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_add_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_add_pd(vlow, vhigh)); 
}
inline
double vec_hmax(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_max_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_max_pd(vlow, vhigh)); 
}
inline
double vec_hmin(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_min_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_min_pd(vlow, vhigh)); 
}

double norm_2(vec &x, int n)
{
  // Loop Unrolling for ILP

  double norm = 0;
  int i;

  double *x_ptr = (double *)(&x(0));

  __m256d result = _mm256_set1_pd(0); 
  __m256d temp;
  for (i = 0; i < n / 4; i++){
    __m256d x_vec = _mm256_loadu_pd(x_ptr + 4*i);
    result = _mm256_fmadd_pd(x_vec, x_vec, result);
  }
  norm = vec_hadd(result);

  // Cleanup code
  for (i = (n / 4) * 4; i < n; i++)
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

double polytope::walk(vec &x, vec &Ax, const vector<vec> &B, const vector < vector < __m256d > >& Agt,  const vector < vector < __m256d > >& Alt,
                            const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng)
{
  // Choose coordinate direction
  int dir = (rng() % n);

  double r, max, min, C = 0;

  C = norm_2(x, n);
  C -= x[dir] * x[dir];

  r = sqrt(rk - C);
  max = r - x[dir], min = -r - x[dir];

  vec bound(m); // = B[dir] - (Ax/A.col(dir));
  double *B_ptr = (double *)(&B[dir][0]), *bound_ptr = (double *)(&bound[0]), *Ax_ptr = (double *)(&Ax[0]), *Adir_ptr = (double *)(&A.col(dir)[0]);

  for (size_t i = 0; i < m / 4; i++){
    __m256d Adir_vec = _mm256_loadu_pd(Adir_ptr + 4*i);
    __m256d Ax_vec = _mm256_loadu_pd(Ax_ptr + 4*i);
    __m256d bound_vec = _mm256_loadu_pd(bound_ptr + 4*i);
    __m256d B_vec = _mm256_loadu_pd(B_ptr + 4*i);
    __m256d result = _mm256_div_pd(Ax_vec, Adir_vec);
    result = _mm256_sub_pd(B_vec, result);
    _mm256_storeu_pd(bound_ptr + 4 * i, result);
  }
  for (size_t i = (m / 4) * 4 ; i < m; i++)
  {
    bound[i] = B[dir][i] - (Ax[i] / A.col(dir)[i]);
  }

  
  __m256d max_all = _mm256_set1_pd(max), min_all = _mm256_set1_pd(min);
  __m256d maxd = max_all, mind = min_all;
  for (size_t i = 0; i < m / 4; i++)
  {
    __m256d bb = _mm256_loadu_pd(bound_ptr + 4 * i);
    
    __m256d bbgt = _mm256_blendv_pd(max_all, bb, Agt[dir][i]);
    maxd = _mm256_min_pd(maxd, bbgt);

    __m256d bblt = _mm256_blendv_pd(min_all, bb, Alt[dir][i]);
    mind = _mm256_max_pd(mind, bblt);
    
  }
  min = vec_hmax(mind), max = vec_hmin(maxd);
  for (size_t i = (m / 4) * 4; i < m; i++)
  {
    double aa = A.col(dir)[i], bb = bound[i];
    if (aa > 0 && bb < max)
      max = bb;
    else if (aa < 0 && bb > min)
      min = bb;
  }

  double randval = (XoshiroCpp::FloatFromBits(rng()))*(max - min) + min;
  double t = x[dir] + randval;
  x[dir] = t;
  assert((min - 0.00001) <= randval && randval <= (max + 0.00001));
  
  // Ax += (A.col(dir) * randval);

  __m256d randval_vec = _mm256_set1_pd(randval); 
  for (size_t i = 0; i < m / 4; i++){
    __m256d Ax_vec = _mm256_loadu_pd(Ax_ptr + 4*i);
    __m256d Adir_vec = _mm256_loadu_pd(Adir_ptr + 4*i);
    __m256d result = _mm256_fmadd_pd(randval_vec, Adir_vec, Ax_vec);
    _mm256_storeu_pd(Ax_ptr + 4 * i, result);
  }

  // Cleanup code
  for (size_t i = (m / 4) * 4 ; i < m; i++)
  {
    Ax[i] += A.col(dir)[i] * randval;
  }
  
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
  vec Ax(m);
  Ax.zeros();
  for (size_t i = 0; i < n; ++i)
  {
    B[i] = b / A.col(i);
  }

  // Precomputing radii
  double r2 [l+1];
  double pow_precomputed = pow ((double) 2.0, (double) 2.0 / n);
  // Replace Power with Just Multiplication at Each Loop
  r2[0] = 1;
  for (long i = 1; i <= l; ++i)
    r2[i] = pow_precomputed*r2[i - 1];

  // Precomputing vectorization mask
  vector < vector < __m256d > >  Agt(n), Alt(n);
  const __m256d zeros = _mm256_setzero_pd();
  for (size_t i = 0; i < n; i++)
  {
    Agt[i].resize(m/4);
    Alt[i].resize(m/4);
    double *A_ptr = (double *)&(A.col(i))[0]; 

    for (size_t j = 0; j < m / 4; j++)
    {
      __m256d aa = _mm256_loadu_pd(A_ptr + 4 * j);
      Agt[i][j] = _mm256_cmp_pd(aa, zeros, _CMP_GT_OQ);
      Alt[i][j] = _mm256_cmp_pd(aa, zeros, _CMP_LT_OQ);
    }
  }

  // Random Generator
  XoshiroCpp::Xoshiro128PlusPlus rng(time(0));

  for (int k = l - 1; k >= 0; k--)
  {
    for (long i = count; i < step_sz; i++)
    {
      double x_norm = walk(x, Ax, B, Agt, Alt, r2[k + 1], rng);
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


    double *x_ptr = (double *)(&x(0));
    size_t i; 

    __m256d factor_vec = _mm256_set1_pd(factor);
    __m256d x_vec, temp;

    for (i = 0; i < n / 4; i++){
      x_vec = _mm256_loadu_pd(x_ptr + 4 * i);
      temp = _mm256_mul_pd(x_vec, factor_vec);
      _mm256_storeu_pd(x_ptr + 4 * i, temp);
    }
    for (i = (n / 4) * 4; i < n; i++){
      x[i]*=factor;
    }
    Ax *= factor;
  }

  res *= unitBallVol(n);
  return res;
}
