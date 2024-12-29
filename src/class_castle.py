from random import randint as dice

from src.class_basic import Money
from src.class_book import Book
from src.class_potions import Potion
from src.class_items import Key, Map, Matches, Rune
from src.class_room import Door, Room, Ladder
from src.class_allies import Trader
from src.functions.functions import randomitem


class Floor:
    
    _dark_rooms_ratio = 8
    """Какая часть комнат этажа будет темными (если 5, то будет каждая пятая комната)."""
    
    _locked_rooms_ratio = 8
    """Какая часть комнат этажа будет заперта (если 5, то будет каждая пятая комната)."""
    
    _min_money_in_locked_room = 15
    """Минимальное количество денег в запертой комнате."""
    
    _max_money_in_locked_room = 40
    """Максимальное количество денег в запертой комнате."""
        
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
                
    
    def get_rooms_around(self, room:Room, ladders:bool=True) -> list[Room]:
        directions = {0: -self.rooms,
                      1: 1,
                      2: self.rooms,
                      3: -1}
        available_rooms = []
        for i, door in enumerate(room.doors):
            if door and not door.locked:
                available_rooms.append(self.plan[room.position + directions[i]])
        if ladders:
            if room.ladder_down and not room.ladder_down.locked:
                available_rooms.append(room.ladder_down.room_down)
            if room.ladder_up and not room.ladder_up.locked:
                available_rooms.append(room.ladder_up.room_up)
        return available_rooms
    
    def create_ladders(self) -> bool:
        next_floor = self.game.get_floor_by_number(self.floor_number + 1)
        if not next_floor:
            return False
        for _ in range(self.how_many['лестницы']):
            room = self.get_room_to_place_ladder_up()
            room_to_go = next_floor.get_room_to_place_ladder_down()
            new_ladder = Ladder(room, room_to_go)  # noqa: F841
        return True
    
    
    def get_room_to_place_ladder_up(self) -> Room:
        rooms = [room for room in self.plan if not room.ladder_up]
        return randomitem(rooms)
    
    
    def get_room_to_place_ladder_down(self) -> Room:
        rooms = [room for room in self.plan if not room.ladder_down]
        return randomitem(rooms)
    
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
        self.place_furniture()
        
        # Создаем очаги и разбрасываем по замку
        self.place_rest_places()
        
        # Создаем торговцев и рассаживаем по этажу
        self.place_traders()
        
        # Читаем монстров из файла и разбрасываем по замку
        self.place_monsters()
        
        # Читаем оружие из файла и разбрасываем по замку
        self.place_weapons()
        
        # Читаем щиты из файла и разбрасываем по замку
        self.place_shields()
        
        # Читаем доспехи из файла и разбрасываем по замку
        self.place_armor()
        
        # Читаем зелья из файла и разбрасываем по замку
        self.place_potions()
        
        # Создаем руны и разбрасываем по замку
        self.place_runes()
        
        # Создаем книги и разбрасываем по замку
        self.place_books()
        
        # Помещаем на этаж карту
        self.place_map() 
        
        # Помещаем на этаж спички
        self.place_matches()

     
    def place_matches(self):
        matches = Matches(self.game)
        matches.place(self)

    
    def place_traders(self):
        for _ in range(self.how_many['торговец']):
            trader = Trader.random_trader(self.game, self)
            trader.place()
    
    
    def place_map(self):
        new_map = Map(self.game, self)
        new_map.place()

    
    def place_books(self):
        for _ in range(self.how_many['книга']):
            new_book = self.game.books_controller.get_random_object_by_filters()
            new_book.place(self)

    
    def place_runes(self):
        for _ in range(self.how_many['руна']):
            new_rune = self.game.runes_controller.get_random_object_by_filters()
            new_rune.place(self)
    
    
    def activate_traps(self):
        all_furnitures = [f for f in self.all_furniture if f.can_contain_trap and not f.trap.activated]
        furnitures = randomitem(all_furnitures, how_many=self.how_many['ловушка'])
        for f in furnitures:
            f.trap.activate()
            f.trap.set_difficulty(self.traps_difficulty)

    
    def place_potions(self):
        self.all_potions = [] 
        for _ in range(self.how_many['зелье']):
            new_potion = self.game.potions_controller.get_random_object_by_filters()
            self.all_potions.append(new_potion)
            new_potion.place(self)

    
    def place_armor(self):
        self.all_armor = self.game.protection_controller.get_random_objects_by_class_name(
            class_name = 'Armor',
            how_many=self.how_many['доспех'],
        )
        for armor in self.all_armor:
            armor.place(self)

    
    def place_shields(self):
        self.all_shields = self.game.protection_controller.get_random_objects_by_class_name(
            class_name = 'Shield',
            how_many=self.how_many['щит'],
        )
        for shield in self.all_shields:
            shield.place(self)

    
    def place_weapons(self):
        self.all_weapon = self.game.weapon_controller.get_random_objects_by_class_name(
            class_name = 'Weapon',
            how_many=self.how_many['оружие'],
        )
        for weapon in self.all_weapon:
            weapon.place(self)
            print(weapon)

    
    def place_monsters(self):
        self.all_monsters = self.game.monsters_controller.create_monsters_by_floor(
            self.floor_number,
            self.how_many['монстры']
        )
        for monster in self.all_monsters:
            monster.place(self)

    
    def place_rest_places(self):
        self.all_rest_places = self.game.create_objects_from_json(file='json/furniture-rest.json',
                                        how_many=self.how_many['очаг'],)
        self.all_rest_places[0].place(self, room_to_place=self.plan[0])
        for rest_place in self.all_rest_places[1:]:
            rest_place.place(self)

    
    def place_furniture(self):
        self.all_furniture = self.game.create_objects_from_json(file='json/furniture.json',
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
        if room.stink >= stink_level:
            return True
        else:
            room.stink = stink_level
        available_rooms = self.get_rooms_around(room)
        if stink_level > 1:
            for next_room in available_rooms:
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
        dark_rooms = randomitem(self.plan, self.how_many_dark_rooms)
        if isinstance(dark_rooms, list):
            for room in dark_rooms:
                room.light = False
        if isinstance(dark_rooms, Room):
            dark_rooms.light = False

    
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
        
    
    def get_random_room_with_furniture(self) -> Room:
    
        """ Метод возвращает случайную комнату с мебелью. """
    
        rooms = [a for a in self.plan if a.furniture]
        return randomitem(rooms)
    
    
    def get_random_unlocked_room(self) -> Room:
        
        """ Метод возвращает случайную незапертую комнату. """
        
        rooms = [a for a in self.plan if (not a.locked)]
        return randomitem(rooms)
