from functions import randomitem, howmany, tprint
from class_basic import *
from settings import *
from math import sqrt
from math import floor
from random import randint as dice


class Item:
    def __init__(self, game):
        self.game = game
        self.name = 'штука'
        self.name1 = 'штуку'
        self.can_use_in_fight = False
        self.description = self.name
        self.empty = False

    def __str__(self):
        return self.name

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')

    def use(self, who_is_using, in_action=False):
        tprint(self.game, f'{who_is_using.name} не знает, как использовать такие штуки.')

    def show(self):
        return self.description


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
        self.description = self.name + ' ' + s_elements_dictionary[self.element]
        self.empty = False

    def __str__(self):
        return f'{self.name} {s_elements_dictionary[self.element]} - ' \
               f'урон + {str(self.damage)} или защита + {str(self.defence)}'

    def on_create(self):
        return True

    def place(self, castle, room_to_place=None):
        rooms_with_secrets = [i for i in castle.plan if i.secret_word]
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if room in rooms_with_secrets:
            room.secret_loot.pile.append(self)
            return True
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

    def element(self):
        return int(self.element)

    def take(self, who=''):
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')

    def show(self):
        return f'{self.name} {s_elements_dictionary[self.element]} - ' \
               f'урон + {str(self.damage)} или защита + {str(self.defence)}'

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


class Matches():
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
        game = self.game
        if room_to_place:
            room = room_to_place
        else:
            done = False
            while not done:
                room = randomitem(game.new_castle.plan, False)
                if not room.locked and room.light:
                    done = True
            self.room = room
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

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
        room = game.new_castle.plan[who_is_using.current_position]
        if room.light:
            message = ['Незачем тратить спички, здесь и так светло.']
            tprint(game, message)
        else:
            room.light = True
            room.torch = True
            message = [f'{who_is_using.name} зажигает факел и комната озаряется светом']
            if not room.center.empty and room.center.frightening:
                    message.append(f'{who_is_using.name} замирает от ужаса глядя на чудовище перед собой.')
                    who_is_using.fear += 1
            tprint(game, message)
            room.show(who_is_using)
            room.map()
            if not room.center.empty and room.center.agressive:
                    player.fight(room.center, True)

class Map():
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'карта'
        self.name1 = 'карту'
        self.empty = False
        self.description = 'Карта, показывающая расположение комнат замка'

    def place(self, castle, room_to_place=None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

    def show(self):
        return self.description

    def use(self, who_is_using, in_action=False):
        """Функция использования карты. Если вызывается в бою, то ничего не происходит. 
        В мирное время выводит на экран карту замка.

        Args:
            who_is_using (oject Hero): Герой, который использует карту
            in_action (bool, optional): Признак того, что предмет используется в бою. По умолчанию False.

        """
        if not in_action:
            if who_is_using.fear >= s_fear_limit:
                tprint(self.game, f'{who_is_using.name} от страха не может сосредоточиться и что-то разобрать на карте.')
                return False
            else:    
                tprint(self.game, f'{who_is_using.name} смотрит на карту замка.')
                self.game.new_castle.map()
                return True
        else:
            tprint(self.game, 'Во время боя это совершенно неуместно!')
            return False

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')


class Key():
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

    def place(self, castle, room_to_place=None):
        furniture = False
        if room_to_place:
            room = room_to_place
        else:
            unlocked_rooms = [a for a in castle.plan if (not a.locked)]
            room = randomitem(unlocked_rooms, False)
        if len(room.furniture) > 0:
            for i in room.furniture:
                if not i.locked:
                    furniture = i
            if furniture:
                furniture.put(self)
                return True
        room.loot.pile.append(self)

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')


class Potion():
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

    def place(self, castle, room_to_place=None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

    def use(self, who_using, in_action=False):
        game = self.game
        if not in_action:
            if self.type == 1:
                who_using.start_health += self.effect
                who_using.health += self.effect
                tprint(game, f'{who_using.name} увеличивает свое максимальное здоровье '
                             f'на {str(self.effect)} до {str(who_using.health)}.')
                return True
            elif self.type == 2:
                who_using.stren += self.effect
                who_using.start_stren += self.effect
                tprint(game, f'{who_using.name} увеличивает свою силу на {str(self.effect)} до {str(who_using.stren)}.')
                return True
            elif self.type == 4:
                who_using.dext += self.effect
                who_using.start_dext += self.effect
                tprint(game, f'{who_using.name} увеличивает свою ловкость '
                             f'на {str(self.effect)} до {str(who_using.dext)}.')
                return True
            elif self.type == 6:
                who_using.intel += self.effect
                who_using.start_intel += self.effect
                tprint(game, f'{who_using.name} увеличивает свой интеллект '
                             f'на {str(self.effect)} до {str(who_using.intel)}.')
                return True
            else:
                tprint(game, 'Это зелье можно использовать только в бою!')
                return False
        else:
            if self.type == 0:
                if (who_using.start_health - who_using.health) < self.effect:
                    heal = dice(1, (who_using.start_health - who_using.health))
                else:
                    heal = dice(1, self.effect)
                who_using.health += heal
                tprint(game, f'{who_using.name} восполняет {howmany(heal, "единицу жизни,единицы жизни,единиц жизни")}')
                return True
            elif self.type == 3:
                who_using.stren += self.effect
                tprint(game, f'На время боя {who_using.name} увеличивает свою силу '
                             f'на {str(self.effect)} до {str(who_using.stren)}.')
                return True
            elif self.type == 5:
                who_using.dext += self.effect
                tprint(game, f'На время боя {who_using.name} увеличивает свою ловкость '
                             f'на {str(self.effect)} до {str(who_using.dext)}.')
                return True
            elif self.type == 7:
                who_using.intel += self.effect
                tprint(game, f'На время боя {who_using.name} увеличивает свой интеллект '
                             f'на {str(self.effect)} до {str(who_using.intel)}.')
                return True
            else:
                tprint(game, 'Это зелье нельзя использовать в бою!')
                return False

    def __str__(self):
        return self.description

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name} себе.')


class Book():
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

    def place(self, castle, room_to_place=None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = []
            for i in castle.plan:
                if len(i.furniture) > 0:
                    rooms.append(i)
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

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

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, f'{who.name} забирает {self.name1} себе.')
