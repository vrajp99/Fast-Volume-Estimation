import numpy as np

def gen_poly(A, b, fname):
    m, n = A.shape
    assert m == b.shape[0]
    Ab = np.concatenate((A, b[:, np.newaxis]), axis=1)
    with open("tests/{}_{}".format(fname, n), 'w') as f:
        f.write("{} {}\n".format(m, n))
        for each in Ab:
            f.write(" ".join(str(x) for x in each) + '\n')

dims = list(range(1, 11)) + [15, 20, 30, 40, 50, 60, 70, 80]

#Cubes
for n in dims:
    A = np.identity(n)
    A = np.concatenate((A, -A), axis=1)
    b = np.ones(2 * n)
    gen_poly(A.T, b, "cube")
    
    b[np.random.randint(2 * n)] = 99
    gen_poly(A.T, b, "cuboid")

print('Cubes and cuboids done.')

#Simplices
for n in dims:
    A = np.identity(n)
    A = np.concatenate((-A, np.ones(n)[:, np.newaxis]), axis=1)
    b = np.zeros(n + 1)
    b[-1] = 1
    gen_poly(A.T, b, "simplex")

print('Simplices done.')
