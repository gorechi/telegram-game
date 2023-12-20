from functions import howmany, normal_count, randomitem, tprint, roll
from class_weapon import Weapon

class Backpack:
    
    def __init__(self) -> None:
        self.insides = []
        
    
    def append(self, item):
        self.insides.append(item)


    def __add__(self, item):
        self.insides.append(item)
    
        
    def remove(self, item):
        self.insides.remove(item)
        
    
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
            if name.lower() in [item.name.lower(), item.name1.lower()]:
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


    def show(self, who) -> list:
        """Метод генерирует описание рюкзака."""
        
        message = []
        if self.is_empty():
            message.append(f'{who.name} осматривает свой рюкзак и обнаруживает, что тот абсолютно пуст.')
        else:
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
