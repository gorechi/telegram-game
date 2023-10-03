from random import randint as dice
from typing import NoReturn

from class_basic import Loot, Money
from class_items import Key
from class_monsters import Monster
from functions import pprint, randomitem, readfile, tprint
from settings import *


class Door:
    """Класс дверей."""
    
    
    def __init__(self, game=None):
        self.empty = True
        self.game = game

    
    def activate(self):
        self.empty = False
        self.locked = False
        self.closed = True
        
    def horizontal_symbol(self) -> str:
        if self.empty:
            return '='
        elif self.locked:
            return '-'
        else:
            return ' '       

    def vertical_symbol(self) -> str:
        if self.empty:
            return '║'
        elif self.locked:
            return '|'
        else:
            return ' '

class Furniture:
    """Класс мебели."""
    
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

    def __str__(self):
        return self.where + ' ' + self.state + ' ' + self.name
    
    
    def on_create(self):
        self.name = randomitem(self.descriptions, False) + ' ' + self.name
        self.state = randomitem(self.states, False)
        self.where = randomitem(self.wheres, False)
        return True

    def put(self, item):
        self.loot.pile.append(item)
   
    def monster_in_ambush(self):
        monsters = self.room.monsters()
        if monsters:
            for monster in monsters:
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
    """Класс комнат."""
    
    decor1 = readfile('decorate1', False)
    decor2 = readfile('decorate2', False)
    decor3 = readfile('decorate3', False)
    decor4 = readfile('decorate4', False)
    
    
    def __init__(self, game, floor, doors):
        self.game = game
        self.floor = floor
        self.doors = doors
        self.money = 0
        self.decorate()
        self.loot = Loot(self.game)
        self.secret_loot = Loot(self.game)
        self.locked = False
        self.position = -1
        self.visited = ' '
        self.rune_place = self.game.empty_thing
        self.light = True
        self.morgue = []
        self.furniture = []
        self.stink = 0
        self.stink_levels = s_room_stink_levels
        if not self.light or dice(1, s_room_torch_is_on_dice) != 4:
            self.torch = False
        else:
            self.torch = True
        self.secret_word = self.get_secret_word()

    
    def get_secret_word(self) -> str:
        secret_word = ''
        for i in s_room_secrets_dictionary:
            if self.description.find(i) > -1:
                secret_word = i
        return secret_word
    
    
    def decorate(self):
        self.decoration1 = randomitem(Room.decor1)
        self.decoration2 = randomitem(Room.decor2)
        self.decoration3 = randomitem(Room.decor3)
        self.decoration4 = randomitem(Room.decor4)
        self.description = f'{self.decoration1} комнату {self.decoration2}. {self.decoration4}'

    
    def can_rest(self):
        """Функция проверяет, можно ли отдыхать в комнате

        Returns:
            list: Список причин, почему нельзя отдыхать в комнате
            obj Furniture: Объект мебели, который позволяет отдохнуть
        """
        message = []
        monster = self.monsters('first')
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
        monsters = self.monsters()
        if monsters:
            monster = monsters[0]
        else:
            monster = None
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
        monster = self.monsters('first')
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
        all_monsters = self.floor.monsters_in_rooms[self]
        if all_monsters:
            if mode == 'random':
                return randomitem(all_monsters, False)
            elif mode == 'first':
                return all_monsters[0]
            else:
                return all_monsters
        else:
            return False
        
    def monster_in_ambush(self):
        monsters = self.monsters()
        if monsters:
            for monster in self.monsters():
                if monster.hiding_place == self:
                    return monster 
        return False
    
    def map(self):
        if not self.light:
            return False
        game=self.game
        monsters = self.monsters()
        if monsters:
            monster = monsters[0]
        else:
            monster = None
        string1 = '=={0}=='.format(self.doors[0].horizontal_symbol())
        string2 = '║   ║'
        string3 = '{0} '.format(self.doors[3].vertical_symbol())
        if monster:
            string3 += monster.name[0]
        else:
            string3 += ' '
        string3 += ' {0}'.format(self.doors[1].vertical_symbol())
        string4 = '=={0}=='.format(self.doors[2].horizontal_symbol())
        pprint(game, string1 + '\n' + string2 + '\n' + string3 + '\n' + string2 + '\n' + string4,
                s_room_plan_picture_width, s_room_plan_picture_height)
        return True

    
    def lock(self):
        for door in self.doors:
            if not door.empty:
                door.locked = True
        self.locked = True
        return None
    
    def turn_on_light(self, who) -> NoReturn:
        
        """Метод зажигания в комнате света. """
        
        self.light = True
        self.torch = True
        monster = self.monsters('first')
        message = [
                f'{who.name} зажигает факел и комната озаряется светом']
        if monster:
            if monster.frightening:
                message.append(
                        f'{who.name} замирает от ужаса глядя на чудовище перед собой.')
                who.fear += 1
        tprint(self.game, message)
        self.show(who)
        self.map()
        if monster:
            if monster.agressive:
                who.fight(monster.name, True)
                
    
    def get_random_unlocked_furniture(self) -> Furniture:
        if self.furniture:
            furniture_list = [f for f in self.furniture if not f.locked]
            return randomitem(furniture_list, neednumber=False)
        return None
