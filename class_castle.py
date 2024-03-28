from random import randint as dice

from class_basic import Money
from class_items import Key, Map, Matches, Rune, Book
from class_room import Door, Room
from functions import pprint, randomitem


class Floor:
    
    _dark_rooms_ratio = 8
    """Какая часть комнат замка будет темными (если 5, то будет каждая пятая комната)."""
    
    _locked_rooms_ratio = 8
    """Какая часть комнат замка будет заперта (если 5, то будет каждая пятая комната)."""
    
    _min_money_in_locked_room = 15
    """Минимальное количество денег в запертой комнате."""
    
    _max_money_in_locked_room = 40
    """Максимальное количество денег в запертой комнате."""
    
    _map_width_coefficient = 72
    """Коэффициент для расчета ширины карты."""
    
    _map_height_coefficient = 90
    """Коэффициент для расчета высоты карты."""
    
    def __init__(self, game, floor_number:int, data:dict):
        self.game = game
        self.floor_number = floor_number
        print(f'floor number = {self.floor_number}')
        self.rows = data['rows']
        self.rooms = data['rooms']
        self.traps_difficulty = data['traps_difficulty']
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
        self.how_many = data['how_many']
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
        self.place_furniture(game)
        
        # Создаем очаги и разбрасываем по замку
        self.place_rest_places(game)
        
        # Читаем монстров из файла и разбрасываем по замку
        self.place_monsters(game)
        
        # Читаем оружие из файла и разбрасываем по замку
        self.place_weapons(game)
        
        # Читаем щиты из файла и разбрасываем по замку
        self.place_shields(game)
        
        # Читаем доспехи из файла и разбрасываем по замку
        self.place_armor(game)
        
        # Читаем зелья из файла и разбрасываем по замку
        self.place_potions(game)
        
        # Создаем руны и разбрасываем по замку
        self.place_runes()
        
        # Создаем книги и разбрасываем по замку
        self.place_books(game)
        
        self.place_map(game) 
        self.place_matches(game)

    
    def place_matches(self, game):
        matches = Matches(game)
        matches.place(self)

    
    def place_map(self, game):
        new_map = Map(game)
        new_map.place(self)

    
    def place_books(self, game):
        for _ in range(self.how_many['книга']):
            new_book = Book(self.game)
            new_book.place(self)

    
    def place_runes(self):
        self.all_runes = [Rune(self.game) for _ in range(self.how_many['руна'])]
        for rune in self.all_runes:
            rune.place(self)
    
    
    def activate_traps(self):
        all_furnitures = [f for f in self.all_furniture if f.can_contain_trap and not f.trap.activated]
        furnitures = randomitem(all_furnitures, how_many=self.how_many['ловушка'])
        for f in furnitures:
            f.trap.activate()
            f.trap.set_difficulty(self.traps_difficulty)

    
    def place_potions(self, game):
        self.all_potions = game.create_objects_from_json(file='potions.json',
                                      how_many=self.how_many['зелье'], 
                                      random=True)
        for potion in self.all_potions:
            potion.place(self)

    
    def place_armor(self, game):
        self.all_armor = game.create_objects_from_json(file='armor.json',
                                    how_many=self.how_many['доспех'],
                                    random=True)
        for armor in self.all_armor:
            armor.place(self)

    
    def place_shields(self, game):
        self.all_shields = game.create_objects_from_json(file='shields.json',
                                      how_many=self.how_many['щит'],
                                      random=True)
        for shield in self.all_shields:
            shield.place(self)

    
    def place_weapons(self, game):
        self.all_weapon = game.create_objects_from_json(file='weapon.json',
                                     how_many=self.how_many['оружие'],
                                     random=True)
        for weapon in self.all_weapon:
            weapon.place(self)

    
    def place_monsters(self, game):
        self.all_monsters = game.create_objects_from_json(file='monsters.json',
                                       how_many=self.how_many['монстры'],
                                       random=True,
                                       floor=self.floor_number)
        for monster in self.all_monsters:
            monster.place(self)
            self.game.how_many_monsters += 1

    
    def place_rest_places(self, game):
        self.all_rest_places = game.create_objects_from_json(file='furniture-rest.json',
                                        how_many=self.how_many['очаг'],)
        self.all_rest_places[0].place(self, room_to_place=self.plan[0])
        for rest_place in self.all_rest_places[1:]:
            rest_place.place(self)

    
    def place_furniture(self, game):
        self.all_furniture = game.create_objects_from_json(file='furniture.json',
                                        how_many=self.how_many['мебель'],
                                        random=True)
        for furniture in self.all_furniture:
            furniture.place(self)

    
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
        
        self.how_many_dark_rooms = len(self.plan) // Floor._dark_rooms_ratio
        dark_rooms = randomitem(self.plan, False, self.how_many_dark_rooms)
        for room in dark_rooms:
            room.light = False

    
    def lock_doors(self):
        
        """
        Функция запирает двери некоторых случайных комнатах этажа замка.
        
        """
        
        how_many_locked_rooms = len(self.plan) // Floor._locked_rooms_ratio
        for _ in range(how_many_locked_rooms):
            room = randomitem([r for r in self.plan[1::] if not r.locked])
            new_money = Money(self.game, dice(Floor._min_money_in_locked_room, Floor._max_money_in_locked_room))
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
        pprint(game, text, r*Floor._map_width_coefficient, f*Floor._map_height_coefficient)
        
    
    def get_random_room_with_furniture(self) -> Room:
    
        """ Метод возвращает случайную комнату с мебелью. """
    
        rooms = [a for a in self.plan if a.furniture]
        return randomitem(rooms, False)
    
    
    def get_random_unlocked_room(self) -> Room:
        
        """ Метод возвращает случайную незапертую комнату. """
        
        rooms = [a for a in self.plan if (not a.locked)]
        return randomitem(rooms, False)
