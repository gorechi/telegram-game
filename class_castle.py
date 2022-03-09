from random import randint as dice

from class_basic import Loot, Money
from class_items import Book, Key, Map, Matches, Potion, Rune, Spell
from class_protection import Armor, Shield
from class_room import Furniture
from class_weapon import Weapon
from class_room import Room
from functions import pprint, randomitem
from settings import *


class Floor:
    def __init__(self, game, floors, rooms, how_many):
        self.game = game
        self.floors = floors
        self.rooms = rooms
        self.directions_dict = {0: (0 - self.rooms),
                               1: 1,
                               2: self.rooms,
                               3: (0 - 1),
                               'наверх': (0 - self.rooms),
                               'направо': 1,
                               'вправо': 1,
                               'налево': (0 - 1),
                               'лево': (0 - 1),
                               'влево': (0 - 1),
                               'вниз': self.rooms,
                               'низ': self.rooms,
                               'вверх': (0 - self.rooms),
                               'верх': (0 - self.rooms),
                               'право': 1}
        self.how_many = how_many
        self.monsters_in_rooms = {}
        f = self.floors
        r = self.rooms
        self.all_rooms = [2] * r
        if f > 2: self.all_rooms += ([2] + [3] * (r - 2) + [2]) * (f - 2)
        if f > 1: self.all_rooms += [2] * r
        self.all_doors = []
        for i in range(f * r):
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
            new_room = Room(self.game, self, self.all_doors[i], new_loot)
            new_room.position = i
            self.plan.append(new_room)
            self.monsters_in_rooms[new_room] = []
        self.lock_doors()
        self.lights_off()
        self.inhabit() 
    
    def inhabit(self):
        game = self.game
        # Создаем мебель и разбрасываем по замку
        self.all_furniture = game.readobjects(file='furniture.json',
                                        howmany=self.how_many['мебель'],
                                        random=True)
        for furniture in self.all_furniture:
            furniture.place(self)
        print (self.all_furniture)
        # Создаем очаги и разбрасываем по замку
        self.all_rest_places = game.readobjects(file='furniture-rest.json',
                                        howmany=self.how_many['очаг'],
                                        random=False)
        self.all_rest_places[0].place(self, room_to_place=self.plan[0])
        for rest_place in self.all_rest_places[1:]:
            rest_place.place(self)
        
        # Читаем монстров из файла и разбрасываем по замку
        self.all_monsters = game.readobjects(file='monsters.json',
                                       howmany=self.how_many['монстры'])
        for monster in self.all_monsters:
            monster.place(self)
            self.game.how_many_monsters += 1
        
        # Читаем оружие из файла и разбрасываем по замку
        self.all_weapon = game.readobjects(file='weapon.json',
                                     howmany=self.how_many['оружие'],
                                     object_class=Weapon)
        for weapon in self.all_weapon:
            weapon.place(self)
        
        # Читаем щиты из файла и разбрасываем по замку
        self.all_shields = game.readobjects(file='shields.json',
                                      howmany=self.how_many['щит'],
                                      object_class=Shield)
        for shield in self.all_shields:
            shield.place(self)
        
        # Читаем доспехи из файла и разбрасываем по замку
        self.all_armor = game.readobjects(file='armor.json',
                                    howmany=self.how_many['доспех'],
                                    object_class=Armor)
        for armor in self.all_armor:
            armor.place(self)
        
        # Читаем зелья из файла и разбрасываем по замку
        self.all_potions = game.readobjects(file='potions.json',
                                      howmany=self.how_many['зелье'],
                                      object_class=Potion)
        for potion in self.all_potions:
            potion.place(self)
        
        # Создаем руны и разбрасываем по замку
        self.all_runes = [Rune(self.game) for _ in range(self.how_many['руна'])]
        for rune in self.all_runes:
            rune.place(self)
            print(rune.poison)
        
        # Создаем книги и разбрасываем по замку
        self.all_books = game.readobjects(file='books.json',
                                    howmany=self.how_many['книга'],
                                    random=True,
                                    object_class=Book)
        for book in self.all_books:
            book.place(self)
        new_map = Map(game)
        new_map.place(self)  # Создаем и прячем карту
        matches = Matches(game)
        matches.place(self)  # Создаем и прячем спички

    
    def secret_rooms(self):
        return [i for i in self.plan if i.secret_word]
    
    def stink(self, room, stink_level):
        """Функция распространения вони по замку.\n
        Распространяет вонь через открытые и закрытые двери, постепенно уменьшая уровень.\n
        Уровень вони записывается в параметр stink комнаты.

        Args:
            room (object Room): Комната, с которой начинается распределение вони
            stink_level (int): Начальный уровень вони

        """
        directions = {0: (0 - self.rooms),
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
                next_room = self.plan[room.position + directions[direction]]
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
        for i in range(how_many_locked_rooms):
            while True:
                room = randomitem(self.plan)
                if room != self.plan[0]:
                    new_money = Money(self.game, dice(s_min_money_in_locked_room, s_max_money_in_locked_room))
                    room.lock(2)
                    monster = room.monsters('random')
                    if not monster:
                        room.loot.add(new_money)
                    else:
                        monster.give(new_money)
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
