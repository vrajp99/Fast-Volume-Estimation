#include "polytope.h"
#include <iostream>

int main ()
{
	polytope p;
	p.readPolytope();
	// p.preprocess();
	cout << p.estimateVol() << '\n';
	return 0;
}
