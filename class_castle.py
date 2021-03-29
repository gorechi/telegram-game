from functions import *
from class_room import Room
from class_items import Key
from class_basic import Loot, Money


class Castle:
    def __init__(self, game, floors=5, rooms=5):
        self.game = game
        self.floors = floors
        self.rooms = rooms
        f = self.floors
        r = self.rooms
        self.allRooms = [2] * r
        if f > 2: self.allRooms += ([2] + [3] * (r - 2) + [2]) * (f - 2)
        if f > 1: self.allRooms += [2] * r
        self.allDoors = []
        for j in range(f * r):
            self.allDoors.append([0, 0, 0, 0])
        for i in range(f * r):
            floor = i // r
            room = i % r
            if f > 1 and r > 1:
                while self.allDoors[i].count(1) < self.allRooms[i]:
                    q = dice(0, 3)
                    if self.allDoors[i][q] != 1:
                        if q == 0 and floor != 0:
                            self.allDoors[i][0] = 1
                            self.allDoors[i - r][2] = 1
                        elif q == 2 and floor < f - 1:
                            self.allDoors[i][2] = 1
                            self.allDoors[i + r][0] = 1
                        elif q == 3 and room != 0:
                            self.allDoors[i][3] = 1
                            self.allDoors[i - 1][1] = 1
                        elif q == 1 and room < r - 1:
                            self.allDoors[i][1] = 1
                            self.allDoors[i + 1][3] = 1
        self.plan = []
        for i in range(f * r):
            newLoot = Loot(self.game)
            a = Room(self.game, self.allDoors[i], '', newLoot)
            a.position = i
            self.plan.append(a)
        self.lights_off() #Выключаем свет в некоторых комнатах

    def lights_off(self):
        self.how_many_dark_rooms = len(self.plan) // 8
        darkRooms = randomitem(self.plan, False, self.how_many_dark_rooms)
        for room in darkRooms:
            room.light = False

    def lockDoors(self):
        howManyLockedRooms = len(self.plan) // 8
        for i in range(howManyLockedRooms):
            while True:
                a = randomitem(self.plan)
                if a != self.plan[0]:
                    newMoney = Money(self.game, dice(25, 75))
                    a.lock(2)
                    if a.center == '':
                        a.loot.pile.append(newMoney)
                    else:
                        a.center.loot.pile.append(newMoney)
                    newKey = Key(self.game)
                    newKey.place(self)
                    break
        return True

    def map(self):
        f = self.floors
        r = self.rooms
        game = self.game
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '║', '1': ' ', '2': '|'}
        text = []
        text.append('======' * r + '=')
        for i in range(f):
            text.append('║' + '     ║' * r)
            line1 = '║'
            line2 = ''
            for j in range(r):
                a = game.player.name[0] if game.player.currentPosition == i * r + j else self.plan[i*r+j].visited
                line1 += '  {0}  {1}'.format(a, doorsVertical[str(self.allDoors[i * r + j][1])])
                line2 += '==={0}=='.format(doorsHorizontal[str(self.allDoors[i * r + j][2])])
            text.append(line1)
            text.append('║' + '     ║' * r)
            text.append(line2 + '=')
        pprint(game, text, r*72, f*90)

    def monsters(self): #Возвращает количество живых монстров, обитающих в замке в данный момент
        roomsWithMonsters = [a for a in self.plan if (a.monster() or a.monster_in_ambush())]
        return len(roomsWithMonsters)
