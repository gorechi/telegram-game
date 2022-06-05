a = [1, 2, 3, 4, 5]

def func_chunks_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
        
new_list = list(func_chunks_generators(a, 2))

print(new_list)