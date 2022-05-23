from functions import randomitem

d = [121, 345, 1231, 123, 3, 56]

item = randomitem([a for a in d[1::] if a > 100])

print ([a for a in d[1::] if a > 100])
print (item)

