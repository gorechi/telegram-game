from functions import randomitem

d = [12, 345, 1231, 123, 3, 56]

item = randomitem([i for i in d if i > 100])

print ([i for i in d if i > 100])
print (item)
print (d.index(item))

