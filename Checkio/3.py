def checkio(array):
    a = 0
    if array != []:
        for i in range (0, len(array), 2):
            print ('i = ', i)
            a += array[i]
            print ('a = ', a)
        a *= array[-1]
    return a

print (checkio([1, 3, 5]))
