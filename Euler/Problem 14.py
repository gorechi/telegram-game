# The following iterative sequence is defined for the set of positive integers:
#
# n → n/2 (n is even)
# n → 3n + 1 (n is odd)
#
# Using the rule above and starting with 13, we generate the following sequence:
#
# 13 → 40 → 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1
# It can be seen that this sequence (starting at 13 and finishing at 1) contains 10 terms. Although it has not been proved yet (Collatz Problem), it is thought that all starting numbers finish at 1.
#
# Which starting number, under one million, produces the longest chain?
#
# NOTE: Once the chain starts the terms are allowed to go above one million.
#
allNumbers = {}
k = 1000000
for i in range(2, k):
    if not i in allNumbers:
        result = i
        shortList = {}
        while result != 1:
            shortList[int(result)] = 1
            for j in shortList:
                shortList[j] += 1
            if result % 2 == 0:
                result /= 2
            else:
                result = 3 * result + 1
            if result in allNumbers:
                for j in shortList:
                    shortList[j] += allNumbers[result] - 1
                break
        allNumbers.update(shortList)
element = 0
max = 0
for j in range(2, k):
    if allNumbers[j] > max:
        max = allNumbers[j]
        element = j
print(element, max)
