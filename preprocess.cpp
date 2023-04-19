#include "polytope.h"

// Ideas for optimization
// Normal array access has bound checks


// Must set ori_0 and return square of r_0
const double initEllipse (vec& ori)
{
	return 0;	
}

void polytope::preprocess ()
{
	// Ellipse parameters
	vec ori;
	double r_s = initEllipse(ori);
	mat T;
	T.eye(n, n);
	T = T * r_s;

	// Some constants required for the upcoming computation
	double beta_sqr = beta * beta;
	double cons1 = (1 - n * beta) / (n + 1);
	double cons2 = (2 * n * n + pow(1 - n * beta, 2)) * (1 - beta_sqr) / (2 * n * n - 2.0);
	double cons3 = 2 * cons1 / (1 - beta);

	// The main preprocessing algorithm
	for(size_t k = 0; ; ++k)
	{
		size_t i;
		bool found_i = false;

		// The value of T_k and a_i
		vec ta;

		// Find i such that a_i x <= b_i does not hold
		vec signed_dis = A * ori - b;
		uvec indices = find(signed_dis > 0, 1);

		if(!indices.is_empty())
		{
			found_i = true;
			i = indices(0);
			ta = T * A.row(i).t();
		}
		else
		{
			// Does the original code have a bug here?
			for(size_t j = 0; j < m; ++j)
			{
				ta = T * A.row(j).t();
				if(beta_sqr * as_scalar(A.row(j) * ta) + signed_dis(j) > 0)
				{
					found_i = true;
					i = j;
				}
			}
		}

		if(!found_i)
			break;
		
		// Updating parameters
		vec c = ta / sqrt(as_scalar(A.row(i) * ta));
		ori = ori - cons1 * c;
		T = cons2 * (T - cons3 * c * c.t());	
	}

	mat L = chol(T); // Check for runtime errors
	b = (b - A * ori) / beta;
	A = A * L.t();
	determinant = det(L) * pow(beta, n);
	
	// Initialize parameters for efficient walk if needed
}
