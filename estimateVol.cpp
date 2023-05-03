#include "polytope.h"
#include <cassert>

double norm_2(vec &x){
    double norm = 0;
    for (int i = 0; i < x.n_elem; i++){
        norm = norm + x(i)*x(i);
    }
    return norm; 
}

bool polytope::checkInBall(vec &x, int k){
    long l = ceill(n*log2(2*n));
    return (norm_2(x) <= pow(2,2.0*((double)k)/n));
}

double unitBallVol(int n){
    if(n >=2){
        return ((2 * M_PI) / n) * unitBallVol(n-2);
    } else if (n ==1){
        return 2;
    } else {
        return 1;
    }
}

const void polytope::walk(vec &x, int k){
    // Choose coordinate direction
    long l = ceill(n*log2(2*n));
    int dir = polytope::randi(n);

    double r, max, min, C = 0;

    C = norm_2(x);
	C -= x(dir) * x(dir);
    
	r = sqrt(pow(2,(2.0*(k+1))/n) - C);
	max = r - x(dir), min = -r - x(dir);
    vec B;
    mat Ai;
    rowvec exp(n);
	exp.ones();
    Ai = A / (A.col(dir) * exp);
    B = b / A.col(dir);
	vec bound = B - Ai * x;
	for (int i=0;i<m;i++){
		if (A(i,dir) > 0 && bound(i) < max)
	        max = bound(i);
		else if (A(i,dir) < 0 && bound(i) > min)
		    min = bound(i); 
	}
    double randval =(((double)rand()*(max - min))/RAND_MAX) + min;
	double t = x(dir) + randval;
	x(dir) = t;
    assert(min <= randval && randval<=max);
}



double polytope::estimateVol ()
{
    double gamma = determinant;
    long l = ceill(n*log2(2*n));
    long ll = (int)(n * log((double)2*n) / log((double)2)) + 2;
    cout<<"l:"<<l<<", ll: "<<ll<<", n:"<<n<<endl;
    long step_sz = 1600 * l;
    cout << "step size : " << step_sz << endl;
    long count=0;
    vec x;
    x.zeros(n);
    vector<long> t(l+1,0);
    vector<double> alpha(l,0);
    for(int k=l-1; k>=0; k--){
        // cout<<"x: ";
        // for(int i=0;i<n;i++){
        //     cout<<x(i)<<" ";
        // }
        // cout << endl;
        for(long i=count;i<step_sz;i++){
            walk(x,k);
            if (checkInBall(x,0)){
                t[0]++;
            } else if (checkInBall(x,k)){
                long m = ceill(((double)n)/2 * log2(norm_2(x)));
                t[m]++;
                assert(m<=k);
            } 
        }
        count = 0;
        for(int i=0;i<=k;i++){
            count += t[i];
        }

        // Alpha has to be >= 1
        if(count > step_sz){
            count=step_sz;
            cout<<"WTF"<<endl;
        }
        alpha[k] = ((double)step_sz)/count;
        cout<<pow(2,2.0*((double)k)/n)<<"\t"<<alpha[k]<<"\t"<<count<<"\n";
        double factor = pow(2.0,-1.0/n);
        for(int i=0;i<n;i++){
            x(i) = x(i)*factor;
        }
    }
    double res = gamma;
    for(int i=0;i<l;i++){
        res*=alpha[i];
    }
    res*=unitBallVol(n);
    cout<<unitBallVol(n)<<"\n";
    cout<<determinant<<endl;
    return res;
}
