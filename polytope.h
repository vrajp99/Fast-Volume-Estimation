#ifndef POLYTOPE_H
#define POLYTOPE_H 1

#include <armadillo>

// Note : mat and vec are typedefs of the corresponding
// data structures template-instantiated for doubles

using namespace std;
using namespace arma;

class polytope
{
	// The convex polytope in Ax <= b format
	size_t m, n;
	mat A;
	vec b;

	double beta_r;

public:

	polytope () {};

	void preprocess () const;
	const double estimateVol (int coeff = 1600) const;

	void readPolytope ();
};

#endif
