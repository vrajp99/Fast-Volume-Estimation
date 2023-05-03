import subprocess 
import math

tol = 0.1

#Cubes
for n in range(1, 11):
    out = float(subprocess.run(["./polyvol", "tests/cube_" + str(n)], capture_output = True).stdout.decode('utf-8')) 
    exp = 2 ** n 
    if not abs(out - exp) <= tol * max(out, exp):
        print('Error : cube_' + str(n), ", expected :", exp, ", output :", out)
                                                                                                        
print('Cubes done.')

#Simplices
for n in range(1, 11) :
    out = float(subprocess.run(["./polyvol", "tests/simplex_" + str(n)], capture_output = True).stdout.decode('utf-8')) 
    exp = 1 / math.factorial(n) 
    if not abs(out - exp) <= tol * max(out, exp):
        print('Error : simplex_' + str(n), ", expected :", exp, ", output :", out)

print('Simplices done.')
