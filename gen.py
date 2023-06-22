import numpy as np
np.random.seed(2)

def gen_poly(A, b, fname, is_m = False):
    m, n = A.shape
    assert m == b.shape[0]
    Ab = np.concatenate((A, b[:, np.newaxis]), axis=1)
    filename = "tests/{}_{}_{}".format(fname, n, m) if is_m else "tests/{}_{}".format(fname, n)
    with open(filename, 'w') as f:
        f.write("{} {}\n".format(m, n))
        for each in Ab:
            f.write(" ".join(str(x) for x in each) + '\n')

small_dims = list(range(1, 11)) + [13]
big_dims = [15] + list(range(20, 90, 10))
dims = small_dims + big_dims

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

#Crosses
for n in small_dims:
    m = 2 ** n
    f = lambda x, y : -1 if (int(2 ** x) & int(y)) == 0 else 1
    A = np.fromfunction(np.vectorize(f), (n, m))
    b = np.ones(m)
    gen_poly(A.T, b, "cross")

print('Crosses done.')

#Random Hyperplanes
for n in small_dims:
    for m in [2 * n, (5 * n) // 2, 3 * n]:
        A = 2 * np.random.rand(n, m) - 1
        A /= np.sqrt(np.sum(A ** 2, axis=0))
        b = np.ones(m)
        gen_poly(A.T, b, "rh", True)

print('Random Hyperplanes done.')
