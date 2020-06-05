s = 2
F = [1, 2]
while (F[-1]+F[-2]) < 4000000:
    F.append(F[-1]+F[-2])
    if F[-1]%2 == 0:
        s += F[-1]
print(s)
