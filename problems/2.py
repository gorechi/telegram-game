def resheto(a, b):
    d = [i for i in range(2, b)]
    for i in range(b-2):
        if d[i] != 0:
            for j in range(i+d[i], b-2, d[i]):
                d[j] = 0
    g=[]
    for q in range (a-1,len(d)):
        if d[q] != 0:
            g.append(d[q])
    return g
t = int(input())
a = []
for i in range (t):
    b = input()
    a.append(b.split(' '))
for i in range (t):
    n = int(a[i][0])
    m = int(a[i][1])
    q = resheto(n, m)
    for j in q:
        print (j)
    print ()
