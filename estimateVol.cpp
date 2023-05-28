#include "polytope.h"
#include "XoshiroCpp.hpp"
#include <cassert>
#include <algorithm>

// Specifies how many data types (float or double) fit into one vector register
const size_t N_VEC = 4;
double* bound;

static inline
// Takes a vector, and computes the sum of the individual elements of the vector.
const double vec_hadd(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_add_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_add_pd(vlow, vhigh)); 
}
// Takes a vector, and computes the maximum of the individual elements of the vector.
static inline
const double vec_hmax(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_max_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_max_pd(vlow, vhigh)); 
}
// Takes a vector, and computes the minimum of the individual elements of the vector.
static inline
const double vec_hmin(const __m256d& v) {
    __m128d vlow  = _mm256_castpd256_pd128(v);
    __m128d vhigh = _mm256_extractf128_pd(v, 1); 
    vlow  = _mm_min_pd(vlow, vhigh); 

    vhigh = _mm_unpackhi_pd(vlow, vlow);
    return  _mm_cvtsd_f64(_mm_min_pd(vlow, vhigh)); 
}

static const double norm_2(double* x, size_t n)
{
  // Loop Unrolling for ILP

  double norm = 0;

  double *x_ptr = x; 

  __m256d result = _mm256_set1_pd(0); 
  for (size_t i = 0; i < (n / N_VEC) * N_VEC; i += N_VEC){
    __m256d x_vec = _mm256_load_pd(x_ptr + i);
    result = _mm256_fmadd_pd(x_vec, x_vec, result);
  }
  norm = vec_hadd(result);

  // Cleanup code
  for (size_t i = (n / N_VEC) * N_VEC; i < n; i++) {
    norm += x[i] * x[i];
  }
  return norm;
}

static const double unitBallVol(size_t n)
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

const double polytope::walk(double* x, double *Ax, const double* B, const mat& A_negrecp, const __m256d* Agt,  const __m256d* Alt, const double rk, XoshiroCpp::Xoshiro128PlusPlus &rng) const
{
  // Choose coordinate direction
  int dir = (rng() % n);

  double r, max, min, C = 0;

  C = norm_2(x, n);
  C -= x[dir] * x[dir];

  r = sqrt(rk - C);
  max = r - x[dir], min = -r - x[dir];

  vec A_dir = A.col(dir), A_negrecp_dir = A_negrecp.col(dir);
  const double *B_ptr = B + m * dir, *A_negrecp_dir_ptr = A_negrecp.colptr(dir), *A_dir_ptr = A.colptr(dir);
  double *bound_ptr = bound, *Ax_ptr = Ax;

  for (size_t i = 0; i < (m / N_VEC) * N_VEC; i += N_VEC){
    __m256d A_negrecp_dir_vec = _mm256_loadu_pd(A_negrecp_dir_ptr + i);
    __m256d Ax_vec = _mm256_load_pd(Ax_ptr + i);
    __m256d B_vec = _mm256_loadu_pd(B_ptr + i);
    __m256d result = _mm256_fmadd_pd(Ax_vec, A_negrecp_dir_vec, B_vec);
    _mm256_store_pd(bound_ptr + i, result);
  }
  for (size_t i = (m / N_VEC) * N_VEC ; i < m; i++)
  {
    bound[i] = B[m * dir + i] + (Ax[i] * A_negrecp_dir[i]);
  }

  
  __m256d max_all = _mm256_set1_pd(max), min_all = _mm256_set1_pd(min);
  __m256d maxd = max_all, mind = min_all;
  for (size_t i = 0; i < (m / N_VEC); i++)
  {
    __m256d bb = _mm256_load_pd(bound_ptr + i * N_VEC);
    
    __m256d bbgt = _mm256_blendv_pd(max_all, bb, Agt[(m/N_VEC)*dir + i]);
    maxd = _mm256_min_pd(maxd, bbgt);

    __m256d bblt = _mm256_blendv_pd(min_all, bb, Alt[(m/N_VEC)*dir + i]);
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
  
  __m256d randval_vec = _mm256_set1_pd(randval); 
  for (size_t i = 0; i < (m / N_VEC) * N_VEC; i += N_VEC){
    __m256d Ax_vec = _mm256_load_pd(Ax_ptr + i);
    __m256d A_dir_vec = _mm256_loadu_pd(A_dir_ptr + i);
    __m256d result = _mm256_fmadd_pd(randval_vec, A_dir_vec, Ax_vec);
    _mm256_store_pd(Ax_ptr + i, result);
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
  double* x = (double *) aligned_alloc(32, ((n*sizeof(double))/32 + 1)*32);
  memset((void *)x,0,((n*sizeof(double))/32 + 1)*32);
  // long t[l + 1];
  double* t = (double *) aligned_alloc(32, (((l+1)*sizeof(double))/32 + 1)*32);
  memset((void *)t,0,(((l+1)*sizeof(double))/32 + 1)*32);
  bound = (double *) aligned_alloc(32, (((m)*sizeof(double))/32 + 1)*32);
  // Move factor computation outside.
  double factor = pow(2.0, -1.0 / n);

  // Initialization of Ax and B
  double* B = (double *) aligned_alloc(32, n*m*sizeof(double));
  double* Ax = (double *) aligned_alloc(32, ((m*sizeof(double))/32 + 1)*32);
  memset((void *)Ax,0,((m*sizeof(double))/32 + 1)*32);

  // Ax.zeros();


  // Precomputing the reciprocal of elements in A
  mat A_negrecp = -1.0 / A;

  size_t cl;
  size_t rw;

  const double *b_ptr = b.memptr();
  __m256d sign_flip = _mm256_set1_pd(-1);
 
  for (cl = 0; cl < n; cl++){
    double *B_ptr = B + m * cl;
    double *A_rcp_ptr = A_negrecp.colptr(cl);
    __m256d A_rcp_val, b_val, B_to_store;
    
    for (rw = 0; rw < (m / N_VEC) * N_VEC; rw += N_VEC){
      b_val = _mm256_loadu_pd(b_ptr + rw);
      // Arma -- Change b to aligned.
      b_val = _mm256_mul_pd(b_val, sign_flip);
      A_rcp_val = _mm256_loadu_pd(A_rcp_ptr + rw);
      // Arma - A reciprocal - change...
      B_to_store = _mm256_mul_pd(b_val, A_rcp_val);
      _mm256_storeu_pd(B_ptr + rw, B_to_store);
    }
    for (rw = (m / N_VEC) * N_VEC; rw < m; rw++){
      B[m *cl + rw] = -b[rw]*A_negrecp.col(cl)[rw];
    }
  }


  // Precomputing radii
  double* r2  = (double *) aligned_alloc(32, (((l+1)*sizeof(double))/32 + 1)*32);
  double pow_precomputed = pow ((double) 2.0, (double) 2.0 / n);
  // Replace Power with Just Multiplication at Each Loop
  r2[0] = 1;
  for (long i = 1; i <= l; ++i)
    r2[i] = pow_precomputed*r2[i - 1];


  // Precomputing vectorization mask
  __m256d* Agt = (__m256d*) aligned_alloc(sizeof(__m256d),(m / N_VEC)*n*sizeof(__m256d));
  __m256d* Alt = (__m256d*) aligned_alloc(sizeof(__m256d),(m / N_VEC)*n*sizeof(__m256d));
  const __m256d zeros = _mm256_setzero_pd();
  for (size_t i = 0, ii = 0; i < n; i++, ii+=(m / N_VEC))
  {
    const double *A_ptr = A.colptr(i);
    // Column Pointer -- Need aligned allocate for A? 
    for (size_t j = 0, jj = 0; j < m / N_VEC; j++, jj+=N_VEC)
    {
      __m256d aa = _mm256_loadu_pd(A_ptr + jj);
      // Change to Aligned Load I guess.
      Agt[ii + j] = _mm256_cmp_pd(aa, zeros, _CMP_GT_OQ);
      Alt[ii + j] = _mm256_cmp_pd(aa, zeros, _CMP_LT_OQ);
    }
  }

  // Random Generator
  XoshiroCpp::Xoshiro128PlusPlus rng(time(0));

  for (int k = l - 1; k >= 0; k--)
  {
    for (long i = count; i < step_sz; i++)
    {
      double x_norm = walk(x, Ax, B, A_negrecp, Agt, Alt, r2[k + 1], rng);
      if (x_norm <= r2[0]) {
        t[0]++;
      } else if (x_norm <= r2[k]) {
        // Change divide by 2 to multiply by 0.5
        long m = ceill(((double)n) * 0.5 * log2(x_norm));
        t[m]++;
        assert(m <= k);
      }
    }
    count = 0;
    __m256d count_vec = _mm256_setzero_pd();
    __m256d t_vec;
    size_t i;
    for (i = 0; i < (k / N_VEC)*N_VEC; i+=N_VEC) {
      t_vec = _mm256_load_pd(t + i);
      count_vec = _mm256_add_pd(count_vec, t_vec);
    }
    count = vec_hadd(count_vec);
    // Clean Up Loop
    for(; i <= (size_t)k; i++){
      count+=t[i];
    }
    // Alpha has to be >= 1
    count = count > step_sz ? step_sz : count;
    res *= ((double)step_sz) / count;


    double *x_ptr = x;

    __m256d factor_vec = _mm256_set1_pd(factor);
    __m256d x_vec, temp;

    for (i = 0; i < (n / N_VEC) * N_VEC; i += N_VEC){
      // Modify to have aligned loads
      x_vec = _mm256_load_pd(x_ptr + i);
      temp = _mm256_mul_pd(x_vec, factor_vec);
      _mm256_store_pd(x_ptr + i, temp);
    }
    for (; i < n; i++){
      x[i] *= factor;
    }
    __m256d Ax_vec, Ax_fact;
    for (i = 0; i < (m / N_VEC) * N_VEC; i += N_VEC) {
      Ax_vec = _mm256_load_pd(Ax + i);
      Ax_fact = _mm256_mul_pd(Ax_vec, factor_vec);
      _mm256_store_pd(Ax + i, Ax_fact);
    }
    for (; i < m; i++){
      Ax[i] *= factor;
    }
  }

  res *= unitBallVol(n);
  return res;
}
