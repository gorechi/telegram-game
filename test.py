test1 = 'один два три (четыре) пять (шесть)'
test2 = 'один два'
test3 = 'один'

def normal_count(str, exclude=None):
    str = str.replace(' ', ' и ')
    if exclude:
        print(exclude)
        str = str.replace(' и ' + exclude, ' ' + exclude)
        print(str)
    count = str.count(' и ')
    str = str.replace(' и ', ', ', count-1)
    return str

print(normal_count(test1, '('))
print(normal_count(test2))
print(normal_count(test3))