#Cubes
for n in range(1, 11):
    with open('tests/cube_' + str(n), 'w') as f:
        f.write("{} {}\n".format(2 * n, n))
        for i in range(n):
            f.write("1" + " 0" * i + " 1" + " 0" * (n - i - 1) + "\n")
            f.write("1" + " 0" * i + " -1" + " 0" * (n - i - 1) + "\n")

print('Cubes done.')

#Simplices
for n in range(1, 11):
    with open('tests/simplex_' + str(n), 'w') as f:
        f.write("{} {}\n".format(n + 1, n))
        for i in range(n):
            f.write("0" + " 0" * i + " -1" + " 0" * (n - i - 1) + "\n")
        f.write("1" + " 1" * n + "\n")

print('Simplices done.')
