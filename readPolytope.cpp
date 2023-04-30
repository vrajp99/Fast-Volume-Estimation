#include "polytope.h"
#include <fstream>

// Assume that the inputs in the file is stored
// in the format of A b

void polytope::readPolytope (const char * const filename)
{
	ifstream fin(filename);

	fin >> m >> n;

	A.set_size(m, n);
	b.set_size(m);

	// Accessed with bound checks. Remove bounds checking for faster performance
	for(size_t i = 0; i < m; ++i)
	{
		for(size_t j = 0; j < n; ++j)
			fin >> A(i, j);
		fin >> b(i);
	}
}
