from math import floor, sqrt
from random import randint as dice
from typing import Any, NoReturn

from class_basic import *
from functions import howmany, randomitem, tprint
from settings import *


class Rune:
    
    """ Класс Руна. """
    
    def __init__(self, game):
        self.game = game
        self.damage = 4 - floor(sqrt(dice(1, 15)))
        self.defence = 3 - floor(sqrt(dice(1, 8)))
        self.elements = [1, 3, 7, 12]
        self.element = self.elements[dice(0, 3)]
        self.can_use_in_fight = False
        self.name = 'руна'
        self.name1 = 'руну'
        self.description = f'{self.name} {s_elements_dictionary[self.element]}'
        self.empty = False
        self.check_if_poisoned()
        
        
    def __str__(self) -> str:
        return f'{self.name} {s_elements_dictionary[self.element]} - ' \
            f'урон + {str(self.damage)} или защита + {str(self.defence)}'

    
    def check_if_poisoned(self) -> NoReturn:    
        
        """ Метод определяет, ядовитая руна, или нет. """
        
        if dice(1, s_rune_poison_probability) == 1:
            self.poison = True
            self.description = f'ядовитая {self.description}'
        else:
            self.poison = False


    def on_create(self) -> Any:
        
        """ Метод вызывается после создания экземпляра класса. Ничего не делает. """
        
        return True

    def place(self, castle, room=None) -> bool:
        
        """ Метод раскидывания рун по замку. """
        
        rooms_with_secrets = castle.secret_rooms()
        if not room:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if room in rooms_with_secrets:
            room.secret_loot.add(self)
        elif bool(room.furniture):
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    def element(self) -> int:
        
        """ Метод возвращает элемент руны в виде целого числа. """
        
        return int(self.element)

    
    def take(self, who) -> NoReturn:
        
        """ Метод вызывается когда кто-то забирает руну себе. """
        
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')

    def show(self) -> str:
        
        """ Метод возвращает описание руны в виде строки. """
        
        return f'{self.description} - урон + {str(self.damage)} или защита + {str(self.defence)}'.capitalize()

    def use(self, who_is_using, in_action:bool=False) -> str:
        
        """ 
        Метод использования руны. Возвращает строку ответа и ничего не делает 
        так как руну использовать нельзя.
        
        """
        
        tprint(
            self.game, f'{who_is_using.name} не знает, как использовать такие штуки.')


class Spell:
    def __init__(self, game, name='Обычное заклинание', name1='Обычного заклинания', element='магия', min_damage=1,
                 max_damage=5, min_damage_mult=1, max_damage_mult=1, actions='кастует'):
        self.game = game
        self.name = name
        self.name1 = name1
        self.description = self.name
        self.element = element
        self.min_damage_mult = min_damage_mult
        self.max_damage_mult = max_damage_mult
        self.actions = actions
        self.max_damage = max_damage
        self.min_damage = min_damage
        self.empty = False

    def __str__(self):
        return self.name

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')


class Matches:
    
    """ Класс Спички. """
    
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'спички'
        self.name1 = 'спички'
        self.description = 'Спички, которыми можно что-то поджечь'
        self.room = None
        self.empty = False

    def show(self) -> str:
        
        """ Метод возвращает описание спичек в виде строки. """
        
        return self.description

    def place(self, castle, room=None) -> bool:
        
        """ Метод раскидывания спичек по замку. """
        
        if not room:
            rooms = [i for i in castle.plan if not i.locked and i.light]
            room = randomitem(rooms, False)
        if bool(room.furniture):
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        self.room = room
        return True

    def take(self, who=None) -> bool:
        
        """ Метод вызывается когда кто-то забирает спички себе. """
        
        if not who:
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')
        return True

    def use(self, who_is_using=None, in_action=False) -> NoReturn:
        
        """ Метод использования спичек. """
        
        floor = who_is_using.floor
        room = floor.plan[who_is_using.current_position]
        if not who_is_using:
            who_is_using = self.game.player
        if room.light:
            tprint(self.game, 'Незачем тратить спички, здесь и так светло.')
        else:
            room.turn_on_light(who_is_using)
  
class Map:
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'карта'
        self.name1 = 'карту'
        self.empty = False
        self.description = 'Карта, показывающая расположение комнат замка'

    def place(self, castle, room=None) -> bool:
        
        """ Метод размещения карты в замке. """
        
        if not room:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if bool(room.furniture):
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    def show(self) -> str:
        
        """ Метод возвращает описание карты в виде строки. """
        
        return self.description

    def use(self, who, in_action: bool = False) -> bool:
        """
        Метод использования карты. Если вызывается в бою, то ничего не происходит. 
        В мирное время выводит на экран карту замка.

        Параметры:
        - who_is_using - герой, который использует карту
        - in_action - признак того, что предмет используется в бою. По умолчанию False.

        """
        game = self.game
        floor = who.floor
        room = floor.plan[who.current_position]
        if not in_action:
            if who.fear >= s_fear_limit:
                tprint(
                    game, 
                    f'{who.name} от страха не может сосредоточиться и что-то разобрать на карте.', 'direction')
                return False
            elif not room.light:
                tprint(
                    game, 
                    f'В комнате слишком темно чтобы разглядывать карту', 'direction')
                return False
            else:
                tprint(
                    game, 
                    f'{who.name} смотрит на карту этажа замка.', 'direction')
                floor.map()
                return True
        else:
            tprint(game, 'Во время боя это совершенно неуместно!')
            return False

    def take(self, who) -> NoReturn:
        
        """ Метод вызывается когда кто-то забирает карту себе. """
        
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')


class Key:
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'ключ'
        self.name1 = 'ключ'
        self.description = 'Ключ, пригодный для дверей и сундуков'
        self.empty = False

    def __str__(self) -> str:
        return self.description

    def show(self):
        return self.description

    def on_create(self):
        return True

    def place(self, floor, room=None) -> bool:
        if not room:
            room = floor.get_random_unlocked_room()
        furniture = room.get_random_unlocked_furniture()
        if furniture:
            furniture.put(self)
        else:
            room.loot.add(self)
        return True


    def take(self, who):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')
        return True


class Potion:
    def __init__(self, game, name='', effect=0, type=0, can_use_in_fight=True):
        self.game = game
        self.name = name
        self.empty = False
        if self.name != 0:
            self.name = name
            self.name1 = self.name
            self.effect = int(effect)
            self.type = int(type)
            self.can_use_in_fight = can_use_in_fight
            self.description = s_potion_types[self.type][4]
        elif self.name == 0:
            n = dice(0, 5)
            self.name = s_potion_types[n][0]
            self.name1 = self.name
            self.effect = s_potion_types[n][1]
            self.type = s_potion_types[n][2]
            self.can_use_in_fight = s_potion_types[n][3]
            self.description = s_potion_types[n][4]

    def __str__(self):
        return self.description

    def on_create(self):
        return True

    def show(self):
        return self.description

    def place(self, castle, room=None):
        if not room:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if bool(room.furniture):
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    def check_if_can_be_used(self, who_using, in_action: bool) -> bool:
        game = self.game
        if self.type == 8 and not who_using.poisoned and who_using.fear == 0:
            tprint(
                game, f'{who_using.name} не чувствует никакого недомогания и решает приберечь зелье на попозже.')
            return False
        if not in_action and self.type in [0, 3, 5, 7]:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        if in_action and self.type in [1, 2, 4, 6]:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True

    def use_type_0(self, who_using) -> bool:
        if (who_using.start_health - who_using.health) < self.effect:
            heal = dice(1, (who_using.start_health - who_using.health))
        else:
            heal = dice(1, self.effect)
        who_using.health += heal
        text = f'{who_using.name} восполняет {howmany(heal, "единицу жизни,единицы жизни,единиц жизни")}'
        if who_using.poisoned:
            who_using.poisoned = False
            text += ' и излечивается от отравления'
        tprint(self.game, text)
        return True

    def use_type_1(self, who_using) -> bool:
        who_using.start_health += self.effect
        who_using.health += self.effect
        tprint(
            self.game, f'{who_using.name} увеличивает свое максимальное здоровье на {str(self.effect)} до {str(who_using.health)}.')
        return True

    def use_type_2(self, who_using) -> bool:
        who_using.stren += self.effect
        who_using.start_stren += self.effect
        tprint(
            self.game, f'{who_using.name} увеличивает свою силу на {str(self.effect)} до {str(who_using.stren)}.')
        return True

    def use_type_3(self, who_using) -> bool:
        who_using.stren += self.effect
        tprint(self.game, f'На время боя {who_using.name} увеличивает \
            свою силу на {str(self.effect)} до {str(who_using.stren)}.')
        return True

    def use_type_4(self, who_using) -> bool:
        who_using.dext += self.effect
        who_using.start_dext += self.effect
        tprint(
            self.game, f'{who_using.name} увеличивает свою ловкость на {str(self.effect)} до {str(who_using.dext)}.')
        return True

    def use_type_5(self, who_using) -> bool:
        who_using.dext += self.effect
        tprint(
            self.game, f'На время боя {who_using.name} увеличивает свою ловкость на {str(self.effect)} до {str(who_using.dext)}.')
        return True

    def use_type_6(self, who_using) -> bool:
        who_using.intel += self.effect
        who_using.start_intel += self.effect
        tprint(self.game, f'{who_using.name} увеличивает свой \
            интеллект на {str(self.effect)} до {str(who_using.intel)}.')
        return True

    def use_type_7(self, who_using) -> bool:
        who_using.intel += self.effect
        tprint(
            self.game, f'На время боя {who_using.name} увеличивает свой интеллект на {str(self.effect)} до {str(who_using.intel)}.')
        return True

    def use_type_8(self, who_using) -> bool:
        who_using.poisoned = False
        who_using.fear = 0
        tprint(
            self.game, f'{who_using.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.')
        return True

    def use(self, who_using, in_action:bool=False):
        game = self.game
        functions_list = {
            0: self.use_type_0,
            1: self.use_type_1,
            2: self.use_type_2,
            3: self.use_type_3,
            4: self.use_type_4,
            5: self.use_type_5,
            6: self.use_type_6,
            7: self.use_type_7,
            8: self.use_type_8
        }
        if not self.check_if_can_be_used(who_using=who_using, in_action=in_action):
            return False
        result = functions_list[self.type](who_using=who_using)
        if result:
            who_using.pockets.remove(self)
        return result

    def take(self, who):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')
        return True


class Book:
    def __init__(self, game, name=None):
        self.game = game
        self.name = name
        self.empty = False

    def __str__(self):
        return self.name

    def on_create(self):
        self.type = dice(0, 2)
        description = randomitem(self.descriptions, False)
        self.name = description[0] + ' ' + \
            self.name + ' ' + self.decorations[self.type]
        self.name1 = description[1] + ' ' + \
            self.name1 + ' ' + self.decorations[self.type]
        self.description = self.name
        available_texts = []
        for i in self.texts:
            if i[0] == self.type:
                available_texts.append(i[1])
        self.text = randomitem(available_texts, False)
        self.weapon_type = self.weapon_types[self.type]
        self.armor_type = self.armor_types[self.type]
        self.shield_type = self.shield_types[self.type]
        return True

    def get_mastery_string(self, who):
        return f'{who.name} теперь немного лучше знает, как использовать {self.weapon_type} оружие.'

    
    def place(self, floor, room=None):
        if not room:
            room = floor.get_random_room_with_furniture()
        furniture = randomitem(room.furniture, False)
        furniture.put(self)
        return True

    def show(self):
        return self.description

    def use(self, who_using, in_action:bool=False):
        if in_action:
            tprint(self.game, 'Сейчас абсолютно не подходящее время для чтения.')
            return False
        else:
            return who_using.read(self)

    def take(self, who):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')
        return True
