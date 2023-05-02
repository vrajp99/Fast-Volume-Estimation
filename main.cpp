#include "polytope.h"
#include <iostream>

int main (int argc, char *argv[])
{
    if(argc != 2)
    {
        cout << "Usage : polyvol [FILE]\n";
        return 1;	
    }

    polytope p;
    p.readPolytope(argv[1]);
    // p.preprocess();
    cout << p.estimateVol() << '\n';
    return 0;
}
