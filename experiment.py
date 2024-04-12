class A:
    
    _decoration = 'qq'
    
    def __init__(self):
        return None
    
    def decoration(self):
        print(f'A: {A._decoration}')
        print(f'A: {self.__class__._decoration}')

a = A()
a.decoration()

class B(A):
    
    _decoration = 'pp'
    
    def __init__(self):
        super().__init__()
        
    def decorations(self):
        print(f'B: {B._decoration}')
        print(f'B: {self.__class__._decoration}')
        print(f'A: {self.__class__.__base__._decoration}')

b = B()
b.decorations()
b.decoration()

print('bb', isinstance(b, A))
print(A.__subclasses__()[0].__class__)