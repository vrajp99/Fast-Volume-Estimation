#include "polytope.h"
#include "glpk.h"

// Ideas for optimization
// Normal array access has bound checks


// Must set ori_0 and return square of r_0
const double polytope::initEllipsoid (vec& ori)
{
    double r_0s = 0;
    ori.zeros(n);
    // Initialize LP (with glp)
    glp_prob *lp;
    lp = glp_create_prob();
    glp_set_obj_dir(lp, GLP_MAX);
    glp_add_rows(lp, m);
    glp_add_cols(lp, n);

    // Constraints
    // GLP row setting need data from index 1 not 0
    int ind[n+1];
    double val[n+1];
    for(int i=1;i<m+1;i++){
        for(int j=1;j<n+1;j++){
            ind[j] = j;
            val[j] = A(i-1,j-1);
        }
        glp_set_mat_row(lp, i, n, ind, val);
        glp_set_row_bnds(lp, i, GLP_UP, 0, b(i-1));
    }

    // Freeing the column
    for(int j=1;j<n+1;j++){
        glp_set_col_bnds(lp, j, GLP_FR, 0, 0);
    }

    // Getting the bounds
    for(int i=1;i<n+1;i++){
        double ub, lb;

        // Objective +x_i
        for(int j=0;j<n+1;j++){
            if(j!=i){
                glp_set_obj_coef(lp, j, 0);
            } else {
                glp_set_obj_coef(lp, j, 1);
            }
        }

        glp_simplex(lp, NULL);
        ub = glp_get_obj_val(lp);

        // Origin Update
        for(int j=1;j<n+1;j++){
            ori(j-1) = ori(j-1) + (glp_get_col_prim(lp,j))/(2*n);
        }

        // Objective -x_i
        for(int j=0;j<n+1;j++){
            if(j!=i){
                glp_set_obj_coef(lp, j, 0);
            } else {
                glp_set_obj_coef(lp, j, -1);
            }
        }

        glp_simplex(lp, NULL);
        lb = -glp_get_obj_val(lp);

        // Origin Update
        for(int j=1;j<n+1;j++){
            ori(j-1) = ori(j-1) + (glp_get_col_prim(lp,j))/(2*n);
        }

        r_0s = pow(ub - lb, 2);
    }

    glp_delete_prob(lp);
    return r_0s;	
}

void polytope::preprocess ()
{
    // Assuming r = 2n
    // beta = 1 / 2n
    beta = 0.5 / n;

    // Ellipse parameters
    vec ori;
    double r_s = initEllipsoid(ori);
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
    // Gamma in the paper is determinant that is supposed to be returned
    
    // Initialize parameters for efficient walk if needed
}
