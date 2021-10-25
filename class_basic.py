from functions import *
from settings import *

class Loot:
    def __init__(self, game):
        self.game = game
        self.pile = []

    def __str__(self):
        return 'loot'

    def add(self, obj):
        self.pile.append(obj)

    def remove(self, obj):
        self.pile.remove(obj)


class Money:
    def __init__(self, game, howmuchmoney):
        self.game = game
        self.howmuchmoney = howmuchmoney
        if 0 < self.howmuchmoney <= money_groups[0]:
            self.name = 'Несколько монет'
            self.name1 = 'Несколько монет'
        elif money_groups[0] < self.howmuchmoney <= money_groups[1]:
            self.name = 'Кучка монет'
            self.name1 = 'Кучку монет'
        elif money_groups[1] < self.howmuchmoney <= money_groups[2]:
            self.name = 'Груда монет'
            self.name1 = 'Груду монет'
        elif money_groups[2] < self.howmuchmoney:
            self.name = 'Много монет'
            self.name1 = 'Много монет'

    def __str__(self):
        return self.name + ' (' + self.howmuchmoney + ')'

    def take(self, luckyOne):
        luckyOne.money.howmuchmoney += self.howmuchmoney
        tprint(self.game, f'{luckyOne.name} забрал {howmany(self.howmuchmoney, "монету,монеты,монет")}')

    def show(self):
        if self.howmuchmoney > 0:
            return howmany(self.howmuchmoney, 'монету,монеты,монет')
        else:
            return 'Денег нет'

    def __add__(self, other):
        self.howmuchmoney += other.howmuchmoney
