number = 600851475143
a = []
i = 2
while i <= number:
    if number % i == 0:
        a.append(i)
        number /= i
        i = 2
    else:
        i += 1
q = 0
for j in a:
    if j > q:
        q = j
print (q)
