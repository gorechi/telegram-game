from src.functions.functions import howmany

from typing import Union


class Loot:
    """
    Класс для управления лутом.    
    """
    def __init__(self, game):
        self.game = game
        self.pile = []
        self.empty = False


    def __str__(self):
        """
        Метод возвращает строковое представление лута.
        """
        return 'loot'


    def __add__(self, other) -> bool:
        """
        Метод объединяет два лута в один.
        """
        if not isinstance(other, Loot):
            return False
        self.pile.extend(other.pile)
        return True
    
    
    def add(self, obj):
        """
        Метод добавляет объект в лут.
        """
        self.pile.append(obj)


    def remove(self, obj):
        """
        Метод удаляет объект из лута.
        """
        self.pile.remove(obj)
    
    
    def __eq__(self, other) -> bool:
        """
        Метод сравнивает лут с числом по количеству предметов в нем.
        """
        if isinstance(other, int):
            return len(self.pile) == other
        
    
    def is_item_in_loot(self, item) -> bool:
        """
        Метод проверяет, есть ли предмет в луте.
        """
        return item in self.pile
    
    
    def reveal(self, room):
        """
        Метод перемещает все предметы из лута в комнату.
        """
        for item in self.pile:
            room.loot.add(item)
            room.action_controller.add_actions(item)
        self.clear()
        return True
    
    
    def clear(self):
        """
        Метод очищает лут.
        """
        self.pile=list()
        
    
    def transfer(self, other_loot):
        """
        Метод переносит все предметы из этого лута в другой лут.
        """
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
        """
        Метод принимает на вход класс вещи и
        и возвращает список вещей в луте этого класса.
        """
        return [item for item in self.pile if type(item).__name__ == item_class]
        
        
    def show_sorted(self) -> list:
        """
        Метод возвращает отсортированный список предметов в луте.
        """
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
    """
    Класс для управления деньгами.    
    """
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
                "in_darkness": False,
                "duration": 0
                },
            "брать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "собрать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                }
        }

    
    def generate_name(self):
        """
        Функция генерирует имя для кучи денег в зависимости от их количества.
        Варианты:
        0-10 - несколько монет
        11-20 - кучка монет
        21-30 - груда монет
        31 и больше - много монет
        """
        piles = {
            0 <= self.how_much_money and self.how_much_money <= Money._groups[0]: 0,
            Money._groups[0] < self.how_much_money and self.how_much_money <= Money._groups[1]: 1,
            Money._groups[1] < self.how_much_money and self.how_much_money <= Money._groups[2]: 2, 
            Money._groups[2] < self.how_much_money: 3
        }
        self.lexemes = Money._piles[piles[True]]
        self.name = self.lexemes['nom']

    
    def check_name(self, message:str) -> bool:
        """
        Функция проверяет, относится ли сообщение к деньгам.
        """
        return message.lower() in ['деньги', self.lexemes["nom"], self.lexemes["accus"]]
    
    
    def __format__(self, format:str) -> str:
        """
        Метод форматирования имени денег в различных падежах.
        """
        return self.lexemes.get(format, '')
    
    
    def __repr__(self):
        """
        Метод возвращает строковое представление денег.
        """
        return str(self.how_much_money)
    
    
    def __int__(self) -> int:
        """
        Метод возвращает количество денег как целое число.
        """
        return self.how_much_money

    
    def __eq__(self, other:Union[int, 'Money']) -> bool:
        """
        Метод сравнивает деньги с числом или с другим объектом класса Money по количеству денег.
        """
        if isinstance(other, int):
            return self.how_much_money == other
        if isinstance(other, Money):
            return self.how_much_money == other.how_much_money

    
    def __ge__(self, other:Union[int, 'Money']) -> bool:
        """
        Метод проверяет если денег больше или равно числа или другого объекта класса Money. 
        """
        if isinstance(other, int):
            return self.how_much_money >= other
        if isinstance(other, Money):
            return self.how_much_money >= other.how_much_money
    
    
    def __gt__(self, other:Union[int, 'Money']) -> bool:
        """
        Метод проверяет если денег строго больше числа или другого объекта класса Money.
        """
        if isinstance(other, int):
            return self.how_much_money > other
        if isinstance(other, Money):
            return self.how_much_money > other.how_much_money
    
    
    def __le__(self, other:Union[int, 'Money']) -> bool:
        """
        Метод проверяет если денег меньше или равно числа или другого объекта класса Money.
        """
        if isinstance(other, int):
            return self.how_much_money <= other
        if isinstance(other, Money):
            return self.how_much_money <= other.how_much_money
    
    
    def __lt__(self, other:Union[int, 'Money']) -> bool:
        """
        Метод проверяет если денег строго меньше числа или другого объекта класса Money.
        """
        if isinstance(other, int):
            return self.how_much_money < other
        if isinstance(other, Money):
            return self.how_much_money < other.how_much_money

    
    def __add__(self, other:Union[int, 'Money']) -> 'Money':
        """
        Метод увеличивает количество денег на заданное число или на количество другого объекта класса Money.
        """
        if isinstance(other, int):
            self.how_much_money += other
        elif isinstance(other, Money):
            self.how_much_money += other.how_much_money
        self.generate_name()
        return self

    
    def __sub__(self, other:Union[int, 'Money']) -> 'Money':
        """
        Метод уменьшает количество денег на заданное число или на количество другого объекта класса Money.
        """
        if isinstance(other, int):
            self.how_much_money -= other
        elif isinstance(other, Money):
            self.how_much_money -= other.how_much_money
        self.generate_name()
        return self


    def take(self, who, in_action:bool=False) -> str:
        """
        Метод позволяет герою или монстру взять деньги из комнаты.
        """
        who.money += self
        who.current_position.loot.remove(self)
        return f'{who.name} {who.g("забрал", "забрала")} {howmany(self.how_much_money, ["монету", "монеты", "монет"])}'


    def show(self):
        """
        Метод возвращает строковое представление денег.
        """
        if self >= 1:
            return howmany(self.how_much_money, ["монета", "монеты", "монет"])
        else:
            return 'Денег нет'
        

    def get_sum(self) ->int:
        """
        Метод возвращает количество денег как целое число.
        """
        return self.how_much_money
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """
        Метод возвращает список имен денег в различных падежах.
        """
        names_list = ['деньги', 'монеты']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list