from random import randint as dice

from class_basic import Money, Loot
from class_items import Key, Map, Matches, Rune
from class_room import Door, Room
from functions import pprint, randomitem
from class_monsters import Corpse
from settings import *


class Floor:
    def __init__(self, game, rows:int, rooms:int, how_many:list):
        self.game = game
        self.rows = rows
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
        self.create_rooms(self.rows, self.rooms)
        self.lock_doors()
        self.lights_off()
        self.inhabit()
                
    
    def create_rooms(self, f:int, r:int):    
        
        """
        Функция генерирует комнаты этажа замка.
        - f - это количество рядов в плане этажа
        - r - это количество комнат в одном ряду
        
        """
        
        all_doors = self.create_doors(f, r)
        self.plan = []
        for index, doors in enumerate(all_doors):
            new_room = Room(self.game, self, doors)
            new_room.position = index
            self.plan.append(new_room)
            self.monsters_in_rooms[new_room] = []
         
    
    def create_rooms_plan(self, f:int, r:int) -> list:
        
        """
        Функция генерирует заготовки для всех комнат этажа замка.
        - f - это количество рядов в плане этажа
        - r - это количество комнат в одном ряду
        
        Возвращает список заготовок комнат с указанием, 
        с каким количеством других комнат каждая из них граничит
        """
        
        all_rooms = [2] * r
        if f > 2: 
            all_rooms += ([2] + [3] * (r - 2) + [2]) * (f - 2)
        if f > 1: 
            all_rooms += [2] * r
        return all_rooms
    
    
    def create_doors(self, f:int, r:int) -> list:
        
        """
        Функция случайным образом генерирует двери между комнатами.
        - f - это количество рядов в плане этажа
        - r - это количество комнат в одном ряду
        
        Возвращает список, который для каждой комнаты содержит список дверей.
        """
        
        all_rooms = self.create_rooms_plan(f, r)
        all_doors = []
        for _ in range(f * r):
            doors = []
            for _ in range(4):
                door = Door(self.game)
                doors.append(door)
            all_doors.append(doors)
        for index, doors in enumerate(all_doors):
            row = index // r
            room = index % r
            if f > 1 and r > 1:
                while sum(not door.empty for door in doors) < all_rooms[index]:
                    door = randomitem([door for door in doors if door.empty])
                    q = doors.index(door)
                    if q == 0 and row != 0:
                        doors[0].activate()
                        all_doors[index - r][2] = doors[0]
                    elif q == 2 and row < f - 1:
                        doors[2].activate()
                        all_doors[index + r][0] = doors[2]
                    elif q == 3 and room != 0:
                        doors[3].activate()
                        all_doors[index - 1][1] = doors[3]
                    elif q == 1 and room < r - 1:
                        doors[1].activate()
                        all_doors[index + 1][3] = doors[1]
        return all_doors
    
    
    def inhabit(self):
        
        """
        Функция населяет этаж замка всякими монстрами и штуками. 
        Отвечает за наполнение этажа всем содержимым.
        
        """    
        
        game = self.game
        
        # Создаем мебель и разбрасываем по замку
        self.all_furniture = game.create_objects_from_json(file='furniture.json',
                                        how_many=self.how_many['мебель'],
                                        random=True)
        for furniture in self.all_furniture:
            furniture.place(self)
        
        # Создаем очаги и разбрасываем по замку
        self.all_rest_places = game.create_objects_from_json(file='furniture-rest.json',
                                        how_many=self.how_many['очаг'],)
        self.all_rest_places[0].place(self, room_to_place=self.plan[0])
        for rest_place in self.all_rest_places[1:]:
            rest_place.place(self)
        
        # Читаем монстров из файла и разбрасываем по замку
        self.all_monsters = game.create_objects_from_json(file='monsters.json',
                                       how_many=self.how_many['монстры'])
        for monster in self.all_monsters:
            monster.place(self)
            self.game.how_many_monsters += 1
        
        # Читаем оружие из файла и разбрасываем по замку
        self.all_weapon = game.create_objects_from_json(file='weapon.json',
                                     how_many=self.how_many['оружие'])
        for weapon in self.all_weapon:
            weapon.place(self)
        
        # Читаем щиты из файла и разбрасываем по замку
        self.all_shields = game.create_objects_from_json(file='shields.json',
                                      how_many=self.how_many['щит'])
        for shield in self.all_shields:
            shield.place(self)
        
        # Читаем доспехи из файла и разбрасываем по замку
        self.all_armor = game.create_objects_from_json(file='armor.json',
                                    how_many=self.how_many['доспех'])
        for armor in self.all_armor:
            armor.place(self)
        
        # Читаем зелья из файла и разбрасываем по замку
        self.all_potions = game.create_objects_from_json(file='potions.json',
                                      how_many=self.how_many['зелье'])
        for potion in self.all_potions:
            potion.place(self)
        
        # Создаем руны и разбрасываем по замку
        self.all_runes = [Rune(self.game) for _ in range(self.how_many['руна'])]
        for rune in self.all_runes:
            rune.place(self)
        
        # Создаем книги и разбрасываем по замку
        self.all_books = game.create_objects_from_json(file='books.json',
                                    how_many=self.how_many['книга'],
                                    random=True)
        for book in self.all_books:
            book.place(self)
        new_map = Map(game)
        new_map.place(self) 
        matches = Matches(game)
        matches.place(self)
        for i in range(5):
            new_key = Key(game)
            self.plan[0].loot.add(new_key)
        new_loot = Loot(self.game)
        new_corpse = Corpse(self.game, 'Труп разбойника', new_loot, self.plan[0])
        new_key = Key(game)
        new_corpse.loot.add(new_key)

    
    def secret_rooms(self):
        return [i for i in self.plan if i.secret_word]
    
    
    def stink(self, room:Room, stink_level:int):
        """
        Функция распространения вони по замку.\n
        Распространяет вонь через открытые и закрытые двери, постепенно уменьшая уровень.\n
        Уровень вони записывается в параметр stink комнаты.

        Получает на вход:
            - room - Комната, с которой начинается распределение вони
            - stink_level - Начальный уровень вони

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
        for i, door in enumerate(room.doors):
            if not door.empty:
                available_directions.append(i)
        if stink_level > 1:
            for direction in available_directions:
                next_room = self.plan[room.position + directions[direction]]
                self.stink(next_room, stink_level - 1)
        return True

    
    def stink_map(self):
        
        """
        Генерирует карту вони этажа замка. 
        Нужна в основном для отладки, но может потом и понадобится.
        
        """
        
        for i in range(self.rows):
            floor = ''
            for j in range(self.rooms):
                floor = f'{floor + str(self.plan[i*self.rooms + j].stink)} '

    
    def lights_off(self):
        
        """
        Функция выключает свет в некоторых комнатах этажа замка.
        
        """
        
        self.how_many_dark_rooms = len(self.plan) // s_dark_rooms_ratio
        dark_rooms = randomitem(self.plan, False, self.how_many_dark_rooms)
        for room in dark_rooms:
            room.light = False

    
    def lock_doors(self):
        
        """
        Функция запирает двери некоторых случайных комнатах этажа замка.
        
        """
        
        how_many_locked_rooms = len(self.plan) // s_locked_rooms_ratio
        for _ in range(how_many_locked_rooms):
            room = randomitem([r for r in self.plan[1::] if not r.locked])
            new_money = Money(self.game, dice(s_min_money_in_locked_room, s_max_money_in_locked_room))
            room.lock()
            monster = room.monsters('random')
            if not monster:
                room.loot.add(new_money)
            else:
                monster.take(new_money)
            new_key = Key(self.game)
            new_key.place(self)
        return True

    
    def map(self):
        
        """
        Функция генерирует и выводит в чат карту этажа замка.
        
        """
        
        f = self.rows
        r = self.rooms
        game = self.game
        text = []
        text.append('======' * r + '=')
        for i in range(f):
            text.append('║' + '     ║' * r)
            line1 = '║'
            line2 = ''
            for j in range(r):
                room = self.plan[i*r+j]
                cant_rest, rest_place = room.can_rest()
                if game.player.current_position.position == i * r + j:    
                    a = game.player.name[0]
                elif rest_place and not room.visited == ' ':
                    a = '#'
                else: 
                    a = room.visited
                line1 += f'  {a}  {room.doors[1].vertical_symbol()}'
                line2 += f'==={room.doors[2].horizontal_symbol()}=='
            text.append(line1)
            text.append('║' + '     ║' * r)
            text.append(line2 + '=')
        pprint(game, text, r*s_map_width_coefficient, f*s_map_height_coefficient)
        
    
    def get_random_room_with_furniture(self) -> Room:
    
        """ Метод возвращает случайную комнату с мебелью. """
    
        rooms = [a for a in self.plan if a.furniture]
        return randomitem(rooms, False)
    
    def get_random_unlocked_room(self) -> Room:
        
        """ Метод возвращает случайную незапертую комнату. """
        
        rooms = [a for a in self.plan if (not a.locked)]
        return randomitem(rooms, False)
