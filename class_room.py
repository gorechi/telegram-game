from functions import *
from class_monsters import Monster
from class_basic import Loot, Money
from class_items import Key

decor1 = readfile('decorate1', False)
decor2 = readfile('decorate2', False)
decor3 = readfile('decorate3', False)
decor4 = readfile('decorate4', False)


class Furniture:
    def __init__(self, game, name=''):
        self.game = game
        newloot = Loot(self.game)
        self.ambush = False
        self.loot = newloot
        self.locked = False
        self.lockable = False
        self.opened = True
        self.can_contain_weapon = True
        self.can_hide = False
        self.name = name
        self.empty = 'пусто'
        self.state = 'стоит'
        self.where = 'в углу'
        self.name1 = 'мебель'

    def on_create(self):
        self.name = randomitem(self.descriptions, False) + ' ' + self.name
        self.state = randomitem(self.states, False)
        self.where = randomitem(self.wheres, False)
        return True

    def put(self, item):
        self.loot.pile.append(item)

    def place(self, castle = None, room_to_place = None):
        if room_to_place:
            print(room_to_place.furniture_types(), self.type)
            if self.type not in room_to_place.furniture_types():
                room_to_place.furniture.append(self)
                return True
            else:
                return False
        else:
            can_place = False
            while not can_place:
                room = randomitem(castle.plan, False)
                if self.type not in room.furniture_types():
                    can_place = True
        room.furniture.append(self)
        if dice(1, 4) == 1 and self.lockable:
            self.locked = True
            veryNewKey = Key(self.game)
            veryNewKey.place(castle)
        if dice(1, 100) <= 50:
            newMoney = Money(self.game, dice(1, 50))
            self.loot.pile.append(newMoney)
        return True


class Room:
    def __init__(self, game, doors, center='', loot=''):
        self.game = game
        self.doors = doors
        a = dice(0, len(decor1) - 1)
        self.decoration1 = decor1[a]
        a = dice(0, len(decor2) - 1)
        self.decoration2 = decor2[a]
        a = dice(0, len(decor3) - 1)
        self.decoration3 = decor3[a]
        a = dice(0, len(decor4) - 1)
        self.decoration4 = decor4[a]
        self.center = center
        self.money = 0
        self.loot = loot
        self.locked = False
        self.position = -1
        self.visited = ' '
        self.ambush = ''
        self.runePlace = ''
        self.light = True
        self.furniture = []
        self.torchDice = dice(1, 5)
        if not self.light or self.torchDice != 4:
            self.torch = False
        else:
            self.torch = True

    def show(self, player):
        game = self.game
        if self.light:
            if self.torch:
                self.decoration1 = 'освещенную факелом ' + self.decoration1
            if self.center == '':
                whoIsHere = 'Не видно ничего интересного.'
            else:
                whoIsHere = self.decoration3 + ' ' + self.center.state + ' ' + self.center.name + '.'
            message = []
            message.append(player.name + ' попадает в {0} комнату {1}. {2}'.format(self.decoration1,
                                                                          self.decoration2,
                                                                          self.decoration4))
            for furniture in self.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            message.append(whoIsHere)
            tprint(game, message, state = 'direction')
        else:
            message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
            if isinstance(self.center, Monster):
                message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
            tprint(game, message, state = 'direction')

    def showThroughKeyHole(self, who):
        if self.center == '':
            return 'не может ничего толком разглядеть.'
        else:
            return self.center.keyHole

    def furniture_types(self):
        types = []
        for furniture in self.furniture:
            if furniture.type not in types:
                types.append(furniture.type)
        return types

    def monster(self):
        if self.center != '':
            if isinstance(self.center, Monster):
                return self.center
            else:
                return False
        else:
            return False

    def monster_in_ambush(self):
        if self.ambush != '':
            if isinstance(self.ambush, Monster):
                return self.ambush
            else:
                return False
        else:
            return False

    def map(self):
        game=self.game
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '║', '1': ' ', '2': '|'}
        string1 = '=={0}=='.format(doorsHorizontal[str(self.doors[0])])
        string2 = '║   ║'
        string3 = '{0} '.format(doorsVertical[str(self.doors[3])])
        if self.center != '':
            string3 += self.center.name[0]
        else:
            string3 += ' '
        string3 += ' {0}'.format(doorsVertical[str(self.doors[1])])
        string4 = '=={0}=='.format(doorsHorizontal[str(self.doors[2])])
        if self.light:
            pprint(game, string1 + '\n' + string2 + '\n' + string3 + '\n' + string2 + '\n' + string4, 100, 120)
            return True
        else:
            return False

    def lock(self, lockOrNot=2):
        game=self.game
        a = [-game.newCastle.rooms, 1, game.newCastle.rooms, -1]
        for i in range(4):
            if self.doors[i] == 1:
                self.doors[i] = lockOrNot
                j = i + 2 if (i + 2) < 4 else i - 2
                game.newCastle.plan[self.position + a[i]].doors[j] = lockOrNot
        self.locked = True
        return None
