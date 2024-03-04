from math import ceil
from random import randint as dice

from functions import randomitem, tprint
from settings import *


class Protection:
    def __init__(self, game, name='', protection=1, actions='', empty=False, enchantable=True):
        self.game = game
        self.name = name
        self.actions = actions.split(',')
        self.can_use_in_fight = True
        self.empty = empty
        self.runes = []
        self.protection = int(protection)
        self.user = None

    def __str__(self):
        protection_string = str(self.protection)
        if self.perm_protection() != 0:
            protection_string += '+' + str(self.perm_protection())
        return self.name + self.enchantment() + ' (' + protection_string + ')'
    
    def on_create(self):
        return True

    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', 'accus'])
        if message.lower() in names_list:
            return True
        return False
    
    
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
            tprint(self.game, f'{who.name} использует {self.lexemes['accus']} как защиту.')
        else:
            self.game.player.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self.lexemes['accus']} себе.')

    
    def show(self) -> str:
        if self.empty:
            return None
        full_name = self.get_full_names('nom')
        protection_string = str(self.protection)
        if self.perm_protection() != 0:
            protection_string += '+' + str(self.perm_protection())
        return f'{full_name} ({protection_string})'

    
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
        tprint(self.game, f'{who_using.name} теперь использует {self.lexemes['accus']} в качестве защиты!')
    
    
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
           


#Класс Доспех (подкласс Защиты)
class Armor(Protection):
    def __init__(self, 
                 game, 
                 name:str='защита', 
                 protection:int=1, 
                 actions:list=['отражает'], 
                 empty:bool=False, 
                 enchantable:bool=True):
        self.game = game
        self.name = name
        self.protection = protection
        self.enchantable = enchantable
        self.actions = actions
        self.can_use_in_fight = True
        self.empty = empty
        self.runes = []
        self.user = None
  
    
    def on_create(self):
        self.decorate()
        return True

    
    def decorate(self):
        decorators = s_armor_decorators[self.type]
        decorator = randomitem(decorators)
        lexemes = {}
        for lexeme in self.lexemes:
            lexemes[lexeme] = f'{decorator[self.gender][lexeme]} {self.lexemes[lexeme]}'
        self.protection += decorator['protection_modifier']
        if self.protection < 2:
            self.protection = 1
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
        message = [f'{who.name} использует {self.lexemes['accus']} как защиту.']
        if not old_armor.empty:
            message.append(f'При этом он снимает {old_armor.lexemes['accus']} и оставляет валяться на полу.')
            who.drop(old_armor.name)
        who.armor = self
        self.user = who
        tprint(self.game, message)


#Класс Щит (подкласс Защиты)
class Shield (Protection):
    def __init__(self, 
                 game, 
                 name:str='', 
                 protection:int=1, 
                 actions:list=[], 
                 empty:bool=False, 
                 enchantable:bool=True):
        self.game = game
        self.name = name
        self.protection = protection
        self.enchantable = enchantable
        self.actions = actions
        self.can_use_in_fight = True
        self.empty = empty
        self.runes = []
        self.accumulated_damage = 0
        self.user = None
    
    
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
        return s_shield_states_dictionary.get(self.accumulated_damage // 1, None)
    
    
    def check_if_broken(self, attack:int=0) -> bool:
        damage_limit = dice(1, s_shield_crushed_upper_limit)
        damage_to_shield = attack * self.accumulated_damage
        if damage_limit < damage_to_shield:
            self.game.all_shields.remove(self)
            self.user.shield = self.game.no_shield
            return True
        return False
    
    
    def take_damage(self, is_hiding:bool=False) -> None:
        if is_hiding:
            dice_result = dice(s_shield_damage_when_hiding_min, s_shield_damage_when_hiding_max) / 100
        else:
            dice_result = dice(s_shield_damage_min, s_shield_damage_max) / 100
        self.accumulated_damage += dice_result
    
    
    def get_repair_price(self):
        return self.accumulated_damage * s_shield_repair_multiplier // 1
    
    
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
            message = [f'{who.name} помещает {self.get_full_names('accus')} за спину.']
        else:
            who.shield = self
            message = [f'{who.name} берет {self.get_full_names('accus')} в руку.']
        if old_shield:
            message.append(f'При этом он бросает {old_shield.get_full_names('accus')} и оставляет валяться на полу.')
            who.drop(old_shield.name)
        self.user = who
        tprint(self.game, message)
