from functions import readfile, randomitem, tprint, pprint
from class_monsters import Monster
from class_basic import Loot, Money
from class_items import Key
from settings import *
from random import randint as dice

decor1 = readfile('decorate1', False)
decor2 = readfile('decorate2', False)
decor3 = readfile('decorate3', False)
decor4 = readfile('decorate4', False)


class Furniture:
    def __init__(self, game, name=''):
        self.game = game
        new_loot = Loot(self.game)
        self.ambush = False
        self.loot = new_loot
        self.locked = False
        self.lockable = False
        self.opened = True
        self.can_contain_weapon = True
        self.can_hide = False
        self.name = name
        self.empty = 'пусто'
        self.state = 'стоит'
        self.where = 'в углу'
        self.name1 = 'мебель'

    def on_create(self):
        self.name = randomitem(self.descriptions, False) + ' ' + self.name
        self.state = randomitem(self.states, False)
        self.where = randomitem(self.wheres, False)
        return True

    def put(self, item):
        self.loot.pile.append(item)

    def show(self):
        message = []
        message.append(self.where + ' ' + self.state + ' ' + self.name + '.')
        if self.can_hide and self.ambush:
            message.append('Внутри слышится какая-то возня.')
        return message

    def place(self, castle = None, room_to_place = None):
        if room_to_place:
            print(room_to_place.furniture_types(), self.type)
            if self.type not in room_to_place.furniture_types():
                room_to_place.furniture.append(self)
                return True
            else:
                return False
        else:
            can_place = False
            while not can_place:
                room = randomitem(castle.plan, False)
                if self.type not in room.furniture_types():
                    can_place = True
        room.furniture.append(self)
        if dice(1, s_furniture_locked_possibility) == 1 and self.lockable:
            self.locked = True
            very_new_key = Key(self.game)
            very_new_key.place(castle)
        if dice(1, 100) <= 50:
            new_money = Money(self.game, dice(1, s_furniture_initial_money_maximum))
            self.loot.pile.append(new_money)
        return True


class Room:
    def __init__(self, game, doors, center='', loot=''):
        self.game = game
        self.doors = doors
        a = dice(0, len(decor1) - 1)
        self.decoration1 = decor1[a]
        a = dice(0, len(decor2) - 1)
        self.decoration2 = decor2[a]
        a = dice(0, len(decor3) - 1)
        self.decoration3 = decor3[a]
        a = dice(0, len(decor4) - 1)
        self.decoration4 = decor4[a]
        self.description = f'{self.decoration1} комнату {self.decoration2}. {self.decoration4}'
        self.center = center
        self.money = 0
        self.loot = loot
        self.secret_loot = Loot(self.game)
        self.locked = False
        self.position = -1
        self.visited = ' '
        self.ambush = ''
        self.rune_place = ''
        self.light = True
        self.morgue = None
        self.monsters = []
        self.furniture = []
        self.stink = 0
        self.stink_levels = s_room_stink_levels
        if not self.light or dice(1, s_room_torch_is_on_dice) != 4:
            self.torch = False
        else:
            self.torch = True
        self.secret_dict = s_room_secrets_dictionary
        self.secret_word = ''
        for i in self.secret_dict:
            if self.description.find(i) > -1:
                self.secret_word = i

    def show(self, player):
        game = self.game
        if self.stink > 0:
            stink_text = f'{self.stink_levels[self.stink]} воняет чем-то очень неприятным.'
        if self.light:
            if self.torch:
                self.decoration1 = f'освещенную факелом {self.decoration1}'
            if self.center == '':
                who_is_here = 'Не видно ничего интересного.'
            else:
                who_is_here = self.decoration3 + ' ' + self.center.state + ' ' + self.center.name + '.'
            message = []
            message.append(f'{player.name} попадает в {self.decoration1} '
                           f'комнату {self.decoration2}. {self.decoration4}')
            for furniture in self.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            message.append(who_is_here)
            if self.stink > 0:
                message.append(stink_text)
            tprint(game, message, state = 'direction')
        else:
            message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
            if isinstance(self.center, Monster):
                message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
            if self.stink > 0:
                message.append(stink_text)
            tprint(game, message, state = 'direction')

    def show_through_key_hole(self, who):
        message = []
        if self.center == '':
            message.append(f'{who.name} заглядывает в замочную скважину двери, но не может ничего толком разглядеть.')
        else:
            message.append(f'{who.name} заглядывает в замочную скважину двери и {self.center.key_hole}')
        if self.stink > 0:
            message.append(f'Из замочной скважины {self.stink_levels[self.stink].lower()} воняет чем-то омерзительным.')
        return message

    def furniture_types(self):
        types = []
        for furniture in self.furniture:
            if furniture.type not in types:
                types.append(furniture.type)
        return types

    def monster(self):
        if self.center != '':
            if isinstance(self.center, Monster):
                return self.center
            else:
                return False
        else:
            return False

    def monster_in_ambush(self):
        if self.ambush != '':
            if isinstance(self.ambush, Monster):
                return self.ambush
            else:
                return False
        else:
            return False

    def map(self):
        game=self.game
        doors_horizontal = {'0': '=', '1': ' ', '2': '-'}
        doors_vertical = {'0': '║', '1': ' ', '2': '|'}
        string1 = '=={0}=='.format(doors_horizontal[str(self.doors[0])])
        string2 = '║   ║'
        string3 = '{0} '.format(doors_vertical[str(self.doors[3])])
        if self.center != '':
            string3 += self.center.name[0]
        else:
            string3 += ' '
        string3 += ' {0}'.format(doors_vertical[str(self.doors[1])])
        string4 = '=={0}=='.format(doors_horizontal[str(self.doors[2])])
        if self.light:
            pprint(game, string1 + '\n' + string2 + '\n' + string3 + '\n' + string2 + '\n' + string4,
                   s_room_plan_picture_width, s_room_plan_picture_height)
            return True
        else:
            return False

    def lock(self, locked_or_not=2):
        game=self.game
        a = [-game.new_castle.rooms, 1, game.new_castle.rooms, -1]
        for i in range(4):
            if self.doors[i] == 1:
                self.doors[i] = locked_or_not
                j = i + 2 if (i + 2) < 4 else i - 2
                game.new_castle.plan[self.position + a[i]].doors[j] = locked_or_not
        self.locked = True
        return None
