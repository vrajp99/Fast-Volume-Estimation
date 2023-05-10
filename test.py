import subprocess 
import math

tol = 0.1

def run_test(fname, ans):
    out = float(subprocess.run(["./polyvol", "tests/" + fname], capture_output = True).stdout.decode('utf-8')) 
    if not abs(out - ans) <= tol * max(out, ans):
        print('Error :', fname, ", expected :", ans, ", output :", out)

sizes = list(range(1, 11)) + [15, 20]

#Cubes
for n in sizes:
    ans = 2 ** n
    run_test("cube_" + str(n), ans)
                                                                                                        
print('Cubes done.')

#Cuboids
for n in sizes:
    ans = (2 ** n) * 50
    run_test("cuboid_" + str(n), ans)
                                                                                                        
print('Cuboids done.')

#Simplices
for n in sizes:
    ans = 1 / math.factorial(n)
    run_test("simplex_" + str(n), ans) 

print('Simplices done.')
