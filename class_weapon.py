from math import ceil
from random import randint as dice

from functions import randomitem, tprint
from settings import *


class Weapon:
    def __init__(self, 
                 game, 
                 name=None, 
                 name1='оружие', 
                 damage=1, 
                 actions='бьет,ударяет', 
                 empty=False, 
                 weapon_type=None, 
                 enchantable=True):
        self.game = game
        if name:
            self.name = name
            self.damage = int(damage)
            self.name1 = name1
            self.twohanded = False
            self.type = ''
            self.hit_chance = 0
            self.enchatable = enchantable
            self.weapon_type = weapon_type
            self.generate_type()
            self.generate_name()
        self.actions = actions.split(',')
        self.can_use_in_fight = True
        self.runes = []
        self.twohanded_dict = s_weapon_twohanded_dictionary
        self.empty = empty

    
    def on_create(self):
        return True

    
    def __str__(self):
        damage_string = str(self.damage)
        if self.perm_damage() != 0:
            damage_string += '+' + str(self.perm_damage())
        return f'{self.name}{self.enchantment()} ({damage_string})'

    
    def generate_name(self):
        first_word_lexemes = randomitem(s_weapon_first_words_dictionary)[self.gender]
        self.lexemes = {}
        for lexeme in first_word_lexemes:
            self.lexemes[lexeme] = f'{first_word_lexemes[lexeme]} {self.weapon_type[0][lexeme]}'
        self.name = self.lexemes['nom']
        self.name1 = self.lexemes['accus']
        print(self.lexemes)
    
    
    def generate_type(self):
        settings_list = s_weapon_types_dictionary
        if self.weapon_type:
            settings_list = [i for i in settings_list if i[3] == self.weapon_type]
        self.settings = randomitem(settings_list)
        self.type = self.weapon_type[3]
        self.twohanded = self.weapon_type[4]
        self.gender = self.weapon_type[1]
        self.hit_chance = self.weapon_type[5]
    
    
    def real_name(self, all:bool=False, additional:list=[]) -> list:
        names = []
        if self.element() != 0:
            names.append(f'{self.name} {s_elements_dictionary[self.element()]}'.capitalize())
            names.append(f'{self.name1} {s_elements_dictionary[self.element()]}'.capitalize())
        if self.element() == 0 or all == 'all':
            names.append(self.name.capitalize())
            names.append(self.name1.capitalize())
        names += additional
        return names
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.real_name(all=True) + ['оружие']
        names_list_lower = []
        for name in names_list:
            names_list_lower.append(name.lower())
        if message.lower() in names_list_lower:
            return True
        return False

    
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
        message = [f'{who.name} берет {self.name1}.']
        second_weapon = who.get_second_weapon()
        if who.weapon.empty:
            who.weapon = self
            message.append(f'{who.name} теперь использует {self.name1} в качестве оружия.')
            if who.weapon.twohanded and not who.shield.empty:
                shield = who.shield
                who.shield = self.game.no_shield
                who.removed_shield = shield
                message.append(f'Из-за того, что {who.g(["герой взял", "героиня взяла"])} двуручное оружие, '
                               f'{who.g(["ему", "ей"])} пришлось убрать {shield.real_name()[1]} за спину.')
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
            message = [f'{who.name} теперь использует {self.name1} в качестве оружия.']
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
                               f'{who.g(["герой", "героиня"])} теперь держит во второй руке {shield.real_name()[1]}.')
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
