from functions import roll

def prob(text, dex, monster_size, basis, weight):

    _range = 1000
    #basis = 9
    count = 0
    #weight = 6

    for _ in range(_range):
        result = [basis + roll([dex]) - monster_size]
        _roll = roll(result)
        _answer = _roll > weight
        if _answer:
            count += 1
    return f'{text}: {100*count/_range}%'

weights = [
    [5, 3],
    [6, 3],
    [7, 3],
    [8, 4],
    [8, 5]
]
for w in weights:
    basis = w[0]
    weight = w[1]
    print(f'basis: {basis}, weight: {weight}')
    print(prob('{Хилый герой, маленький монстр}', 1, 1, basis, weight))
    print(prob('{Средний герой, маленький монстр}', 5, 1, basis, weight))
    print(prob('{Ловкий герой, маленький монстр}', 10, 1, basis, weight))
    print(prob('{Очень ловкий герой, маленький монстр}', 15, 1, basis, weight))
    print(prob('{Хилый герой, средний монстр }', 1, 3, basis, weight))
    print(prob('{Средний герой, средний монстр}', 5, 3, basis, weight))
    print(prob('{Ловкий герой, средний монстр}', 10, 3, basis, weight))
    print(prob('{Очень ловкий герой, маленький монстр}', 15, 1, basis, weight))
    print(prob('{Хилый герой, большой монстр}', 1, 5, basis, weight))
    print(prob('{Средний герой, большой монстр}', 5, 5, basis, weight))
    print(prob('{Ловкий герой, большой монстр}', 10, 5, basis, weight))
    print(prob('{Очень ловкий герой, большой монстр}', 15, 1, basis, weight))
