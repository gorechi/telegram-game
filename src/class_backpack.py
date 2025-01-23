from src.functions.functions import randomitem, tprint
from src.class_weapon import Weapon

class Backpack:
    
    def __init__(self,
                 game,
                 no_backpack=False
                 ) -> None:
        self.insides = []
        self.name = 'рюкзак'
        self.game = game
        self.no_backpack = no_backpack
        self.owner = None
        self.lexemes = {
            "nom": "рюкзак",
            "accus": "рюкзак",
            "gen": "рюкзака",
            "dat": "рюкзаку",
            "prep": "рюкзаке",
            "inst": "рюкзаком"
        }
        self.hero_actions = {
            "осмотреть": {
                "method": "show",
                "batch": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "get_name_for_show",
                },
            "проверить": {
                "method": "show",
                "batch": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "get_name_for_show",
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True,
                },
            "снять": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True,
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True,
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True,
                },
        }
        self.room_actions = {
            "взять": {
                "method": "take",
                "batch": False,
                "in_combat": False,
                "in_darkness": False
                },
            "брать": {
                "method": "take",
                "batch": False,
                "in_combat": False,
                "in_darkness": False
                },
            "забрать": {
                "method": "take",
                "batch": False,
                "in_combat": False,
                "in_darkness": False
                }
        }

    
    def get_name_for_show(self, who) -> str:
        return "Рюкзак героя"
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
    def check_name(self, message:str) -> bool:
        return message.lower() in [self.name, self.lexemes["accus"]]
    
    
    def append(self, item):
        """Метод добавления вещи в рюкзак"""
        
        self.insides.append(item)
        item.place = self


    def __add__(self, item):
        """Метод добавления вещи в рюкзак"""
        
        self.append(item)
    
        
    def remove(self, item, place=None):
        """
        Метод извлечения вещи из рюкзака.
        """
        
        self.insides.remove(item)
        item.place = place
    
    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания рюкзака.
        """
        room = who.current_position
        room.loot.add(self)
        who.action_controller.delete_actions_by_item(self)
        room.action_controller.add_actions(self)
        who.backpack = who.game.no_backpack
        return f'{who.name} снимает рюкзак и кладет в угол комнаты.'
        
    
    def get_items_by_class(self, item_class) -> list:
        return [item for item in self.insides if isinstance(item, item_class)]

    
    def get_items_list(self) -> list:
        return self.insides
    
    
    def get_first_item_by_name(self, name:str):
        """
        Метод принимает на вход строку имени вещи и
        и возвращает первую найденную в рюкзаке по этому имени вещь.
        """
        
        for item in self.insides:
            if item.check_name(name):
                return item
        return False


    def get_first_item_by_class(self, item_class):
        """
        Метод принимает на вход класс вещи и
        и возвращает первую найденную в рюкзаке вещь этого класса.
        """
        
        for item in self.insides:
            if isinstance(item, item_class):
                return item
        return False

    
    def count_items(self) -> int:
        return len(self.insides)
    
    
    def is_empty(self) -> bool:
        return len(self.insides) == 0
    
    
    def get_items_except_class(self, item_class) -> list:
        return [item for item in self.insides if not isinstance(item, item_class)]
    
    
    def get_random_item(self):
        if not self.is_empty():
            return randomitem(self.insides)
        return False


    def get_random_item_by_class(self, item_class):
        items_list = [item for item in self.insides if isinstance(item, item_class)]
        if items_list:
            return randomitem(items_list)
        return False

    
    def get_items_for_fight(self) -> list:
        """
        Метод возвращает список вещей, 
        которые герой может использовать в бою. 
        
        """
        
        can_use = []
        for i in self.insides:
            if i.can_use_in_fight:
                can_use.append(i)
        return can_use


    def show(self, who, in_action:bool=False) -> list:
        """Метод генерирует описание рюкзака."""
        
        message = []
        if self.no_backpack:
            return [f'У {who.g("героя", "героини")} нет рюкзака, поэтому и осматривать нечего.']
        if self.is_empty():
            return [f'{who.name} осматривает свой рюкзак и обнаруживает, что тот абсолютно пуст.']
        message.append(f'{who.name} осматривает свой рюкзак и обнаруживает в нем:')
        for i, item in enumerate(self.insides):
            description = f'{str(i + 1)}: {item.show()}'
            if isinstance(item, Weapon):
                weapon_mastery = who.weapon_mastery[item.type]['level']
                if weapon_mastery > 0:
                    description += f', мастерство - {weapon_mastery}'
            message.append(description)
        return message
    

    def get_item_by_number(self, number:int):
        if not isinstance (number, int):
            return False
        item_index = number - 1
        if item_index < self.count_items():
            return self.insides[item_index]
        return False
    
    
    def take(self, who, in_action:bool=False) -> str:
        room = who.current_position
        if not who.backpack.no_backpack:
            return f'{who.name} не может надеть новый рюкзак поверх своего рюкзака. Это уже слишком.'
        who.backpack = self
        self.owner = who
        who.action_controller.add_actions(self)
        room.action_controller.delete_actions_by_item(self)
        return f'{who.name} радостно надевает рюкзак. Наконец-то {who:pronoun} может носить с собой необходимые вещи.'
    
    
    def get_names_list(self, cases:list=None) -> list:
        return ['рюкзак']