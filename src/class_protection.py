from math import ceil
from random import randint as dice

from src.functions.functions import randomitem, tprint

from src.class_dice import Dice

class Protection:
    
    _elements_dictionary = {1: 'огня',
                        2: 'пламени',
                        3: 'воздуха',
                        4: 'света',
                        6: 'ветра',
                        7: 'земли',
                        8: 'лавы',
                        10: 'пыли',
                        12: 'воды',
                        13: 'пара',
                        14: 'камня',
                        15: 'дождя',
                        19: 'грязи',
                        24: 'потопа'}
    """Словарь стихий."""
    
    _weakness_dictionary = {1: [3, 3],
                            2: [3, 6],
                            3: [7, 7],
                            4: [3, 7],
                            6: [7, 14],
                            7: [12, 12],
                            8: [3, 12],
                            10: [7, 12],
                            12: [1, 1],
                            13: [1, 3],
                            14: [12, 24],
                            15: [1, 7],
                            19: [1, 12],
                            24: [1, 2]}
    """Словарь слабостей. Каждой стихии соответствует список слабых стихий."""

    _armor_decorators = {
    "кованый":
    [
        {
        "protection_modifier": 2,
        0: 
            {
            "nom": "Сияющий",
            "accus": "Сияющего",
            "gen": "Сияющего",
            "dat": "Сияющему",
            "prep": "Сияющем",
            "inst": "Сияющим",
            }, 
        1: 
            {
            "nom": "Сияющая",
            "accus": "Сияющую",
            "gen": "Сияющей",
            "dat": "Сияющей",
            "prep": "Сияющей",
            "inst": "Сияющей",
            }, 
        2: 
            {
            "nom": "Сияющее",
            "accus": "Сияющее",
            "gen": "Сияющего",
            "dat": "Сияющему",
            "prep": "Сияющем",
            "inst": "Сияющим",
        }
        },
        {
        "protection_modifier": -2,
        0: {
            "nom": "Ржавый",
            "accus": "Ржавого",
            "gen": "Ржавого",
            "dat": "Ржавому",
            "prep": "Ржавом",
            "inst": "Ржавым"
        },
        1: {
            "nom": "Ржавая",
            "accus": "Ржавую",
            "gen": "Ржавой",
            "dat": "Ржавой",
            "prep": "Ржавой",
            "inst": "Ржавой"
        },
        2: {
            "nom": "Ржавое",
            "accus": "Ржавое",
            "gen": "Ржавого",
            "dat": "Ржавому",
            "prep": "Ржавом",
            "inst": "Ржавым"
        }
        },
        {
        "protection_modifier": 0,
        0: {
            "nom": "Новый",
            "accus": "Нового",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        },
        1: {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой"
        },
        2: {
            "nom": "Новое",
            "accus": "Новое",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        }
        },
        {
        "protection_modifier": -1,
        0: 
            {
            "nom": "Помятый",
            "accus": "Помятого",
            "gen": "Помятого",
            "dat": "Помятому",
            "prep": "Помятом",
            "inst": "Помятым",
            }, 
        1: 
            {
            "nom": "Помятая",
            "accus": "Помятую",
            "gen": "Помятой",
            "dat": "Помятой",
            "prep": "Помятой",
            "inst": "Помятой",
            }, 
        2: 
            {
            "nom": "Помятое",
            "accus": "Помятое",
            "gen": "Помятого",
            "dat": "Помятому",
            "prep": "Помятом",
            "inst": "Помятым",
        }
        },
        {
        "protection_modifier": 1,
        0: 
            {
            "nom": "Крепкий",
            "accus": "Крепкого",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
            }, 
        1: 
            {
            "nom": "Крепкая",
            "accus": "Крепкую",
            "gen": "Крепкой",
            "dat": "Крепкой",
            "prep": "Крепкой",
            "inst": "Крепкой",
            }, 
        2: 
            {
            "nom": "Крепкое",
            "accus": "Крепкое",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
        }
        }
    ],
    "кожаный":
    [
        {
        "protection_modifier": 0,
        0: {
            "nom": "Новый",
            "accus": "Нового",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        },
        1: {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой"
        },
        2: {
            "nom": "Новое",
            "accus": "Новое",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        }
        },
        {
        "protection_modifier": 1,
        0: 
            {
            "nom": "Крепкий",
            "accus": "Крепкого",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
            }, 
        1: 
            {
            "nom": "Крепкая",
            "accus": "Крепкую",
            "gen": "Крепкой",
            "dat": "Крепкой",
            "prep": "Крепкой",
            "inst": "Крепкой",
            }, 
        2: 
            {
            "nom": "Крепкое",
            "accus": "Крепкое",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
        }
        },
        {
        "protection_modifier": 2,
        0: 
            {
            "nom": "Мощный",
            "accus": "Мощного",
            "gen": "Мощного",
            "dat": "Мощному",
            "prep": "Мощном",
            "inst": "Мощным",
            }, 
        1: 
            {
            "nom": "Мощная",
            "accus": "Мощную",
            "gen": "Мощной",
            "dat": "Мощной",
            "prep": "Мощной",
            "inst": "Мощной",
            }, 
        2: 
            {
            "nom": "Мощное",
            "accus": "Мощное",
            "gen": "Мощного",
            "dat": "Мощному",
            "prep": "Мощном",
            "inst": "Мощным",
        }
        },
        {
        "protection_modifier": -1,
        0: {
            "nom": "Дырявый",
            "accus": "Дырявого",
            "gen": "Дырявого",
            "dat": "Дырявому",
            "prep": "Дырявом",
            "inst": "Дырявым"
        },
        1: {
            "nom": "Дырявая",
            "accus": "Дырявую",
            "gen": "Дырявой",
            "dat": "Дырявой",
            "prep": "Дырявой",
            "inst": "Дырявой"
        },
        2: {
            "nom": "Дырявое",
            "accus": "Дырявое",
            "gen": "Дырявого",
            "dat": "Дырявому",
            "prep": "Дырявом",
            "inst": "Дырявым"
        }
        }
    ]
    }
    """Словарь декораторов для защины"""
    
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = True
        self.empty = False
        self.runes = []
        self.user = None
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    

    def __str__(self):
        name_string = f'{self:nom}' + self.enchantment()
        return f'{name_string} ({self.protection.get_text()})'
    
    
    def on_create(self):
        return True

    
    def check_name(self, message:str) -> bool:
        if self.empty:
            return False
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def is_poisoned(self):
        for i in self.runes:
            if i.poison:
                return True
        return False
    
    def element(self):
        element_sum = 0
        for rune in self.runes:
            element_sum += rune.element
        return element_sum

    
    def can_be_enchanted(self) -> bool:
        if len(self.runes) > 1 or self.empty or not self.enchatable:
            return False
        return True
    
    
    def enchant(self, rune):
        if self.can_be_enchanted():
            self.runes.append(rune)
            self.protection.increase_modificator(rune.defence)
            return True
        return False


    def enchantment(self):
        if len(self.runes) not in [1, 2]:
            return ''
        else:
            return ' ' + Protection._elements_dictionary[self.element()]


    def protect(self, who):
        if who.hide:
            who.hide = False
            return self.protection.roll()
        if who.weapon.empty or who.weapon.element() == 0 or self.element() == 0:
            return self.protection.roll()
        base_damage = [who.weapon.damage.base_die() // 2]
        if who.weapon.element() in Protection._weakness_dictionary[self.element()]:
            return self.perm_protection.roll(subtract=base_damage)
        elif self.element() in Protection._weakness_dictionary[who.weapon.element()]:
            return self.perm_protection.roll(add=base_damage)
        return self.protection.roll()

    
    def take(self, who):
        if who.shield == '':
            who.shield = self
            tprint(self.game, f'{who.name} использует {self:accus} как защиту.')
        else:
            self.game.player.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')

    
    def show(self) -> str:
        if self.empty:
            return None
        full_name = self.get_full_names('nom')
        return f'{full_name} ({self.protection.get_text()})'

    
    def get_full_names(self, key:str=None) -> str|list:
        if self.element != 0:
            return self.get_element_names(key)
        if key:
            return self.lexemes.get(key, '')
        return self.lexemes
    
    
    def use(self, who_using, in_action=False):
        if who_using.shield == '':
            who_using.shield = self
        else:
            who_using.backpack.append(who_using.shield)
            who_using.shield = self
            who_using.backpack.remove(self, who_using)
        tprint(self.game, f'{who_using.name} теперь использует {self:accus} в качестве защиты!')
    
    
    def get_element_decorator(self) -> str|None:
        return Protection._elements_dictionary.get(self.element(), None)
        
        
    def get_element_names(self, key:str=None) -> str|dict|None:
        names = {}
        element_decorator = self.get_element_decorator()
        if not element_decorator:
            return None
        for lexeme in self.lexemes:
            names[lexeme] = f'{self.lexemes[lexeme]} {element_decorator}'
        if key:
            return names.get(key, '')
        return names
           


#Класс Доспех (подкласс Защиты)
class Armor(Protection):
    def __init__(self, game):
        super().__init__(game)
  
    
    def on_create(self):
        self.decorate()
        return True

    
    def decorate(self) -> bool:
        decorators = Protection._armor_decorators.get(self.protection_type, [])
        decorator = randomitem(decorators)
        if not decorator:
            return False
        if not decorator.get(self.gender, False):
            return False
        lexemes = {}
        for lexeme in self.lexemes:
            decorate_string = decorator[self.gender].get(lexeme, False)
            if decorate_string:
                lexemes[lexeme] = f'{decorate_string} {self.lexemes[lexeme]}'
        self.protection.increase_modificator(decorator['protection_modifier'])
        self.lexemes = lexemes
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['защита', 'защиту', 'доспех', 'доспехи']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
            names_list.append(self.get_element_names(case).lower())
        return names_list
    
    
    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan)
        monster = room.monsters('random')
        if monster:
            if monster.wear_armor:
                monster.take(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.loot.add(self)

# Доспех можно надеть. Если на персонаже уже есть доспех, персонаж выбрасывает его и он становится частью лута комнаты.
    def take(self, who):
        old_armor = who.armor
        message = [f'{who.name} использует {self:accus} как защиту.']
        if not old_armor.empty:
            message.append(f'При этом он снимает {old_armor:accus} и оставляет валяться на полу.')
            who.drop(old_armor.name)
        who.armor = self
        self.user = who
        tprint(self.game, message)


#Класс Щит (подкласс Защиты)
class Shield (Protection):
    
    _crushed_upper_limit = 10
    """Верхняя планка случайных значений при проверке того, что щит сломан."""
    
    _damage_when_hiding_min = 50
    """Нижняя планка случайных значений при генерации ущерба щиту когда персонаж спрятался."""
    
    _damage_when_hiding_max = 75
    """Верхняя планка случайных значений при генерации ущерба щиту когда персонаж спрятался."""
    
    _damage_min = 10
    """Нижняя планка случайных значений при генерации ущерба щиту в обычных условиях."""
    
    _damage_max = 25
    """Верхняя планка случайных значений при генерации ущерба щиту в обычных условиях."""
    
    _repair_multiplier = 10 
    """Множитель, на который умножается накопленный урон щита чтобы определить стоимость его починки."""
    
    _states_dictionary = {
                                1: 
                                    {
                                    "nom": "Поцарапанный",
                                    "accus": "Поцарапанного",
                                    "gen": "Поцарапанного",
                                    "dat": "Поцарапанному",
                                    "prep": "Поцарапанном",
                                    "inst": "Поцарапанным",
                                    },
                                2: 
                                    {
                                    "nom": "Потрепанный",
                                    "accus": "Потрепанного",
                                    "gen": "Потрепанного",
                                    "dat": "Потрепанному",
                                    "prep": "Потрепанном",
                                    "inst": "Потрепанным",
                                    },
                                3: 
                                    {
                                    "nom": "Почти сломанный",
                                    "accus": "Почти сломанного",
                                    "gen": "Почти сломанного",
                                    "dat": "Почти сломанному",
                                    "prep": "Почти сломанном",
                                    "inst": "Почти сломанным",
                                    },
                                4: 
                                    {
                                    "nom": "Еле живой",
                                    "accus": "Еле живого",
                                    "gen": "Еле живого",
                                    "dat": "Еле живому",
                                    "prep": "Еле живом",
                                    "inst": "Еле живым",
                                    }
                                }
    """Словарь состояний щита."""

    
    def __init__(self, game):
        super().__init__(game)
        self.accumulated_damage = 0
    
    
    def on_create(self):
        return True
 
    
    def get_damaged_names(self, key:str=None) -> str|dict:
        names = {}
        damage_decorator = self.get_damage_decorator()
        if not damage_decorator:
            return None
        for lexeme in self.lexemes:
            names[lexeme] = f'{damage_decorator[lexeme]} {self.lexemes[lexeme].lower()}'
        if key:
            return names.get(key, '')
        return names
    
    
    def get_full_names(self, key:str=None) -> str|dict:
        names = {}
        damage_decorator = self.get_damage_decorator()
        element_decorator = self.get_element_decorator()
        for lexeme in self.lexemes:
            name = self.lexemes[lexeme]
            if damage_decorator:
                name = f'{damage_decorator[lexeme]} {name.lower()}'
            if element_decorator:
                name = f'{name} {element_decorator}'
            names[lexeme] = name
        if key:
            return names.get(key, '')
        return names
          
    
    def get_damage_decorator(self) -> list|None:
        return Shield._states_dictionary.get(self.accumulated_damage // 1, None)
    
    
    def check_if_broken(self, attack:int=0) -> bool:
        damage_limit = dice(1, Shield._crushed_upper_limit)
        damage_to_shield = attack * self.accumulated_damage
        if damage_limit < damage_to_shield:
            self.game.all_shields.remove(self)
            self.user.shield = self.game.no_shield
            return True
        return False
    
    
    def take_damage(self, is_hiding:bool=False) -> None:
        if is_hiding:
            dice_result = dice(Shield._damage_when_hiding_min, Shield._damage_when_hiding_max) / 100
        else:
            dice_result = dice(Shield._damage_min, Shield._damage_max) / 100
        self.accumulated_damage += dice_result
    
    
    def get_repair_price(self):
        return self.accumulated_damage * Shield._repair_multiplier // 1
    
    
    def repair(self) -> bool:
        self.accumulated_damage = 0
        return True
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['щит']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
            names_list.append(self.get_element_names(case).lower())
            names_list.append(self.get_damaged_names(case).lower())
            names_list.append(self.get_full_names(case).lower())
        return names_list

    
    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan)
        monster = room.monsters('random')
        if monster:
            if monster.carry_shield:
                monster.take(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.loot.add(self)

# Щит можно взять в руку. Если в руке ужесть щит, персонаж выбрасывает его и он становится частью лута комнаты.
    def take(self, who):
        old_shield = None
        if not who.shield.empty:
            old_shield = who.shield
        if not who.removed_shield.empty:
            old_shield = who.removed_shield
        if not who.weapon.empty and who.weapon.twohanded:
            who.removed_shield = self
            message = [f'{who.name} помещает {self.get_full_names("accus")} за спину.']
        else:
            who.shield = self
            message = [f'{who.name} берет {self.get_full_names("accus")} в руку.']
        if old_shield:
            message.append(f'При этом он бросает {old_shield.get_full_names("accus")} и оставляет валяться на полу.')
            who.drop(old_shield.name)
        self.user = who
        tprint(self.game, message)
