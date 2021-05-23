from functions import dice

count = [0, 0]
for i in range(100000):
    d = dice(0, 1)
    count[d] += 1
print(count)