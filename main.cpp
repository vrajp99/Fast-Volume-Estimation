#include "polytope.h"
#include <iostream>

int main(int argc, char *argv[]) {
  if (argc != 2) {
    cout << "Usage : polyvol [FILE]\n";
    return 1;
  }

  srand(time(NULL));

  polytope p;
  p.readPolytope(argv[1]);
  cout << p.estimateVol() << '\n';
  return 0;
}
