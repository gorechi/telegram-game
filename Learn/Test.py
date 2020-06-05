a = []
b = input()
while b != '':
    a.append(int(b))
    b = input()
print(a)
n = len(a)
for i in range(n-1):
    for j in range(n-1):
        if a[j]>a[j+1]:
            a[j], a[j+1] = a[j+1], a[j]
print(a)
