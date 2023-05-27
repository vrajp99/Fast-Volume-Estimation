#include "polytope.h"
#include "XoshiroCpp.hpp"
#include <cassert>
#include <algorithm>

// Specifies how many data types (float or double) fit into one vector register
const size_t N_VEC = 4;

static inline
const double vec_hadd(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_add_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_add_pd(vlow, vhigh)); 
}
static inline
const double vec_hmax(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_max_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_max_pd(vlow, vhigh)); 
}
static inline
const double vec_hmin(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_min_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_min_pd(vlow, vhigh)); 
}

static const double norm_2(vec &x, size_t n)
{
  // Loop Unrolling for ILP

  double norm = 0;

  double *x_ptr = x.memptr(); 

  __m256d result = _mm256_set1_pd(0); 
  __m256d temp;
  for (size_t i = 0; i < (n / N_VEC) * N_VEC; i += N_VEC){
    __m256d x_vec = _mm256_loadu_pd(x_ptr + i);
    result = _mm256_fmadd_pd(x_vec, x_vec, result);
  }
  norm = vec_hadd(result);

  // Cleanup code
  for (size_t i = (n / N_VEC) * N_VEC; i < n; i++)
  {
    norm += x[i] * x[i];
  }
  return norm;
}

static const double unitBallVol(size_t n)
{
  // Added a DP-Like structure, avoid function calls.
  vector <double> vol(n + 1);

  vol[0] = 1;
  vol[1] = 2;
  double scale = (2 * M_PI);
  for (size_t i = 2; i < n + 1; i++)
  {
    vol[i] = (scale / i) * vol[i - 2];
  }
  return vol[n];
}

const double polytope::walk(vec &x, vec &Ax, const vector<vec> &B, const mat& A_negrecp, const vector < vector < __m256d > >& Agt,  const vector < vector < __m256d > >& Alt, const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng) const
{
  // Choose coordinate direction
  int dir = (rng() % n);

  double r, max, min, C = 0;

  C = norm_2(x, n);
  C -= x[dir] * x[dir];

  r = sqrt(rk - C);
  max = r - x[dir], min = -r - x[dir];

  vec A_dir = A.col(dir), A_negrecp_dir = A_negrecp.col(dir);
  vec bound(m);
  const double *B_ptr = B[dir].memptr(), *A_negrecp_dir_ptr = A_negrecp.colptr(dir), *A_dir_ptr = A.colptr(dir);
  double *bound_ptr = bound.memptr(), *Ax_ptr = Ax.memptr();

  for (size_t i = 0; i < (m / N_VEC) * N_VEC; i += N_VEC){
    __m256d A_negrecp_dir_vec = _mm256_loadu_pd(A_negrecp_dir_ptr + i);
    __m256d Ax_vec = _mm256_loadu_pd(Ax_ptr + i);
    __m256d bound_vec = _mm256_loadu_pd(bound_ptr + i);
    __m256d B_vec = _mm256_loadu_pd(B_ptr + i);
    __m256d result = _mm256_fmadd_pd(Ax_vec, A_negrecp_dir_vec, B_vec);
    _mm256_storeu_pd(bound_ptr + i, result);
  }
  for (size_t i = (m / N_VEC) * N_VEC ; i < m; i++)
  {
    bound[i] = B[dir][i] + (Ax[i] * A_negrecp_dir[i]);
  }

  
  __m256d max_all = _mm256_set1_pd(max), min_all = _mm256_set1_pd(min);
  __m256d maxd = max_all, mind = min_all;
  for (size_t i = 0; i < (m / N_VEC); i++)
  {
    __m256d bb = _mm256_loadu_pd(bound_ptr + i * N_VEC);
    
    __m256d bbgt = _mm256_blendv_pd(max_all, bb, Agt[dir][i]);
    maxd = _mm256_min_pd(maxd, bbgt);

    __m256d bblt = _mm256_blendv_pd(min_all, bb, Alt[dir][i]);
    mind = _mm256_max_pd(mind, bblt);
    
  }
  min = vec_hmax(mind), max = vec_hmin(maxd);
  for (size_t i = (m / N_VEC) * N_VEC; i < m; i++)
  {
    double aa = A_dir[i], bb = bound[i];
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
  for (size_t i = 0; i < (m / N_VEC) * N_VEC; i += N_VEC){
    __m256d Ax_vec = _mm256_loadu_pd(Ax_ptr + i);
    __m256d A_dir_vec = _mm256_loadu_pd(A_dir_ptr + i);
    __m256d result = _mm256_fmadd_pd(randval_vec, A_dir_vec, Ax_vec);
    _mm256_storeu_pd(Ax_ptr + i, result);
  }

  // Cleanup code
  for (size_t i = (m / N_VEC) * N_VEC; i < m; i++)
  {
    Ax[i] += A_dir[i] * randval;
  }
  
  return (C + t * t);
}

const double polytope::estimateVol() const
{
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
  vector <double> r2 (l+1);
  double pow_precomputed = pow ((double) 2.0, (double) 2.0 / n);
  // Replace Power with Just Multiplication at Each Loop
  r2[0] = 1;
  for (long i = 1; i <= l; ++i)
    r2[i] = pow_precomputed*r2[i - 1];

  // Precomputing the reciprocal of elements in A
  mat A_negrecp = -1.0 / A;

  // Precomputing vectorization mask
  vector < vector < __m256d > >  Agt(n), Alt(n);
  const __m256d zeros = _mm256_setzero_pd();
  for (size_t i = 0; i < n; i++)
  {
    Agt[i].resize(m / N_VEC);
    Alt[i].resize(m / N_VEC);
    const double *A_ptr = A.colptr(i); 

    for (size_t j = 0; j < m / N_VEC; j++)
    {
      __m256d aa = _mm256_loadu_pd(A_ptr + j * N_VEC);
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
      double x_norm = walk(x, Ax, B, A_negrecp, Agt, Alt, r2[k + 1], rng);
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


    double *x_ptr = x.memptr();
    size_t i; 

    __m256d factor_vec = _mm256_set1_pd(factor);
    __m256d x_vec, temp;

    for (i = 0; i < (n / N_VEC) * N_VEC; i += N_VEC){
      x_vec = _mm256_loadu_pd(x_ptr + i);
      temp = _mm256_mul_pd(x_vec, factor_vec);
      _mm256_storeu_pd(x_ptr + i, temp);
    }
    for (i = (n / N_VEC) * N_VEC; i < n; i++){
      x[i]*=factor;
    }
    Ax *= factor;
  }

  res *= unitBallVol(n);
  return res;
}
