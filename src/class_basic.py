from src.functions.functions import howmany, tprint

from typing import Union


class Loot:
    def __init__(self, game):
        self.game = game
        self.pile = []
        self.empty = False


    def __str__(self):
        return 'loot'


    def __add__(self, other) -> bool:
        if not isinstance(other, Loot):
            return False
        self.pile.extend(other.pile)
        return True
    
    
    def add(self, obj):
        self.pile.append(obj)


    def remove(self, obj):
        self.pile.remove(obj)
    
    
    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return len(self.pile) == other
        
    
    def is_item_in_loot(self, item) -> bool:
        return item in self.pile
    
    
    def reveal(self, room):
        for item in self.pile:
            room.loot.add(item)
            room.action_controller.add_actions(item)
        self.clear()
        return True
    
    
    def clear(self):
        self.pile=list()
        
    
    def transfer(self, other_loot):
        if not isinstance(other_loot, Loot):
            return False
        other_loot.pile.extend(self.pile)
        self.clear()
        return True
    
    
    def get_first_item_by_name(self, name:str):
        """
        Метод принимает на вход строку имени вещи и
        и возвращает первую найденную  по этому имени вещь.
        """
        name_lower = name.lower()
        for item in self.pile:
            if (name_lower in item.name.lower()) or (name_lower in item.lexemes['accus'].lower()):
                return item
        return False
    
    
    def get_all_items_by_name(self, name:str) -> list:
        """
        Метод принимает на вход строку имени вещи и
        и возвращает все найденные по этому имени вещи.
        """
        name_lower = name.lower()
        return [item for item in self.pile if (name_lower in item.name.lower()) or (name_lower in item.lexemes['accus'].lower())]

    
    def get_items_by_class(self, item_class) -> list:
        return [item for item in self.pile if type(item).__name__ == item_class]
        
        
    def show_sorted(self) -> list:
        items = self.pile
        items_dict = {}
        sorted_list = []
        for item in items:
            item_name = item.name.capitalize()
            if item_name in items_dict.keys():
                items_dict[item_name] += 1
            else:
                items_dict[item_name] = 1
        for item in items_dict:
            if items_dict[item] == 1:
                sorted_list.append(item)
            else:
                quantity = howmany(items_dict[item], ['штука', 'штуки', 'штук'])
                sorted_list.append(f'{item} ({quantity})')
        return sorted_list 


class Money:
    
    _groups = (10, 20, 30)
    """Значения для разделения денег на кучки."""

    _piles = (
        {
            "nom": "несколько монет",
            "accus": "несколько монет",
            "gen": "нескольких монет",
            "dat": "нескольким монетам",
            "prep": "нескольких монетах",
            "inst": "несколькими монетами"
        },
        {
            "nom": "кучка монет",
            "accus": "кучку монет",
            "gen": "кучки монет",
            "dat": "кучке монет",
            "prep": "кучке монет",
            "inst": "кучкой монет"
        },
        {
            "nom": "груда монет",
            "accus": "груду монет",
            "gen": "груды монет",
            "dat": "груде монет",
            "prep": "груде монет",
            "inst": "грудой монет"
        },
        {
            "nom": "много монет",
            "accus": "много монет",
            "gen": "много монет",
            "dat": "много монет",
            "prep": "много монет",
            "inst": "много монет"
        },
    )
    """Текстовые обозначения для кучек с разным количеством монет"""
    
    def __init__(self, game, how_much_money):
        self.game = game
        self.how_much_money = how_much_money
        self.empty = False
        self.generate_name()
        self.hero_actions = {}
        self.room_actions = {
            "взять": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False
                },
            "брать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False
                },
            "собрать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False
                }
        }

    
    def generate_name(self):
        piles = {
            0 <= self.how_much_money and self.how_much_money <= Money._groups[0]: 0,
            Money._groups[0] < self.how_much_money and self.how_much_money <= Money._groups[1]: 1,
            Money._groups[1] < self.how_much_money and self.how_much_money <= Money._groups[2]: 2, 
            Money._groups[2] < self.how_much_money: 3
        }
        self.lexemes = Money._piles[piles[True]]
        self.name = self.lexemes['nom']

    
    def check_name(self, message:str) -> bool:
        return message.lower() in ['деньги', self.lexemes["nom"], self.lexemes["accus"]]
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
    def __repr__(self):
        return str(self.how_much_money)
    
    
    def __int__(self) -> int:
        return self.how_much_money

    
    def __eq__(self, other:Union[int, 'Money']) -> bool:
        if isinstance(other, int):
            return self.how_much_money == other
        if isinstance(other, Money):
            return self.how_much_money == other.how_much_money

    
    def __ge__(self, other:Union[int, 'Money']) -> bool:
        if isinstance(other, int):
            return self.how_much_money >= other
        if isinstance(other, Money):
            return self.how_much_money >= other.how_much_money
    
    
    def __gt__(self, other:Union[int, 'Money']) -> bool:
        if isinstance(other, int):
            return self.how_much_money > other
        if isinstance(other, Money):
            return self.how_much_money > other.how_much_money
    
    
    def __le__(self, other:Union[int, 'Money']) -> bool:
        if isinstance(other, int):
            return self.how_much_money <= other
        if isinstance(other, Money):
            return self.how_much_money <= other.how_much_money
    
    
    def __lt__(self, other:Union[int, 'Money']) -> bool:
        if isinstance(other, int):
            return self.how_much_money < other
        if isinstance(other, Money):
            return self.how_much_money < other.how_much_money

    
    def __add__(self, other:Union[int, 'Money']) -> 'Money':
        if isinstance(other, int):
            self.how_much_money += other
        elif isinstance(other, Money):
            self.how_much_money += other.how_much_money
        self.generate_name()
        return self

    
    def __sub__(self, other:Union[int, 'Money']) -> 'Money':
        if isinstance(other, int):
            self.how_much_money -= other
        elif isinstance(other, Money):
            self.how_much_money -= other.how_much_money
        self.generate_name()
        return self


    def take(self, who, in_action:bool=False) -> str:
        who.money += self
        who.current_position.loot.remove(self)
        return f'{who.name} {who.g("забрал", "забрала")} {howmany(self.how_much_money, ["монету", "монеты", "монет"])}'


    def show(self):
        if self >= 1:
            return howmany(self.how_much_money, ["монета", "монеты", "монет"])
        else:
            return 'Денег нет'
        

    def get_sum(self) ->int:
        return self.how_much_money
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        names_list = ['деньги', 'монеты']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list