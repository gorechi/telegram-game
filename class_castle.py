from random import randint as dice

from class_basic import Loot, Money
from class_items import Key
from class_room import Room
from functions import pprint, randomitem
from settings import *


class Castle:
    def __init__(self, game, floors=5, rooms=5):
        self.game = game
        self.floors = floors
        self.rooms = rooms
        f = self.floors
        r = self.rooms
        self.all_rooms = [2] * r
        if f > 2: self.all_rooms += ([2] + [3] * (r - 2) + [2]) * (f - 2)
        if f > 1: self.all_rooms += [2] * r
        self.all_doors = []
        for _ in range(f * r):
            self.all_doors.append([0, 0, 0, 0])
        for i in range(f * r):
            floor = i // r
            room = i % r
            if f > 1 and r > 1:
                while self.all_doors[i].count(1) < self.all_rooms[i]:
                    q = dice(0, 3)
                    if self.all_doors[i][q] != 1:
                        if q == 0 and floor != 0:
                            self.all_doors[i][0] = 1
                            self.all_doors[i - r][2] = 1
                        elif q == 2 and floor < f - 1:
                            self.all_doors[i][2] = 1
                            self.all_doors[i + r][0] = 1
                        elif q == 3 and room != 0:
                            self.all_doors[i][3] = 1
                            self.all_doors[i - 1][1] = 1
                        elif q == 1 and room < r - 1:
                            self.all_doors[i][1] = 1
                            self.all_doors[i + 1][3] = 1
        self.plan = []
        for i in range(f * r):
            new_loot = Loot(self.game)
            a = Room(self.game, self.all_doors[i], '', new_loot)
            a.position = i
            self.plan.append(a)
        self.lights_off() #Выключаем свет в некоторых комнатах

    
    def stink(self, room, stink_level):
        """Функция распространения вони по замку.\n
        Распространяет вонь через открытые и закрытые двери, постепенно уменьшая уровень.\n
        Уровень вони записывается в параметр stink комнаты.

        Args:
            room (object Room): Комната, с которой начинается распределение вони
            stink_level (int): Начальный уровень вони

        """
        directions_dict = {0: (0 - self.rooms),
                           1: 1,
                           2: self.rooms,
                           3: (0 - 1)}
        available_directions = []
        if room.stink != 0:
            return True
        else:
            room.stink = stink_level
        for i in range(4):
            if room.doors[i] in [1, 2]:
                available_directions.append(i)
        if stink_level > 1:
            for direction in available_directions:
                next_room = self.plan[room.position + directions_dict[direction]]
                self.stink(next_room, stink_level - 1)
        return True

    def stink_map(self):
        for i in range(self.floors):
            floor = ''
            for j in range(self.rooms):
                floor = f'{floor + str(self.plan[i*self.rooms + j].stink)} '
            print(floor)

    def lights_off(self):
        self.how_many_dark_rooms = len(self.plan) // s_dark_rooms_ratio
        dark_rooms = randomitem(self.plan, False, self.how_many_dark_rooms)
        for room in dark_rooms:
            room.light = False

    def lock_doors(self):
        how_many_locked_rooms = len(self.plan) // s_locked_rooms_ratio
        for _ in range(how_many_locked_rooms):
            while True:
                a = randomitem(self.plan)
                if a != self.plan[0]:
                    new_money = Money(self.game, dice(s_min_money_in_locked_room, s_max_money_in_locked_room))
                    a.lock(2)
                    if a.center.empty:
                        a.loot.pile.append(new_money)
                    else:
                        a.center.loot.pile.append(new_money)
                    new_key = Key(self.game)
                    new_key.place(self)
                    break
        return True

    def map(self):
        f = self.floors
        r = self.rooms
        game = self.game
        doors_horizontal = {'0': '=', '1': ' ', '2': '-'}
        doors_vertical = {'0': '║', '1': ' ', '2': '|'}
        text = []
        text.append('======' * r + '=')
        for i in range(f):
            text.append('║' + '     ║' * r)
            line1 = '║'
            line2 = ''
            for j in range(r):
                room = self.plan[i*r+j]
                cant_rest, rest_place = room.can_rest()
                if game.player.current_position == i * r + j:    
                    a = game.player.name[0]
                elif rest_place and not room.visited == ' ':
                    a = '#'
                else: 
                    a = room.visited
                line1 += f'  {a}  {doors_vertical[str(self.all_doors[i * r + j][1])]}'
                line2 += f'==={doors_horizontal[str(self.all_doors[i * r + j][2])]}=='
            text.append(line1)
            text.append('║' + '     ║' * r)
            text.append(line2 + '=')
        pprint(game, text, r*s_map_width_coefficient, f*s_map_height_coefficient)

    def monsters(self): #Возвращает количество живых монстров, обитающих в замке в данный момент
        rooms_with_monsters = [a for a in self.plan if (a.monster() or a.monster_in_ambush())]
        return len(rooms_with_monsters)
