from math import floor, sqrt
from random import randint as dice

from class_basic import *
from functions import howmany, randomitem, tprint
from settings import *


class Rune:
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
        if dice (1, s_rune_poison_probability) == 1:
            self.poison = True
            self.description = f'ядовитая {self.description}'
        else:
            self.poison = False

    def __str__(self):
        return f'{self.name} {s_elements_dictionary[self.element]} - ' \
               f'урон + {str(self.damage)} или защита + {str(self.defence)}'

    def on_create(self):
        return True

    def place(self, castle, room=None):
        rooms_with_secrets = castle.secret_rooms()
        if not room:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if room in rooms_with_secrets:
            room.secret_loot.add(self)
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    def element(self):
        return int(self.element)

    def take(self, who):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')

    def show(self):
        return f'{self.description} - урон + {str(self.damage)} или защита + {str(self.defence)}'.capitalize()

    def use(self, who_is_using, inaction=False):
        tprint(self.game, f'{who_is_using.name} не знает, как использовать такие штуки.')


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
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'спички'
        self.name1 = 'спички'
        self.description = 'Спички, которыми можно что-то поджечь'
        self.room = None
        self.empty = False

    def show(self):
        return self.description

    def place(self, castle, room_to_place=None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = [i for i in castle.plan if not i.locked and i.light]
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        self.room = room
        return True

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')

    def use(self, who_is_using=None, in_action=False):
        player = self.game.player
        game = self.game
        if not who_is_using:
            who_is_using = player
        floor = who_is_using.floor
        room = floor.plan[who_is_using.current_position]
        monster = room.monster()
        if room.light:
            message = ['Незачем тратить спички, здесь и так светло.']
            tprint(game, message)
        else:
            room.light = True
            room.torch = True
            message = [f'{who_is_using.name} зажигает факел и комната озаряется светом']
            if monster:
                if monster.frightening:
                    message.append(f'{who_is_using.name} замирает от ужаса глядя на чудовище перед собой.')
                    who_is_using.fear += 1
            tprint(game, message)
            room.show(who_is_using)
            room.map()
            if monster:
                if monster.agressive:
                    player.fight(monster.name, True)

class Map:
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'карта'
        self.name1 = 'карту'
        self.empty = False
        self.description = 'Карта, показывающая расположение комнат замка'

    def place(self, castle, room=None):
        if not room:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.pile.append(self)
        return True

    def show(self):
        return self.description

    def use(self, who, in_action=False):
        """Функция использования карты. Если вызывается в бою, то ничего не происходит. 
        В мирное время выводит на экран карту замка.

        Args:
            who_is_using (oject Hero): Герой, который использует карту
            in_action (bool, optional): Признак того, что предмет используется в бою. По умолчанию False.

        """
        game = self.game
        floor = who.floor
        room = floor.plan[who.current_position]
        if not in_action:
            if who.fear >= s_fear_limit:
                tprint(game, f'{who.name} от страха не может сосредоточиться и что-то разобрать на карте.', 'direction')
                return False
            elif not room.light:
                tprint(game, f'В комнате слишком темно чтобы разглядывать карту', 'direction')
                return False
            else:    
                tprint(game, f'{who.name} смотрит на карту этажа замка.', 'direction')
                floor.map()
                return True
        else:
            tprint(game, 'Во время боя это совершенно неуместно!')
            return False

    def take(self, who):
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

    def __str__(self):
        return self.description

    def show(self):
        return self.description

    def on_create(self):
        return True

    def place(self, castle, room=None):
        furniture = None
        if not room:
            unlocked_rooms = [a for a in castle.plan if (not a.locked)]
            room = randomitem(unlocked_rooms, False)
        if len(room.furniture) > 0:
            for i in room.furniture:
                if not i.locked:
                    furniture = i
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

    def on_create(self):
        return True

    def show(self):
        return self.description

    def place(self, castle, room=None):
        if not room:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    def use(self, who_using, in_action=False):
        game = self.game
        if self.type == 8:
            if who_using.poisoned or who_using.fear > 0:
                who_using.poisoned = False
                who_using.fear = 0
                tprint(game, f'{who_using.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.')
                who_using.pockets.remove(self)
                return True
            else:
                tprint(game, f'{who_using.name} не чувствует никакого недомогания и решает приберечь зелье на попозже.')
                return False
        if not in_action:
            if not self.type in [1, 2, 4, 6]:
                tprint(game, 'Это зелье можно использовать только в бою!')
                return False
            if self.type == 1:
                who_using.start_health += self.effect
                who_using.health += self.effect
                tprint(game, f'{who_using.name} увеличивает свое максимальное здоровье '
                             f'на {str(self.effect)} до {str(who_using.health)}.')
            elif self.type == 2:
                who_using.stren += self.effect
                who_using.start_stren += self.effect
                tprint(game, f'{who_using.name} увеличивает свою силу на {str(self.effect)} до {str(who_using.stren)}.')
            elif self.type == 4:
                who_using.dext += self.effect
                who_using.start_dext += self.effect
                tprint(game, f'{who_using.name} увеличивает свою ловкость '
                             f'на {str(self.effect)} до {str(who_using.dext)}.')
            elif self.type == 6:
                who_using.intel += self.effect
                who_using.start_intel += self.effect
                tprint(game, f'{who_using.name} увеличивает свой интеллект '
                             f'на {str(self.effect)} до {str(who_using.intel)}.')
        else:
            if not self.type in [0, 3, 5, 7]:
                tprint(game, 'Это зелье нельзя использовать в бою!')
                return False
            if self.type == 0:
                if (who_using.start_health - who_using.health) < self.effect:
                    heal = dice(1, (who_using.start_health - who_using.health))
                else:
                    heal = dice(1, self.effect)
                who_using.health += heal
                text = f'{who_using.name} восполняет {howmany(heal, "единицу жизни,единицы жизни,единиц жизни")}'
                if who_using.poisoned:
                    who_using.poisoned = False
                    text += ' и излечивается от отравления'
                tprint(game, text)
            elif self.type == 3:
                who_using.stren += self.effect
                tprint(game, f'На время боя {who_using.name} увеличивает свою силу '
                             f'на {str(self.effect)} до {str(who_using.stren)}.')
            elif self.type == 5:
                who_using.dext += self.effect
                tprint(game, f'На время боя {who_using.name} увеличивает свою ловкость '
                             f'на {str(self.effect)} до {str(who_using.dext)}.')
            elif self.type == 7:
                who_using.intel += self.effect
                tprint(game, f'На время боя {who_using.name} увеличивает свой интеллект '
                             f'на {str(self.effect)} до {str(who_using.intel)}.')
        who_using.pockets.remove(self)
        return True

    def __str__(self):
        return self.description

    def take(self, who):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')
        return True


class Book:
    def __init__(self, game, name=None):
        self.game = game
        self.name = name
        self.empty = False

    def on_create(self):
        self.type = dice(0, 2)
        description = randomitem(self.descriptions, False)
        self.name = description[0] + ' ' + self.name + ' ' + self.decorations[self.type]
        self.name1 = description[1] + ' ' + self.name1 + ' ' + self.decorations[self.type]
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

    def print_mastery(self, who):
        message = [f'{who.name} теперь немного лучше знает, как использовать {self.weapon_type} оружие.']
        return message

    def place(self, castle, room=None):
        if not room:
            rooms = []
            for i in castle.plan:
                if len(i.furniture) > 0:
                    rooms.append(i)
            room = randomitem(rooms, False)
        furniture = randomitem(room.furniture, False)
        furniture.put(self)
        return True

    def show(self):
        return self.description

    def use(self, who_using, in_action=False):
        if in_action:
            tprint(self.game, 'Сейчас абсолютно не подходящее время для чтения.')
            return False
        else:
            return who_using.read(self)

    def __str__(self):
        return self.name

    def take(self, who):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')
        return True
