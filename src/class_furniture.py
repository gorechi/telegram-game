from src.class_items import Key
from src.class_room import Room
from src.class_dice import Dice
from src.functions.functions import randomitem

class Furniture:
    """Класс мебели."""
        
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
        self.room_actions = {
            "отпереть": {
                "method": "unlock",
                "batch": False,
                "in_combat": False,
                "in_darkness": False,
                "condition": "is_locked",
                "post_process": "after_unlock"
                },
            "обыскать": {
                "method": "search",
                "batch": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "after_search"
                },
            "осмотреть": {
                "method": "examine",
                "batch": False,
                "in_combat": False,
                "in_darkness": False,
                },
        }

    
    def __str__(self):
        return self.where + ' ' + self.state + ' ' + self.name
    
    
    def after_unlock(self, who):
        return
    
    
    def after_search(self, who):
        return
    
    
    def is_locked(self) -> bool:
        return self.locked

    
    def unlock(self, who, in_action:bool=False) -> str:
        """
        Метод отпирания мебели при помощи ключа.
        """
        if not self.locked:
            return 'Тут не заперто, можно без проблем посмотреть, что там внутри.'
        key = who.backpack.get_first_item_by_class(Key)
        if not key:
            return f'У {who:gen} нет подходящего ключа чтобы что-то отпирать.'
        who.backpack.remove(key)
        self.locked = False
        return f'{who.name} отпирает {self:accus} ключом.'

    
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
    
    
    def get_names_list(self, cases:list=[]) -> list:
        names_list = self.basic_lexemes
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
        self.room.action_controller.add_actions(self)
        return True
    
    
    def search(self, who, in_action:bool=False) -> list[str]:
        """
        Метод обыскивания мебели.
        """
        room = who.current_position
        if self.locked:
            return f'Нельзя обыскать {self:accus}. Там заперто.'
        # if what_to_search.check_trap():
        #     tprint(game, f'К несчастью в {what_to_search:prep} кто-то установил ловушку.')
        #     what_to_search.trap.trigger(self)
        #     return False
        # if self.check_monster_in_ambush(place=what_to_search):
        #     return False
        if self.loot == 0:
            return f'{self.name} {self.empty_text}'.capitalize()
        message = [f'{who.name} осматривает {self:accus} и находит:']
        message += self.loot.show_sorted()
        self.loot.reveal(room)
        message.append('Все, что было спрятано, теперь лежит на виду.')
        return message
    
    
    def examine(self, who, in_action:bool=False) -> list[str]:
        """
        Метод генерирует текст осмотра мебели.
        """
        message = list()
        message += (self.show())
        if self.trap.activated and who.detect_trap(self.trap):
            message.append(self.trap.get_detection_text())
        return message