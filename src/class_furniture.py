from src.class_items import Key
from src.class_room import Room
from src.class_dice import Dice
from src.functions.functions import randomitem

class Furniture:
    """Класс мебели."""
    
    _basic_lexemes = {
        "полка": ['полка', 'полку'],
        "шкаф": ['шкаф'],
        "сундук": ['сундук'],
        "очаг": ['очаг']
    }
    
    _lock_dice = Dice([4])
    """Вероятность того, что мебель будет заперта (если 4, то 1/4)."""
   
    def __init__(self, game):
        """
        Инициализирует объект класса мебели

        """

        self.game = game
        self.locked:bool = False
        self.opened:bool = True
        self.empty:bool = False
        self.room:Room = None

    
    def __str__(self):
        return self.where + ' ' + self.state + ' ' + self.name
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
    def on_create(self):
        return True

    
    def put(self, item):
        self.loot.pile.append(item)
    
    
    def check_trap(self) -> bool:
        if self.trap.activated:
            return True
        return False
   
    
    def monster_in_ambush(self):
        monsters = self.room.monsters()
        if monsters:
            for monster in monsters:
                if monster.hiding_place == self:
                    return monster 
        return False
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = Furniture._basic_lexemes[self.name]
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list


    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def show(self):
        message = []
        message.append(f'{self.where} {self.state} {self.name}.')
        if self.monster_in_ambush():
            message.append('Внутри слышится какая-то возня.')
        return message

    
    def place(self, floor=None, room_to_place=None):
        if room_to_place:
            if self.furniture_type not in room_to_place.furniture_types():
                room_to_place.furniture.append(self)
                self.room = room_to_place
            else:
                return False
        else:
            can_place = False
            while not can_place:
                room = randomitem(floor.plan)
                if self.furniture_type not in room.furniture_types():
                    can_place = True
            room.furniture.append(self)
            self.room = room
        if Furniture._lock_dice.roll() == 1 and self.lockable:
            self.locked = True
            very_new_key = Key(self.game)
            very_new_key.place(floor)
        return True
