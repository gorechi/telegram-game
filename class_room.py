from random import randint as dice

from class_basic import Loot, Money
from class_items import Key
from class_monsters import Monster
from functions import pprint, randomitem, readfile, tprint
from settings import *

decor1 = readfile('decorate1', False)
decor2 = readfile('decorate2', False)
decor3 = readfile('decorate3', False)
decor4 = readfile('decorate4', False)


class Furniture:
    def __init__(self, game, name=''):
        self.game = game
        new_loot = Loot(self.game)
        self.loot = new_loot
        self.locked = False
        self.lockable = False
        self.opened = True
        self.can_contain_weapon = True
        self.can_hide = False
        self.can_rest = False
        self.name = name
        self.empty = False
        self.empty_text = 'пусто'
        self.state = 'стоит'
        self.where = 'в углу'
        self.name1 = 'мебель'
        self.room = None

    def on_create(self):
        self.name = randomitem(self.descriptions, False) + ' ' + self.name
        self.state = randomitem(self.states, False)
        self.where = randomitem(self.wheres, False)
        return True

    def put(self, item):
        self.loot.pile.append(item)
   
    def monster_in_ambush(self):
        for monster in self.game.all_monsters:
            if monster.hiding_place == self:
                return monster 
        return False

    def show(self):
        message = []
        message.append(self.where + ' ' + self.state + ' ' + self.name + '.')
        if self.monster_in_ambush():
            message.append('Внутри слышится какая-то возня.')
        return message

    def place(self, castle=None, room_to_place=None):
        if room_to_place:
            if self.type not in room_to_place.furniture_types():
                room_to_place.furniture.append(self)
                self.room = room_to_place
            else:
                return False
        else:
            can_place = False
            while not can_place:
                room = randomitem(castle.plan, False)
                if self.type not in room.furniture_types():
                    can_place = True
            room.furniture.append(self)
            self.room = room
        if dice(1, s_furniture_locked_possibility) == 1 and self.lockable:
            self.locked = True
            very_new_key = Key(self.game)
            very_new_key.place(castle)
        if dice(1, 100) <= 50:
            new_money = Money(self.game, dice(1, s_furniture_initial_money_maximum))
            self.loot.pile.append(new_money)
        return True


class Room:
    def __init__(self, game, doors, loot=None):
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
        self.money = 0
        if loot == '' or not loot:
            self.loot = self.game.empty_thing
        else:
            self.loot = loot
        self.secret_loot = Loot(self.game)
        self.locked = False
        self.position = -1
        self.visited = ' '
        self.rune_place = self.game.empty_thing
        self.light = True
        self.morgue = None
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

    def can_rest(self):
        """Функция проверяет, можно ли отдыхать в комнате

        Returns:
            list: Список причин, почему нельзя отдыхать в комнате
            obj Furniture: Объект мебели, который позволяет отдохнуть
        """
        message = []
        monster = self.monster()
        if monster:
            message.append('Враг, который находится в комнате, точно не даст отдохнуть.')
        if self.stink > 0:
            message.append('В комнате слишком сильно воняет чтобы уснуть.')
        if not self.light:
            message.append('В комнате так темно, что нельзя толком устроиться на отдых.')
        place = False
        for furniture in self.furniture:
            if furniture.can_rest:
                place = furniture
        if not place:
            message.append('В комнате нет места, где можно было бы отдохнуть.')
        return message, place
    
    def show(self, player):
        game = self.game
        monster = self.monster()
        if self.stink > 0:
            stink_text = f'{self.stink_levels[self.stink]} воняет чем-то очень неприятным.'
        if self.light:
            if self.torch:
                decoration1 = f'освещенную факелом {self.decoration1}'
            else:
                decoration1 = self.decoration1
            if not monster:
                who_is_here = 'Не видно ничего интересного.'
            else:
                who_is_here = f'{self.decoration3} {monster.state} {monster.name}.'
            message = []
            message.append(f'{player.name} попадает в {decoration1} '
                           f'комнату {self.decoration2}. {self.decoration4}')
            for furniture in self.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            message.append(who_is_here)
            if self.stink > 0:
                message.append(stink_text)
            tprint(game, message, state = 'direction')
        else:
            message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
            if monster:
                message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
            if self.stink > 0:
                message.append(stink_text)
            tprint(game, message, state = 'direction')

    def show_through_key_hole(self, who):
        monster = self.monster()
        message = []
        if not monster:
            message.append(f'{who.name} заглядывает в замочную скважину двери, но не может ничего толком разглядеть.')
        else:
            message.append(f'{who.name} заглядывает в замочную скважину двери и {monster.key_hole}')
        if self.stink > 0:
            message.append(f'Из замочной скважины {self.stink_levels[self.stink].lower()} воняет чем-то омерзительным.')
        return message

    def furniture_types(self):
        types = []
        for furniture in self.furniture:
            if furniture.type not in types:
                types.append(furniture.type)
        return types

    def monsters(self, mode=None):
        all_monsters = []
        for monster in self.game.all_monsters:
            if monster.room == self or monster.hiding_place == self:
                all_monsters.append(monster)
        if len(all_monsters) > 0:
            if mode == 'random':
                return randomitem(all_monsters, False)
            else:
                return all_monsters
        else:
            return False
        
    def monster(self):
        for monster in self.game.all_monsters:
            if monster.room == self:
                return monster 
        return False

    def monster_in_ambush(self):
        for monster in self.game.all_monsters:
            if monster.hiding_place == self:
                return monster 
        return False
    
    def map(self):
        game=self.game
        monster = self.monster()
        doors_horizontal = {'0': '=', '1': ' ', '2': '-'}
        doors_vertical = {'0': '║', '1': ' ', '2': '|'}
        string1 = '=={0}=='.format(doors_horizontal[str(self.doors[0])])
        string2 = '║   ║'
        string3 = '{0} '.format(doors_vertical[str(self.doors[3])])
        if monster:
            string3 += monster.name[0]
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
