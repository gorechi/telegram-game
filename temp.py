test = True

def q(test):
    return test

def check(test):
    if True in [q(test)]:
        return True
    return False

print (check(test))
print (check(test))
print (check(test))
test = False
print (check(test))
print (check(test))
print (check(test))
test = True
print (check(test))
print (check(test))
print (check(test))