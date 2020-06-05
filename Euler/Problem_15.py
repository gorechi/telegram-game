# Starting in the top left corner of a 2×2 grid, and only being able to move to the right and down, there are exactly 6 routes to the bottom right corner.
#
# How many such routes are there through a 20×20 grid?

N = 20


def Factorial(i):
    result = 1
    for j in range(1, i + 1):
        result *= j
    print(result)
    return (result)


bigData = int(Factorial(2 * N) / (Factorial(N)) ** 2)

print(bigData)
