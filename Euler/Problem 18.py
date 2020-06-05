# Задача нахождения самого большого по значению пути в пирамиде чисел

def readfile(filename, divide, divider=' '):
    filelines = []
    newfile = open(filename, encoding='utf-8')
    for line in newfile:
        if divide:
            filelines.append(line.rstrip('\n').split(divider))
        else:
            filelines.append(line.rstrip('\n'))
    newfile.close()
    for i in filelines:
        for j in range (len(i)):
            i[j] = int (i[j])
    return filelines
pyramid = readfile('Pyramid', True, ' ')
for line in range(1,len(pyramid)):
    for entryNumber in range (len(pyramid[line])):
        if entryNumber == 0:
            pyramid[line][entryNumber] += pyramid[line-1][entryNumber]
        elif entryNumber == len(pyramid[line])-1:
            pyramid[line][entryNumber] += pyramid[line-1][entryNumber-1]
        else:
            pyramid[line][entryNumber] += pyramid[line-1][entryNumber] if pyramid[line-1][entryNumber] >= pyramid[line-1][entryNumber-1] else pyramid[line-1][entryNumber-1]

result = sorted(pyramid[-1])[-1]
print (result)

