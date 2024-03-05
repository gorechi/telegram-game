from math import ceil
from random import randint as dice

from functions import randomitem, tprint
from settings import *


class Weapon:
    def __init__(self, 
                 game, 
                 name=None, 
                 damage:int=1, 
                 actions=['бьет', 'ударяет'], 
                 empty=False, 
                 type=None, 
                 enchantable=True,
                 gender=0):
        self.game = game
        self.name = name
        self.damage = damage
        self.empty = empty
        self.actions = actions
        self.enchatable = enchantable
        self.type = type
        self.hit_chance = 0
        self.runes = []
        self.gender = gender

    
    def on_create(self) -> bool:
        self.decorate()
        return True

    
    def decorate(self) -> bool:
        decorators = s_weapon_decorators.get(self.type, [])
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
        self.damage += decorator['damage_modifier']
        self.lexemes = lexemes
        return True
    
    
    def __str__(self) -> str:
        damage_string = str(self.damage)
        if self.perm_damage() != 0:
            damage_string += '+' + str(self.perm_damage())
        return f'{self.name}{self.enchantment()} ({damage_string})'
    
    
    def get_full_names(self, key:str=None) -> str|list:
        if self.element != 0:
            return self.get_element_names(key)
        if key:
            return self.lexemes.get(key, '')
        return self.lexemes
    
    
    def get_element_decorator(self) -> str|None:
        return s_elements_dictionary.get(self.element(), None)
        
        
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
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', 'accus'])
        if message.lower() in names_list:
            return True
        return False

    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['оружие']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
            names_list.append(self.get_element_names(case).lower())
        return names_list
    
    
    def element(self):
        element_sum = 0
        for rune in self.runes:
            element_sum += rune.element
        return element_sum

    
    def is_poisoned(self):
        for i in self.runes:
            if i.poison:
                return True
        return False
    
    
    def can_be_enchanted(self) -> bool:
        if len(self.runes) > 1 or self.empty or not self.enchatable:
            return False
        return True
    
    
    def enchant(self, rune):
        if self.can_be_enchanted():
            self.runes.append(rune)
            return True
        return False
    

    def enchantment(self):
        """Функция генерирует название элемента оружия. 
        Элемент складывается из сочетания рун, прикрепленных к оружию.

        Returns:
            string: Строка элемента для добавления к названию оружия.\n
            Пример: " огня" для формирования названия "Большой топор огня".
        """
        if len(self.runes) not in [1, 2]:
            return ''
        else:
            element = 0
            for i in self.runes:
                element += int(i.element)
            return ' ' + s_elements_dictionary[element]

    
    def perm_damage(self):
        damage = 0
        if len(self.runes) in [1, 2]:
            for rune in self.runes:
                damage += rune.damage
        return damage

    
    def attack(self, who=None):
        """Функция рассчитывает урон, который наносит оружие конкретному монстру

        Args:
            who (object Monster, optional): Монстр, которого атакуют оружием. Defaults to None.

        Returns:
            integer: Значение нанесенного урона
        """
        damage = dice(1, int(self.damage))
        big_damage = damage + self.perm_damage()
        if who:
            damage_multiplier = who.get_weakness(self)
        else:
            damage_multiplier = 1
        full_damage = ceil(big_damage * damage_multiplier)
        return full_damage

    
    def take(self, who):
        game = self.game
        message = [f'{who.name} берет {self.lexemes['accus']}.']
        second_weapon = who.get_second_weapon()
        if who.weapon.empty:
            who.weapon = self
            message.append(f'{who.name} теперь использует {self.lexemes['accus']} в качестве оружия.')
            if who.weapon.twohanded and not who.shield.empty:
                shield = who.shield
                who.shield = self.game.no_shield
                who.removed_shield = shield
                message.append(f'Из-за того, что {who.g(["герой взял", "героиня взяла"])} двуручное оружие, '
                               f'{who.g(["ему", "ей"])} пришлось убрать {shield.get_full_name('accus')} за спину.')
        else:
            if not second_weapon.empty:
                message.append(f'В рюкзаке для нового оружия нет места, поэтому приходится бросить {who.weapon.name}.')
                who.drop(who.weapon.name)
                who.weapon = self
            else:
                message.append('В рюкзаке находится место для второго оружия. Во время схватки можно "Сменить" оружие.')
                who.backpack.append(self)
        tprint(game, message)

    
    def show(self):
        damage_string = str(self.damage)
        if self.perm_damage() != 0:
            damage_string += '+' + str(self.perm_damage())
        if self.twohanded:
            name = self.twohanded_dict[self.gender] + ' ' + self.name + self.enchantment()
        else:
            name = self.name + self.enchantment()
        return f'{name} ({damage_string}), {self.type}'.capitalize()

    
    def use(self, who, in_action=False):
        game = self.game
        if who.weapon.empty:
            who.weapon = self
        else:
            who.backpack.append(who.weapon)
            who.weapon = self
            who.backpack.remove(self, who)
            message = [f'{who.name} теперь использует {self.lexemes['accus']} в качестве оружия.']
            if not who.shield.empty and self.twohanded:
                shield = who.shield
                who.removed_shield = shield
                who.shield = game.no_shield
                message.append('Из-за того, что новое оружие двуручное, щит пришлось убрать за спину.')
            if not who.removed_shield.empty and not self.twohanded:
                shield = who.removed_shield
                who.shield = shield
                who.removed_shield = game.no_shield
                message.append(f'Из-за того, что новое оружие одноручное, '
                               f'{who.g(["герой", "героиня"])} теперь держит во второй руке {shield.get_full_name("occus")}.')
        tprint(game, message)

    
    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan, False)
        monster = room.monsters('random')
        if monster:
            if monster.carry_weapon:
                monster.take(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.loot.add(self)
