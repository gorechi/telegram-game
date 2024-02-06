integers = [12, 23, 1, 123, 34, 1, 2, 3, 4, 123, 34, 23, 432, 432]

def slice_count(s:list) -> int:
    count = 0
    for i in s:
        two_digits = {
            len(str(i)) == 2: 1,
            len(str(i)) != 2: 0
        }
        count += two_digits[True]
    results = {
        count == 1:1,
        count != 1:0
    }
    return results[True]

result = 0
for i in range(0, len(integers)-2):
    s = integers[i:i+3]
    print (s)
    result += slice_count(s)
print (result)

