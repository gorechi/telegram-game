from dataclasses import dataclass

from src.class_castle import Floor
from src.class_room import Room, Door
from src.class_controller import Controller
from src.class_basic import Money
from src.class_items import Key
from src.functions.functions import randomitem

class FloorsController(Controller):
    """Класс для управления этажами замка."""

    @dataclass
    class Template():
        class_name: str
        floor_number: int
        rows: int
        rooms: int
        traps_difficulty: int
        how_many: dict
        how_many_dark_rooms: int
        how_many_locked_rooms: int
        money_in_locked_rooms: dict 
        boss: bool   
    
    
    _classes = {
        "Floor": Floor
    }
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/floors.json')
        self.all_objects = []
    
    
    def additional_actions(self, floor) -> bool:
        self.create_rooms(floor)
        self.lock_doors(floor)
        self.lights_off(floor)
        self.generate_directions(floor)
        return True
    
    
    def create_rooms(self, floor):    
        
        """
        Функция генерирует комнаты этажа замка.
        """
        f = floor.rows
        r = floor.rooms
        all_doors = self.create_doors(f, r)
        floor.plan = []
        for index, doors in enumerate(all_doors):
            new_room = Room(self.game, floor, doors)
            new_room.position = index
            floor.plan.append(new_room)
            floor.monsters_in_rooms[new_room] = []
    
    
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
            doors = [Door(self.game) for _ in range(4)]
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
    
    
    def lock_doors(self, floor):
        
        """
        Функция запирает двери некоторых случайных комнатах этажа замка.
        
        """
        
        for _ in range(floor.how_many_locked_rooms):
            room = randomitem([r for r in floor.plan[1::] if not r.locked])
            new_money = Money(self.game, floor.money_in_locked_rooms.roll())
            room.lock()
            monster = room.monsters('random')
            if not monster:
                room.loot.add(new_money)
            else:
                monster.take(new_money)
            new_key = Key(self.game)
            new_key.place(floor)
        return True
    

    def lights_off(self, floor):
        
        """
        Функция выключает свет в некоторых комнатах этажа замка.
        
        """
        
        dark_rooms = randomitem(floor.plan, floor.how_many_dark_rooms)
        if isinstance(dark_rooms, list):
            for room in dark_rooms:
                room.light = False
        if isinstance(dark_rooms, Room):
            dark_rooms.light = False
    
            
    def create_castle(self):
        self.floors = []
        sorted_templates = sorted(self.templates, key=lambda floor: floor.floor_number)
        for template in sorted_templates:
            floor = self.create_object_from_template(template)
            self.floors.append(floor)
        self.create_ladders()
        self.inhabit_floors()
        return self.floors
    
    
    def create_ladders(self):
        self.floors[0].plan[0].enter_point = True
        for index, floor in enumerate(self.floors[:-1]):
            floor.create_ladders(next_floor=self.floors[index + 1])
        return True
            
    
    def inhabit_floors(self):
        for floor in self.floors:
            floor.inhabit()
        return True
    
    
    def generate_directions(self, floor):
        directions_dict = {
            0: -floor.rooms,
            1: 1,
            2: floor.rooms,
            3: -1,
            'наверх': -floor.rooms,
            'направо': 1,
            'вправо': 1,
            'налево': -1,
            'лево': -1,
            'влево': -1,
            'вниз': floor.rooms,
            'низ': floor.rooms,
            'вверх': -floor.rooms,
            'верх': -floor.rooms,
            'право': 1
            }
        floor.directions_dict = directions_dict