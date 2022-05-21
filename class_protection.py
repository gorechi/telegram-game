from math import ceil
from random import randint as dice

from functions import randomitem, tprint
from settings import *


class Protection:
    def __init__(self, game, name='', name1='защиту', protection=1, actions='', empty=False):
        self.game = game
        self.name = name
        self.name1 = name1
        self.actions = actions.split(',')
        self.can_use_in_fight = True
        self.empty = empty
        self.runes = []
        self.protection = int(protection)

    def __str__(self):
        protection_string = str(self.protection)
        if self.perm_protection() != 0:
            protection_string += '+' + str(self.perm_protection())
        return self.name + self.enchantment() + ' (' + protection_string + ')'
    
    def on_create(self):
        return True

    
    def check_name(self, message:str) -> bool:
        names_list = self.real_name(all=True) + ['щит']
        names_list_lower = []
        for name in names_list:
            names_list_lower.append(name.lower())
        if message.lower() in names_list_lower:
            return True
        return False
    
    
    def real_name(self, all:bool=False, additional:list=[]) -> list[str]:
        names = []
        if self.empty:
            return []
        if self.element() != 0:
            names.append(self.name + ' ' + s_elements_dictionary[self.element()])
            names.append(self.name1 + ' ' + s_elements_dictionary[self.element()])
        if self.element() == 0 or all:
            names.append(self.name)
            names.append(self.name1)
        names += additional
        return names

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

    def perm_protection(self):
        protection = 0
        if len(self.runes) in [1, 2]:
            for rune in self.runes:
                protection += rune.defence
        return protection

    def enchant(self, rune):
        if len(self.runes) > 1 or self.empty:
            return False
        else:
            self.runes.append(rune)
            return True

    def enchantment(self):
        if len(self.runes) not in [1, 2]:
            return ''
        else:
            element = 0
            for i in self.runes:
                element += int(i.element)
            return ' ' + s_elements_dictionary[element]

    def protect(self, who):
        multiplier = 1
        if not who.weapon.empty and who.weapon.element() != 0 and self.element() != 0:
            if who.weapon.element() in s_weakness_dictionary[self.element()]:
                multiplier = s_protection_strong_weapon_multiplier
            elif self.element() in s_weakness_dictionary[who.weapon.element()]:
                multiplier = s_protection_weak_weapon_multiplier
        if who.hide:
            who.hide = False
            return self.protection + self.perm_protection()
        else:
            if self.protection > 0:
                return ceil((dice(1, self.protection) + self.perm_protection())*multiplier)
            else:
                return 0

    def take(self, who):
        if who.shield == '':
            who.shield = self
            tprint(self.game, f'{who.name} использует {self.name1} как защиту.')
        else:
            self.game.player.pockets.append(self)
            tprint(self.game, f'{who.name} забирает {self.name1} себе.')

    
    def show(self) -> str:
        real_name = self.real_name()[0]
        if self.empty:
            return ''
        protection_string = str(self.protection)
        if self.perm_protection() != 0:
            protection_string += '+' + str(self.perm_protection())
        return f'{real_name} ({protection_string})'

    
    def use(self, who_using, in_action=False):
        if who_using.shield == '':
            who_using.shield = self
        else:
            who_using.pockets.append(who_using.shield)
            who_using.shield = self
            who_using.pockets.remove(self)
        tprint(self.game, f'{who_using.name} теперь использует {self.name1} в качестве защиты!')

#Класс Доспех (подкласс Защиты)
class Armor(Protection):
    def __init__(self, game, name='', name1='доспех', protection=1, actions='', empty=False):
        self.game = game
        if name != 0:
            self.name = name
            self.name1 = name1
            self.protection = int(protection)
        else:
            n1 = [['Большой', 'Большая', 'Большой', 'Большую'],
                  ['Малый', 'Малая', 'Малый', 'Малую'],
                  ['Старый', 'Старая', 'Старый', 'Старую'],
                  ['Тяжелый', 'Тяжелая', 'Тяжелый', 'Тяжелую'],
                  ['Новый', 'Новая', 'Новый', 'Новую']]
            n2 = [['броня', 1, 'броню'],
                  ['кольчуга', 1, 'кольчугу'],
                  ['защита', 1, 'защиту'],
                  ['панцирь', 0, 'панцирь']]
            a1 = dice(0, len(n1) - 1)
            a2 = dice(0, len(n2) - 1)
            self.name = n1[a1][n2[a2][1]] + ' ' + n2[a2][0]
            self.name1 = n1[a1][n2[a2][1]+2] + ' ' + n2[a2][2]
            self.protection = dice(1, 3)
        self.actions = actions.split(',')
        self.can_use_in_fight = True
        self.empty = empty
        self.runes = []

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan, False)
        monster = room.monsters('random')
        if monster:
            if monster.wear_armor:
                monster.take(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.loot.add(self)

# Доспех можно надеть. Если на персонаже уже есть доспех, персонаж выбрасывает его и он становится частью лута комнаты.
    def take(self, who):
        old_armor = who.armor
        message = [f'{who.name} использует {self.name1} как защиту.']
        if not old_armor.empty:
            message.append(f'При этом он снимает {old_armor.name1} и оставляет валяться на полу.')
            who.drop(old_armor.name)
        who.armor = self
        tprint(self.game, message)


#Класс Щит (подкласс Защиты)
class Shield (Protection):
    def __init__(self, game, name='', name1='щит', protection=1, actions='', empty=False):
        self.game = game
        if name != 0:
            self.name = name
            self.name1 = name1
            self.protection = int(protection)
        else:
            n1 = ['Большой',
                  'Малый',
                  'Старый',
                  'Тяжелый',
                  'Новый']
            a1 = dice(0, len(n1) - 1)
            self.name = n1[a1] + ' щит'
            self.name1 = self.name
            self.protection = dice(1, 3)
        self.actions = actions.split(',')
        self.can_use_in_fight = True
        self.empty = empty
        self.runes = []
        self.accumulated_damage = 0
    
    
    def on_create(self):
        return True

        
    def real_name(self, all:bool=False, additional:list=[]) -> list[str]:
        if self.empty:
            return []
        damage_dict = s_shield_states_dictionary
        damage = damage_dict.get(self.accumulated_damage // 1)
        names = []
        if damage:
            name = damage + ' ' + self.name
            name1 = damage + ' ' + self.name1
        else:
            name = self.name
            name1 = self.name1
        if self.element() != 0:
            names.append(name + ' ' + s_elements_dictionary[self.element()])
            names.append(name1 + ' ' + s_elements_dictionary[self.element()])
        if self.element() == 0 or all:
            names.append(name)
            names.append(name1)
        if all:
            names.append(self.name)
            names.append(self.name1)
        names += additional
        return names

    
    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan, False)
        monster = room.monsters('random')
        if monster:
            if monster.carry_shield:
                monster.take(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
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
            message = [f'{who.name} помещает {self.name1} за спину.']
        else:
            who.shield = self
            message = [f'{who.name} берет {self.name1} в руку.']
        if old_shield:
            message.append(f'При этом он бросает {old_shield.real_name()[1]} и оставляет валяться на полу.')
            who.drop(old_shield.name)
        tprint(self.game, message)
