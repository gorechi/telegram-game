from functions import *

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
        if 0 < self.howmuchmoney <= 10:
            self.name = 'Несколько монет'
            self.name1 = 'Несколько монет'
        elif 10 < self.howmuchmoney <= 20:
            self.name = 'Кучка монет'
            self.name1 = 'Кучку монет'
        elif 20 < self.howmuchmoney <= 30:
            self.name = 'Груда монет'
            self.name1 = 'Груду монет'
        elif 30 < self.howmuchmoney:
            self.name = 'Много монет'
            self.name1 = 'Много монет'

    def __str__(self):
        return self.name + ' (' + self.howmuchmoney + ')'

    def take(self, luckyOne):
        luckyOne.money.howmuchmoney += self.howmuchmoney
        tprint(self.game, luckyOne.name + ' забрал ' + howmany(self.howmuchmoney, 'монету,монеты,монет'))

    def show(self):
        if self.howmuchmoney > 0:
            return howmany(self.howmuchmoney, 'монету,монеты,монет')
        else:
            return 'Денег нет'

    def __add__(self, other):
        self.howmuchmoney += other.howmuchmoney
