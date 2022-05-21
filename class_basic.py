from functions import howmany, tprint
from settings import s_money_groups


class Loot:
    def __init__(self, game):
        self.game = game
        self.pile = []
        self.empty = False

    def __str__(self):
        return 'loot'

    def add(self, obj):
        self.pile.append(obj)

    def remove(self, obj):
        self.pile.remove(obj)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return len(self.loot.pile) == other 


class Money:
    def __init__(self, game, how_much_money):
        self.game = game
        self.how_much_money = how_much_money
        self.empty = False
        if 0 < self.how_much_money <= s_money_groups[0]:
            self.name = 'Несколько монет'
            self.name1 = 'Несколько монет'
        elif s_money_groups[0] < self.how_much_money <= s_money_groups[1]:
            self.name = 'Кучка монет'
            self.name1 = 'Кучку монет'
        elif s_money_groups[1] < self.how_much_money <= s_money_groups[2]:
            self.name = 'Груда монет'
            self.name1 = 'Груду монет'
        elif s_money_groups[2] < self.how_much_money:
            self.name = 'Много монет'
            self.name1 = 'Много монет'

    def __repr__(self):
        return str(self.how_much_money)
    
    def __int__(self) -> int:
        return self.how_much_money
    
    def __eq__(self, other:int) -> bool:
        return self.how_much_money == other
    
    def __ge__(self, other:int) -> bool:
        return self.how_much_money >= other
    
    def __add__(self, other):
        if isinstance(other, int):
            self.how_much_money += other
        elif isinstance(other, Money):
            self.how_much_money += other.how_much_money
        else:
            raise TypeError('To Money you can only add integer or another Money.')
        return self
    
    def __sub__(self, other):
        if isinstance(other, int):
            self.how_much_money -= other
        elif isinstance(other, Money):
            self.how_much_money -= other.how_much_money
        else:
            raise TypeError('From Money you can only substract integer or another Money.')
        return self

    def take(self, lucky_one):
        lucky_one.money.how_much_money += self.how_much_money
        tprint(self.game, f'{lucky_one.name} {lucky_one.g(["забрал", "забрала"])} {howmany(self.how_much_money, "монету,монеты,монет")}')

    def show(self):
        if self >= 1:
            return howmany(self.how_much_money, 'монету,монеты,монет')
        else:
            return 'Денег нет'