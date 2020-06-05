# If the numbers 1 to 5 are written out in words: one, two, three, four, five, then there are 3 + 3 + 5 + 4 + 4 = 19 letters used in total.
#
# If all the numbers from 1 to 1000 (one thousand) inclusive were written out in words, how many letters would be used?
#
#
# NOTE: Do not count spaces or hyphens. For example, 342 (three hundred and forty-two) contains 23 letters and 115 (one hundred and fifteen) contains 20 letters. The use of "and" when writing out numbers is in compliance with British usage.

result = 0
lastNumber = 1000
numbersDict = {
0: '',
1: 'one',
2: 'two',
3: 'three',
4: 'four',
5: 'five',
6: 'six',
7: 'seven',
8: 'eight',
9: 'nine',
10: 'ten',
11: 'eleven',
12: 'twelve',
13: 'thirteen',
14: 'fourteen',
15: 'fifteen',
16: 'sixteen',
17: 'seventeen',
18: 'eighteen',
19: 'nineteen',
20: 'twenty',
30: 'thirty',
40: 'forty',
50: 'fifty',
60: 'sixty',
70: 'seventy',
80: 'eighty',
90: 'ninety',
100: 'onehundred',
1000: 'onethousand'}

for i in range (1, lastNumber+1):
    if i in numbersDict:
        string = numbersDict[i]
    elif len (str(i)) == 2:
        numberString = str(i)
        string = numbersDict[int(numberString[0])*10] + numbersDict[int(numberString[1])]
    elif len (str(i)) == 3:
        numberString = str(i)
        if numberString[1:] != '00':
            string = numbersDict[int(numberString[0])] + 'hundredand'
        else:
            string = numbersDict[int(numberString[0])] + 'hundred'
        if int(numberString[1:]) in numbersDict:
            string += numbersDict[int(numberString[1:])]
        else:
            string += numbersDict[int(numberString[1])*10] + numbersDict[int(numberString[2])]
    print (i, string, len(string))
    result += len (string)
print (result)
