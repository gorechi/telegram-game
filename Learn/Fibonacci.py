a = int(input())
F = [0, 1]
for i in range(a):
    F.append(F[-1]+F[-2])
print(F[a])
