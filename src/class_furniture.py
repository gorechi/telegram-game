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
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "condition": "is_locked",
                "post_process": "after_unlock",
                "duration": 2
                },
            "обыскать": {
                "method": "search",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "after_search",
                "duration": 2
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 1
                },
        }

    
    def __str__(self):
        """
        Возвращает строковое представление мебели.
        """
        return self.where + ' ' + self.state + ' ' + self.name
    
    
    def after_unlock(self, who):
        """
        Выполняется после отпирания мебели.
        """
        return
    
    
    def after_search(self, who):
        """
        Выполняется после обыска мебели.
        """
        return
    
    
    def is_locked(self, room=None) -> bool:
        """
        Проверяет, заперта ли мебель.
        """
        return self.locked

    
    def unlock(self, who, in_action:bool=False) -> str:
        """
        Метод отпирания мебели при помощи ключа.
        """
        if not self.locked:
            return 'Тут не заперто, можно без проблем посмотреть, что там внутри.'
        key = who.backpack.get_first_item_by_class('Key')
        if not key:
            return f'У {who:gen} нет подходящего ключа чтобы что-то отпирать.'
        who.backpack.remove(key)
        self.locked = False
        return f'{who.name} отпирает {self:accus} ключом.'

    
    def __format__(self, format:str) -> str:
        """
        Возвращает строку с названием мебели в нужном падеже.
        """
        return self.lexemes.get(format, '')
    
    
    def on_create(self):
        """
        Выполняется при создании мебели.
        """
        return True

    
    def put(self, item):
        """
        Помещает предмет в мебель.
        """
        self.loot.pile.append(item)
    
    
    def check_trap(self) -> bool:
        """
        Проверяет, есть ли в мебели ловушка.
        """
        if self.trap.activated:
            return True
        return False
   
    
    def monster_in_ambush(self):
        """
        Проверяет, прячется ли в мебели монстр.
        """
        monsters = self.room.monsters()
        if monsters:
            for monster in monsters:
                if monster.hiding_place == self:
                    return monster 
        return False
    
    
    def get_names_list(self, cases:list=[], room=None) -> list:
        """
        Возвращает список имен мебели в разных падежах.
        """
        names_list = self.basic_lexemes
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list


    def check_name(self, message:str) -> bool:
        """
        Проверяет, соответствует ли сообщение названию мебели.
        """
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def show(self):
        """
        Возвращает описание мебели.
        """
        message = []
        message.append(f'{self.where} {self.state} {self.name}.')
        if self.monster_in_ambush():
            message.append('Внутри слышится какая-то возня.')
        return message

    
    def place(self, floor=None, room_to_place=None):
        """
        Размещает мебель в комнате.
        """
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
        monster = self.monster_in_ambush()
        if monster:
            self.game.events_controller.create_event(
                event_subject = monster,
                method_name = 'attack_from_ambush',
                event_object = who
            )
            return False
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