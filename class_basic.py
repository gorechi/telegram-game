from functions import howmany, tprint
from settings import s_money_groups, s_money_piles
from class_backpack import Backpack


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
    
    
    def get_empty(self):
        self.pile=[]
        
    
    def transfer(self, other_loot):
        if not isinstance(other_loot, Loot):
            return False
        other_loot.pile.extend(self.pile)
        self.pile = []
        return True
    
    
    def get_first_item_by_name(self, name:str):
        """
        Метод принимает на вход строку имени вещи и
        и возвращает первую найденную  по этому имени вещь.
        """
        
        for item in self.pile:
            if name.lower() in [item.name.lower(), item.name1.lower()]:
                return item
        return False
    
    
    def get_all_items_by_name(self, name:str) -> list:
        """
        Метод принимает на вход строку имени вещи и
        и возвращает все найденные по этому имени вещи.
        """
        
        return [item for item in self.pile if name.lower() in [item.name.lower(), item.name1.lower()]]

    
    def get_items_by_class(self, item_class) -> list:
        return [item for item in self.insides if isinstance(item, item_class)]
        
        
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
                quantity = howmany(items_dict[item], 'штука,штуки,штук')
                sorted_list.append(f'{item} ({quantity})')
        return sorted_list 

class Money:
    def __init__(self, game, how_much_money):
        self.game = game
        self.how_much_money = how_much_money
        self.empty = False
        money_pile = 0
        if 0 < self.how_much_money <= s_money_groups[0]:
            money_pile = 0
        elif s_money_groups[0] < self.how_much_money <= s_money_groups[1]:
            money_pile = 1
        elif s_money_groups[1] < self.how_much_money <= s_money_groups[2]:
            money_pile = 2
        elif s_money_groups[2] < self.how_much_money:
            money_pile = 3
        self.name = s_money_piles[money_pile][0]
        self.name1 = s_money_piles[money_pile][1]

    def __repr__(self):
        return str(self.how_much_money)
    
    def __int__(self) -> int:
        return self.how_much_money
    
    def __eq__(self, other:int) -> bool:
        return self.how_much_money == other
    
    def __ge__(self, other:int) -> bool:
        return self.how_much_money >= other
    
    def __add__(self, other):
        if isinstance(other, int):
            self.how_much_money += other
        elif isinstance(other, Money):
            self.how_much_money += other.how_much_money
        else:
            raise TypeError('To Money you can only add integer or another Money.')
        return self
    
    def __sub__(self, other):
        if isinstance(other, int):
            self.how_much_money -= other
        elif isinstance(other, Money):
            self.how_much_money -= other.how_much_money
        else:
            raise TypeError('From Money you can only substract integer or another Money.')
        return self

    def take(self, lucky_one):
        lucky_one.money.how_much_money += self.how_much_money
        tprint(self.game, f'{lucky_one.name} {lucky_one.g(["забрал", "забрала"])} {howmany(self.how_much_money, "монету,монеты,монет")}')

    def show(self):
        if self >= 1:
            return howmany(self.how_much_money, 'монету,монеты,монет')
        else:
            return 'Денег нет'