#!/usr/bin/python
# -*- coding: utf-8 -*-
# Импортируем необходимые модули

import telebot
from telebot import types
from functions import *
from PIL import Image, ImageDraw, ImageFont

# Константы и настройки
TOKEN = '1528705199:AAH_tVPWr6GuxBLdxOhGNUd25tNEc23pSp8' #Токен телеграм-бота
# IN_FIGHT = False # Константа, отвечающая за то, что сейчас бой
# LEVEL_UP = False # Константа, отвечающая за то, что сейчас происходит прокачка
# ENCHANTING = False # Константа, отвечающая за то, что сейчас происходит улучшение шмотки
# selectedItem = ''
game_sessions = {}
telegram_commands = ['обыскать',
                     '?',
                     'осмотреть',
                     'идти',
                     'атаковать',
                     'взять',
                     'открыть',
                     'использовать',
                     'улучшить'] # Команды для бота во время игры
fight_commands = ['ударить',
                  '?',
                  'защититься',
                  'бежать',
                  'сменить оружие',
                  'сменить',
                  'использовать'] # Команды для бота во время боя
level_up_commands = ['здоровье',
                     'силу',
                     'ловкость',
                     'интеллект'] # Команды для бота во время прокачки
# howMany = { 'монстры': 10,
#             'оружие': 10,
#             'щит': 5,
#             'доспех': 5,
#             'зелье': 10,
#             'мебель':10,
#             'книга':5,
#             'руна': 10} # Количество всяких штук, которые разбрасываются по замку
decor1 = readfile('decorate1', False)
decor2 = readfile('decorate2', False)
decor3 = readfile('decorate3', False)
decor4 = readfile('decorate4', False)
# Таблица слабостей
weakness = {1: [3, 3], 2: [3, 6], 3: [7, 7], 4: [3, 7], 6: [7, 14], 7: [12, 12], 8: [3, 12], 10: [7, 12], 12: [1, 1],
            13: [1, 3], 14: [12, 24], 15: [1, 7], 19: [1, 12], 24: [1, 2]}
# Таблица стихий
elementDictionary = {1: 'огня', 2: 'пламени', 3: 'воздуха', 4: 'дыма', 6: 'ветра', 7: 'земли', 8: 'лавы', 10: 'пыли',
                     12: 'воды', 13: 'пара', 14: 'камня', 15: 'дождя', 19: 'грязи', 24: 'потопа'}

# Описываем классы

class Item:
    def __init__(self, game):
        self.game = game
        self.name = 'штука'
        self.name1 = 'штуку'
        self.canUseInFight = False
        self.description = self.name

    def __str__(self):
        return self.name

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.name + ' себе.')

    def use(self, whoisusing, inaction=False):
        tprint(self.game, whoisusing.name + ' не знает, как использовать такие штуки.')

    def show(self):
        return self.description

class Rune:
    def __init__(self, game):
        self.game = game
        self.damage = 4 - floor(sqrt(dice(1, 15)))
        self.defence = 3 - floor(sqrt(dice(1, 8)))
        self.elements = [1, 3, 7, 12]
        self.element = self.elements[dice(0,3)]
        self.canUseInFight = False
        self.name = 'руна'
        self.name1 = 'руну'
        self.description = self.name + ' ' + elementDictionary[self.element]

    def __str__(self):
        return self.name + ' ' + elementDictionary[self.element] + ' - урон + ' + str(self.damage) + \
               ' или защита + ' + str(self.defence)

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        print ('room center = ', room.center)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            print ('Положен в мебель: ' + furniture.name)
            print('-' * 20)
            return True
        room.loot.add(self)
        print('Брошено в комнату')
        print('-'*20)

    def element(self):
        return int(self.element)

    def take(self, who=''):
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.name1 + ' себе.')

    def show(self):
        return self.name + ' ' + elementDictionary[self.element] + ' - урон + ' + str(self.damage) + \
               ' или защита + ' + str(self.defence)

    def use(self, whoisusing, inaction=False):
        tprint(self.game, whoisusing.name + ' не знает, как использовать такие штуки.')


class Spell:
    def __init__(self, game, name='Обычное заклинание', name1='Обычного заклинания', element='магия', minDamage=1,
                 maxDamage=5, minDamageMult=1, maxDamageMult=1, actions='кастует'):
        self.game = game
        self.name = name
        self.name1 = name1
        self.description = self.name
        self.element = element
        self.minDamageMult = minDamageMult
        self.maxDamageMult = maxDamageMult
        self.actions = actions
        self.maxDamage = maxDamage
        self.minDamage = minDamage

    def __str__(self):
        return self.name

class Weapon:
    def __init__(self, game, name='', name1='оружие', damage=1, actions='бьет,ударяет'):
        self.game = game
        if name != 0:
            self.name = name
            self.damage = int(damage)
            self.name1 = name1
        else:
            self.n1 = [['Большой', 'Большая', 'Большой', 'Большую'],
                       ['Малый', 'Малая', 'Малый', 'Малую'],
                       ['Старый', 'Старая', 'Старый', 'Старую'],
                       ['Тяжелый', 'Тяжелая', 'Тяжелый', 'Тяжелую'],
                       ['Новый', 'Новая', 'Новый', 'Новую']]
            self.n2 = [['меч', 0, 'меч', 'рубящее'],
                       ['сабля', 1, 'саблю', 'рубящее'],
                       ['катана', 1, 'катану', 'рубящее'],
                       ['рапира', 1, 'рапиру', 'колющее'],
                       ['пика', 1, 'пику', 'колющее'],
                       ['топор', 0, 'топор', 'рубящее'],
                       ['кинжал', 0, 'кинжал', 'колющее'],
                       ['дубина', 1, 'дубину', 'ударное'],
                       ['палица', 1, 'палицу', 'ударное'],
                       ['булава', 1, 'булаву', 'ударное'],
                       ['молот', 0, 'молот', 'ударное'],
                       ['шпага', 1, 'шпагу', 'колющее']]
            self.a1 = dice(0, len(self.n1) - 1)
            self.a2 = dice(0, len(self.n2) - 1)
            self.name = self.n1[self.a1][self.n2[self.a2][1]] + ' ' + self.n2[self.a2][0]
            self.name1 = self.n1[self.a1][self.n2[self.a2][1]+2] + ' ' + self.n2[self.a2][2]
            self.damage = dice(3, 12)
            self.type = self.n2[self.a2][3]
        self.actions = actions.split(',')
        self.canUseInFight = True
        self.runes = []

    def on_create(self):
        return True

    def __str__(self):
        damageString = str(self.damage)
        if self.permdamage() != 0:
            damageString += '+' + str(self.permdamage())
        return self.name + self.enchantment() + ' (' + damageString + ')'

    def realname(self):
        names = []
        if self.element() != 0:
            names.append(self.name + ' ' + elementDictionary[self.element()])
            names.append(self.name1 + ' ' + elementDictionary[self.element()])
        else:
            names.append(self.name)
            names.append(self.name1)
        return names

    def element(self):
        elementSum = 0
        for rune in self.runes:
            elementSum += rune.element
        return elementSum

    def enchant(self, rune):
        if len(self.runes) > 1:
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
            return ' ' + elementDictionary[element]

    def permdamage(self):
        damage = 0
        if len(self.runes) in [1, 2]:
            for rune in self.runes:
                damage += rune.damage
        return damage

    def attack(self):
        return dice(1, int(self.damage)) + self.permdamage()

    def take(self, who):
        game = self.game
        message = [who.name + ' берет ' + self.name1 + '.']
        weapon = who.weapon
        second_weapon = who.second_weapon()
        if weapon == '':
            who.weapon = self
            message.append(who.name + ' теперь использует ' + self.name1 + ' в качестве оружия.')
        else:
            if second_weapon:
                message.append('В рюкзаке для нового оружия нет места, поэтому приходится бросить ' + weapon.name + '.')
                who.drop(weapon)
                who.weapon = self
            else:
                message.append('В рюкзаке находится место для второго оружия. Во время схватки можно "Сменить" оружие.')
                who.pockets.append(self)
        tprint(game, message)

    def show(self):
        damageString = str(self.damage)
        if self.permdamage() != 0:
            damageString += '+' + str(self.permdamage())
        return self.name + self.enchantment() + ' (' + damageString + ')'

    def use(self, whoUsing, inaction=False):
        if whoUsing.weapon == '':
            whoUsing.weapon = self
        else:
            whoUsing.pockets.append(whoUsing.weapon)
            whoUsing.weapon = self
            whoUsing.pockets.remove(self)
        tprint(self.game, whoUsing.name + ' теперь использует ' + self.name1 + ' в качестве оружия!')

    def place(self, castle, room_to_place = None):
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        print ('room center = ', room.center)
        if room.center != '':
            if isinstance(room.center, Monster):
                monster = room.center
                if monster.carryweapon:
                    monster.give(self)
                    print ('Отдан ', monster.name)
                    print('-' * 20)
                    return True
        elif room.ambush != '':
            print ('room ambush = ', room.ambush)
            monster = room.ambush
            if monster.carryweapon:
                monster.give(self)
                print('Отдан ', monster.name)
                print('-' * 20)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            if furniture.can_contain_weapon:
                furniture.put(self)
                print ('Положен в мебель: ' + furniture.name)
                return True
        room.loot.add(self)
        print('Брошен в комнату')
        print('-'*20)

class Protection:
    def __init__(self, game, name='', name1='защиту', protection=1, actions=''):
        self.game = game
        self.name = name
        self.name1 = name1
        self.actions = actions.split(',')
        self.canUseInFight = True
        self.runes = []

    def __str__(self):
        protectionString = str(self.protection)
        if self.permprotection() != 0:
            protectionString += '+' + str(self.permprotection())
        return self.name + self.enchantment() + ' (' + protectionString + ')'

    def on_create(self):
        return True

    def realname(self):
        names = []
        if self.element() != 0:
            names.append(self.name + ' ' + elementDictionary[self.element()])
            names.append(self.name1 + ' ' + elementDictionary[self.element()])
        else:
            names.append(self.name)
            names.append(self.name1)
        return names

    def element(self):
        elementSum = 0
        for rune in self.runes:
            elementSum += rune.element
        return elementSum

    def permprotection(self):
        protection = 0
        if len(self.runes) in [1, 2]:
            for rune in self.runes:
                protection += rune.defence
        return protection

    def enchant(self, rune):
        if len(self.runes) > 1:
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
            return ' ' + elementDictionary[element]

    def protect(self, who):
        multiplier = 1
        if who.weapon and who.weapon.element() != 0 and self.element() != 0:
            if who.weapon.element() in weakness[self.element()]:
                multiplier = 1.5
            elif self.element() in weakness[who.weapon.element()]:
                multiplier = 0.67
        tprint(self.game, 'Множитель защиты - ' + str(multiplier))
        if who.hide:
            who.hide = False
            return self.protection + self.permprotection()
        else:
            if self.protection > 0:
                return ceil((dice(1, self.protection) + self.permprotection())*multiplier)
            else:
                return 0

    def take(self, who):
        if who.shield == '':
            who.shield = self
            tprint(self.game, who.name + ' использует ' + self.name1 + ' как защиту.')
        else:
            self.game.player.pockets.append(self)
            tprint(self.game, who.name + ' забирает ' + self.name1 + ' себе.')

    def show(self):
        protectionString = str(self.protection)
        if self.permprotection() != 0:
            protectionString += '+' + str(self.permprotection())
        return self.name + self.enchantment() + ' (' + protectionString + ')'

    def use(self, whoUsing, inaction=False):
        if whoUsing.shield == '':
            whoUsing.shield = self
        else:
            whoUsing.pockets.append(whoUsing.shield)
            whoUsing.shield = self
            whoUsing.pockets.remove(self)
        tprint(self.game, whoUsing.name + ' теперь использует ' + self.name1 + ' в качестве защиты!')

#Класс Доспех (подкласс Защиты)
class Armor(Protection):
    def __init__(self, game, name='', name1='доспех', protection=1, actions=''):
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
                  ['панцырь', 0, 'панцырь']]
            a1 = dice(0, len(n1) - 1)
            a2 = dice(0, len(n2) - 1)
            self.name = n1[a1][n2[a2][1]] + ' ' + n2[a2][0]
            self.name1 = n1[a1][n2[a2][1]+2] + ' ' + n2[a2][2]
            self.protection = dice(1, 3)
        self.actions = actions.split(',')
        self.canUseInFight = True
        self.runes = []

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        print ('room center = ', room.center)
        if room.center != '':
            if isinstance(room.center, Monster):
                monster = room.center
                if monster.wearArmor:
                    monster.give(self)
                    print ('Отдан ', monster.name)
                    print('-' * 20)
                    return True
        elif room.ambush != '':
            print ('room ambush = ', room.ambush)
            monster = room.ambush
            if monster.wearArmor:
                monster.give(self)
                print('Отдан ', monster.name)
                print('-' * 20)
                return True
            elif len(room.furniture) > 0:
                furniture = randomitem(room.furniture, False)
                if furniture.can_contain_weapon:
                    furniture.put(self)
                    print('Положен в мебель: ' + furniture.name)
                    return True
        room.loot.add(self)
        print('Брошен в комнату')
        print('-'*20)

# Доспех можно надеть. Если на персонаже уже есть доспех, персонаж выбрасывает его и он становится частью лута комнаты.
    def take(self, who):
        oldArmor = who.armor
        message = [who.name + ' использует ' + self.name1 + ' как защиту.']
        if oldArmor != '':
            message.append('При этом он снимает ' + oldArmor.name1 + ' и оставляет валяться на полу.')
            who.drop(oldArmor)
        who.armor = self
        tprint(self.game, message)

#Класс Щит (подкласс Защиты)
class Shield (Protection):
    def __init__(self, game, name='', name1='щит', protection=1, actions=''):
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
        self.canUseInFight = True
        self.runes = []

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        print ('room center = ', room.center)
        if room.center != '':
            if isinstance(room.center, Monster):
                monster = room.center
                if monster.carryshield:
                    monster.give(self)
                    print ('Отдан ', monster.name)
                    print('-' * 20)
                    return True
        elif room.ambush != '':
            print ('room ambush = ', room.ambush)
            monster = room.ambush
            if monster.carryshield:
                monster.give(self)
                print('Отдан ', monster.name)
                print('-' * 20)
                return True
            elif len(room.furniture) > 0:
                furniture = randomitem(room.furniture, False)
                if furniture.can_contain_weapon:
                    furniture.put(self)
                    print('Положен в мебель: ' + furniture.name)
                    return True
        room.loot.add(self)
        print('Брошен в комнату')
        print('-'*20)

# Щит можно взять в руку. Если в руке ужесть щит, персонаж выбрасывает его и он становится частью лута комнаты.
    def take(self, who):
        oldShield = who.shield
        message = [who.name + ' берет ' + self.name1 + ' в руку.']
        if oldShield != '':
            message.append('При этом он бросает старый ' + oldShield.name1 + ' и оставляет валяться на полу.')
            who.drop(oldShield)
        who.shield = self
        tprint(self.game, message)

class Matches(Item):
    def __init__(self, game):
        self.game = game
        self.canUseInFight = False
        self.name = 'спички'
        self.name1 = 'спички'
        self.description = 'Спички, которыми можно что-то поджечь'
        self.room = None

    def place(self, castle, room_to_place = None):
        game = self.game
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            done = False
            while not done:
                room = randomitem(game.newCastle.plan, False)
                print ('В комнате светло: ', room.light, 'Комната заперта: ', room.locked)
                if not room.locked and room.light:
                    done = True
            self.room = room
        print ('room center = ', room.center)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            print ('Положен в мебель: ' + furniture.name)
            print('-' * 20)
            return True
        room.loot.add(self)
        print('Брошено в комнату')
        print('-'*20)

    def use(self, whoIsUsing = None, inaction = False):
        player = self.game.player
        game = self.game
        if not whoIsUsing:
            whoIsUsing = player
        room = game.newCastle.plan[whoIsUsing.currentPosition]
        if room.light:
            message = ['Незачем тратить спички, здесь и так светло.']
            tprint(game, message)
        else:
            room.light = True
            room.torch = True
            message = [whoIsUsing.name + ' зажигает факел и комната озаряется светом']
            tprint(game, message)
            room.show(whoIsUsing)
            room.map()
            if room.center != '':
                if room.center.agressive:
                    player.fight(room.center, True)

class Map(Item):
    def __init__(self, game):
        self.game = game
        self.canUseInFight = False
        self.name = 'карта'
        self.name1 = 'карту'
        self.description = 'Карта, показывающая расположение комнат замка'

    def place(self, castle, room_to_place = None):
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        print ('room center = ', room.center)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            print ('Положен в мебель: ' + furniture.name)
            print('-' * 20)
            return True
        room.loot.add(self)
        print('Брошено в комнату')
        print('-'*20)

    def use(self, whoisusing, inaction=False):
        if not inaction:
            tprint(self.game, whoisusing.name + ' смотрит на карту замка.')
            self.game.newCastle.map()
            return True
        else:
            tprint(self.game, 'Во время боя это совершенно неуместно!')
            return False

class Key(Item):
    def __init__(self, game):
        self.game = game
        self.canUseInFight = False
        self.name = 'ключ'
        self.name1 = 'ключ'
        self.description = 'Ключ, пригодный для дверей и сундуков'

    def __str__(self):
        return self.description

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        print (self.name)
        furniture = False
        if room_to_place:
            room = room_to_place
        else:
            unlockedRooms = [a for a in castle.plan if (not a.locked)]
            room = randomitem(unlockedRooms, False)
        print ('room center = ', room.center)
        if len(room.furniture) > 0:
            for i in room.furniture:
                if not i.locked:
                    furniture = i
            if furniture:
                furniture.put(self)
                print ('Положен в мебель: ' + furniture.name)
                print('-' * 20)
                return True
        room.loot.add(self)
        print('Брошено в комнату')
        print('-'*20)

class Potion(Item):
    def __init__(self, game, name='', effect=0, type=0, canUseInFight=True):
        self.game = game
        self.name = name
        potions = [['Зелье исцеления', 10, 0, True,
                    'Лечебное зелье восстанавливает некоторое количество единиц здоровья.'],
                   ['Зелье здоровья', 1, 1, False,
                    'Зелье здоровья увеличивает максимальный запас здоровья персонажа.'],
                   ['Зелье силы', 1, 2, False,
                    'Зелье силы увеличивает максимальное значение силы персонажа.'],
                   ['Зелье усиления', 5, 3, True,
                    'Зелье усиления временно добавляет персонажу силы.'],
                   ['Зелье ловкости', 1, 4, False,
                    'Зелье ловкости увеличивает максимальное значение ловкости персонажа.'],
                   ['Зелье увертливости', 5, 5, True,
                    'Зелье увертливости временно добавляет персонажу ловкости.'],
                   ['Зелье ума', 1, 6, False,
                    'Зелье ума увеличивает максимальное значение силы интеллекта.'],
                   ['Зелье просветления', 5, 7, True,
                    'Зелье просветления временно добавляет персонажу интеллекта.']]
        if self.name != 0:
            self.name = name
            self.name1 = self.name
            self.effect = int(effect)
            self.type = int(type)
            self.canUseInFight = canUseInFight
            self.description = potions[self.type][4]
        elif self.name == 0:
            n = dice (0, 5)
            self.name = potions[n][0]
            self.name1 = self.name
            self.effect = potions[n][1]
            self.type = potions[n][2]
            self.canUseInFight = potions[n][3]
            self.description = potions[n][4]

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        print (self.name)
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            print ('Положен в мебель: ' + furniture.name)
            return True
        room.loot.add(self)
        print('Брошено в комнату')
        print('-'*20)

    def use(self, whoUsing, inaction = False):
        game = self.game
        if not inaction:
            if self.type == 1:
                whoUsing.startHealth += self.effect
                whoUsing.health += self.effect
                tprint (game, whoUsing.name + ' увеличивает свое максмальное здоровье на ' +
                        str(self.effect) + ' до ' + str(whoUsing.health) + '.')
                return True
            elif self.type == 2:
                whoUsing.stren += self.effect
                whoUsing.startStren += self.effect
                tprint (game, whoUsing.name + ' увеличивает свою силу на ' +
                        str(self.effect) + ' до ' + str(whoUsing.stren) + '.')
                return True
            elif self.type == 4:
                whoUsing.dext += self.effect
                whoUsing.startDext += self.effect
                tprint (game, whoUsing.name + ' увеличивает свою ловкость на ' +
                        str(self.effect) + ' до ' + str(whoUsing.dext) + '.')
                return True
            elif self.type == 6:
                whoUsing.intel += self.effect
                whoUsing.startIntel += self.effect
                tprint (game, whoUsing.name + ' увеличивает свой интеллект на ' +
                        str(self.effect) + ' до ' + str(whoUsing.intel) + '.')
                return True
            else:
                tprint(game, 'Это зелье можно использовать только в бою!')
                return False
        else:
            if self.type == 0:
                if (whoUsing.startHealth - whoUsing.health) < self.effect:
                    heal = dice(1, (whoUsing.startHealth - whoUsing.health))
                else:
                    heal = dice(1, self.effect)
                whoUsing.health += heal
                tprint (game, whoUsing.name +
                        ' восполняет ' +
                        howmany(heal, 'единицу жизни,единицы жизни,единиц жизни'))
                return True
            elif self.type == 3:
                whoUsing.stren += self.effect
                tprint (game, 'На время боя ' + whoUsing.name + ' увеличивает свою силу на ' +
                        str(self.effect) + ' до ' + str(whoUsing.stren) + '.')
                return True
            elif self.type == 5:
                whoUsing.dext += self.effect
                tprint (game, 'На время боя ' + whoUsing.name + ' увеличивает свою ловкость на ' +
                        str(self.effect) + ' до ' + str(whoUsing.dext) + '.')
                return True
            elif self.type == 7:
                whoUsing.intel += self.effect
                tprint (game, 'На время боя ' + whoUsing.name + ' увеличивает свой интеллект на ' +
                        str(self.effect) + ' до ' + str(whoUsing.intel) + '.')
                return True
            else:
                tprint(game, 'Это зелье нельзя использовать в бою!')
                return False
    def __str__(self):
        return self.description

class Book(Item):
    def __init__(self, game, name=''):
        self.game = game
        self.name = name

    def on_create(self):
        self.type = dice(0,2)
        self.name = randomitem(self.descriptions, False) + ' ' + self.name + ' ' + self.decorations[self.type]
        print(self.name)
        self.weapon_type = self.weapon_types[self.type]
        self.armor_type = self.armor_types[self.type]
        self.shield_type = self.shield_types[self.type]
        return True

    def place(self, castle, room_to_place = None):
        print (self.name)
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
            print ('Положена в мебель: ' + furniture.name)
            print('-' * 20)
            return True
        room.loot.add(self)
        print('Брошена в комнату')
        print('-'*20)

    def use(self, whoUsing, inaction = False):
        return True

    def __str__(self):
        return self.name

class Loot:
    def __init__(self, game):
        self.game = game
        self.pile = []

    def __str__(self):
        return 'loot'

    def __add__(self, other):
        self.pile += other.pile

    def add(self, obj):
        self.pile.append(obj)

    def remove(self, obj):
        self.pile.remove(obj)

class Furniture:
    def __init__(self, game, name=''):
        self.game = game
        newloot = Loot(self.game)
        self.ambush = False
        self.loot = newloot
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
        self.loot.add(item)

    def place(self, castle = None, room_to_place = None):
        print(self.name)
        if room_to_place:
            print(room_to_place.furniture_types(), self.type)
            if self.type not in room_to_place.furniture_types():
                room_to_place.furniture.append(self)
                return True
            else:
                print('Нет места')
                print('-' * 20)
                return False
        else:
            can_place = False
            while not can_place:
                room = randomitem(castle.plan, False)
                print('Пытаемся поставить')
                if self.type not in room.furniture_types():
                    can_place = True
        room.furniture.append(self)
        print ('Поставлен в комнату')
        if dice(1, 4) == 1 and self.lockable:
            self.locked = True
            veryNewKey = Key(self.game)
            veryNewKey.place(castle)
            print ('Заперт')
        if dice(1, 100) <= 50:
            newMoney = Money(self.game, dice(1, 50))
            self.loot.pile.append(newMoney)
            print ('Добавлены деньги', newMoney.howmuchmoney)
        print('-'*20)
        return True

class Money:
    def __init__(self, game, howmuchmoney):
        self.game = game
        self.howmuchmoney = howmuchmoney
        if 0 < self.howmuchmoney <= 10:
            self.name = 'Несколько монет'
            self.name1 = 'Несколько монет'
        elif 10 < self.howmuchmoney <= 20:
            self.name = 'Кучка монет'
            self.name1 = 'Кучку монет'
        elif 20 < self.howmuchmoney <= 30:
            self.name = 'Груда монет'
            self.name1 = 'Груду монет'
        elif 30 < self.howmuchmoney:
            self.name = 'Много монет'
            self.name1 = 'Много монет'

    def __str__(self):
        return self.name + ' (' + self.howmuchmoney + ')'

    def take(self, luckyOne):
        luckyOne.money.howmuchmoney += self.howmuchmoney
        tprint(self.game, luckyOne.name + ' забрал ' + howmany(self.howmuchmoney, 'монету,монеты,монет'))

    def show(self):
        if self.howmuchmoney > 0:
            return howmany(self.howmuchmoney, 'монету,монеты,монет')
        else:
            return 'Денег нет'

    def __add__(self, other):
        self.howmuchmoney += other.howmuchmoney


class Hero:
    def __init__(self, game, name, name1, gender, stren=10, dext=2, intel=0, health=20, weapon='', shield='', actions='бьет',
                 pockets=[]):
        self.game = game
        self.name = name
        self.name1 = name1
        self.gender = gender
        self.stren = int(stren)
        self.startStren = self.stren
        self.dext = int(dext)
        self.startDext = self.dext
        self.intel = int(intel)
        self.startIntel = self.intel
        self.health = int(health)
        self.actions = actions.split(',')
        self.weapon = weapon
        self.armor = ''
        self.shield = shield
        self.pockets = pockets
        self.money = Money(self.game, 0)
        self.currentPosition = 0
        self.gameOver = False
        self.startHealth = self.health
        self.wins = 0
        self.rage = 0
        self.hide = False
        self.run = False
        self.level = 1
        self.exp = 0
        self.levels = [0, 100, 200, 350, 500, 750, 1000, 1300, 1600, 2000, 2500, 3000]
        self.elements = {'огонь': 0, 'вода': 0, 'земля': 0, 'воздух': 0, 'магия': 0}
        self.elementLevels = {'1': 2, '2': 4, '3': 7, '4': 10}
        self.weapon_mastery = {'рубящее': 0, "колющее": 0, "ударное": 0}
        self.directionsDict = {0: (0 - self.game.newCastle.rooms),
                               1: 1,
                               2: self.game.newCastle.rooms,
                               3: (0 - 1),
                               'наверх': (0 - self.game.newCastle.rooms),
                               'направо': 1,
                               'вправо': 1,
                               'налево': (0 - 1),
                               'лево': (0 - 1),
                               'влево': (0 - 1),
                               'вниз': self.game.newCastle.rooms,
                               'низ': self.game.newCastle.rooms,
                               'вверх': (0 - self.game.newCastle.rooms),
                               'верх': (0 - self.game.newCastle.rooms),
                               'право': 1}
        self.doorsDict = {'наверх': 0,
                          'направо': 1,
                          'вправо': 1,
                          'право': 1,
                          'налево': 3,
                          'влево': 3,
                          'лево': 3,
                          'вниз': 2,
                          'низ': 2,
                          'вверх': 0,
                          'верх': 0}

    def __str__(self):
        return 'hero'

    def inpockets(self, itemType):
        itemList = []
        for item in self.pockets:
            if isinstance(item, itemType):
                itemList.append(item)
        return itemList

    def action(self):
        if self.weapon == '':
            return randomitem(self.actions)
        else:
            return randomitem(self.weapon.actions)

    def second_weapon(self):
        for i in self.pockets:
            if isinstance(i, Weapon):
                return i
        return False

    def run_away(self, target):
        game = self.game
        room = game.newCastle.plan[self.currentPosition]
        if room.light:
            tprint(game, self.name + ' сбегает с поля боя.')
        else:
            tprint(game, self.name + ' в кромешной тьме пытается убежать хоть куда-нибудь.')
        a = dice(1, 2)
        if a == 1 and self.weapon != '':
            tprint(game, 'Убегая ' + self.name + ' роняет из рук ' + self.weapon.name1)
            if target.weapon == '' and target.carryweapon:
                target.weapon = self.weapon
            else:
                room.loot.add(self.weapon)
            self.weapon = ''
        elif a == 2 and self.shield != '':
            tprint(game, 'Убегая ' + self.name + ' теряет ' + self.shield.name1)
            if target.shield == '' and target.carryshield:
                target.shield = self.shield
            else:
                room.loot.add(self.shield)
            self.shield = ''
        a = dice(0, len(self.pockets))
        if a > 0:
            firstLine = self.name + ' бежит настолько быстро, что не замечает, как теряет:'
            text = [firstLine]
            for i in range(a):
                b = dice(0, len(self.pockets) - 1)
                text.append(self.pockets[b].name1)
                room.loot.add(self.pockets[b])
                self.pockets.pop(b)
            tprint(game, text)
        availableDirections = []
        for i in range(4):
            if room.doors[i] == 1:
                availableDirections.append(i)
        if room.light:
            direction = availableDirections[dice(0,len(availableDirections)-1)]
        else:
            direction = dice(0, 3)
            if direction not in availableDirections:
                return False
        self.currentPosition += self.directionsDict[direction]
        room = game.newCastle.plan[self.currentPosition]
        room.visited = '+'
        game.IN_FIGHT = False
        self.lookaround()
        if room.center != '':
            if room.center.agressive and room.light:
                self.fight(room.center, True)
        return self.name + ' еле стоит на ногах.'

    def attack(self, target, action):
        game = self.game
        room = game.newCastle.plan[self.currentPosition]
        if room.light:
            targetName = target.name
            targetName1 = target.name1
            if self.rage > 1:
                rage = dice(2, self.rage)
            else:
                rage = 1
            meleAttack = dice(1, self.stren) * rage
        else:
            targetName = 'Неизвестная тварь из темноты'
            targetName1 = 'черт знает кого'
            rage = 1
            meleAttack = dice(1, self.stren) // dice (1, 3)
        self.run = False
        canUse = []
        for i in self.pockets:
            if i.canUseInFight:
                canUse.append(i)
        if action == '' or action == 'у' or action == 'ударить':
            tprint(game, showsides(self, target, game.newCastle))
            self.rage = 0
            if self.weapon != '':
                weaponAttack = self.weapon.attack()
                string1 = self.name + ' ' + self.action() + ' ' + targetName1 + ' используя ' + self.weapon.name + \
                          ' и наносит ' + str(meleAttack) + '+' + howmany(weaponAttack, 'единицу,единицы,единиц') + \
                          ' урона. '
            else:
                weaponAttack = 0
                string1 = self.name + ' бьет ' + targetName1 + ' не используя оружие и наносит ' + howmany(
                    meleAttack, 'единицу,единицы,единиц') + ' урона. '
            targetDefence = target.defence(self)
            if (weaponAttack + meleAttack - targetDefence) > 0:
                totalDamage = weaponAttack + meleAttack - targetDefence
            else:
                totalDamage = 0
            if totalDamage == 0:
               string2 = self.name + ' не смог пробить защиту ' + targetName1 + '.'
            elif targetDefence == 0:
               string2 = targetName + ' не имеет защиты и теряет ' + howmany(totalDamage, 'жизнь,жизни,жизней') + '.'
            else:
               string2 = targetName + ' использует для защиты ' + target.shield.name1 + ' и теряет ' + howmany(
                    totalDamage, 'жизнь,жизни,жизней') + '.'
            target.health -= totalDamage
            return string1 + string2
        elif action == 'з' or action == 'защититься' or action == 'защита':
            tprint(game, showsides(self, target, game.newCastle))
            self.hide = True
            self.rage += 1
            return (self.name + ' уходит в глухую защиту, терпит удары и накапливает ярость.')
        elif action == 'б' or action == 'бежать' or action == 'убежать':
            result = self.run_away(target)
            if not result:
                return self.name + ' с разбега врезается в стену и отлетает в сторону. Схватка продолжается.'
            else:
                return result
        elif (action == 'и' or action == 'использовать') and len(canUse) > 0:
            tprint(game, 'Во время боя ' + self.name + ' может использовать:')
            for i in self.pockets:
                if i.canUseInFight:
                    tprint(game, i.name)
            while True:
                a = input('Что нужно использовать?')
                if a == 'ничего' or a == '':
                    break
                else:
                    itemUsed = False
                    for i in canUse:
                        if i.name == a or i.name1 == a:
                            if i.use(self, inaction=True) and isinstance(i, Potion):
                                self.pockets.remove(i)
                            itemUsed = True
                            break
                    if itemUsed:
                        break
                    tprint(game, 'Что-то не выходит')
        elif (action == 'с' or action == 'сменить оружие' or action == 'сменить'):
            weapon = self.weapon
            spareWeapon = False
            for item in self.pockets:
                if isinstance(item, Weapon):
                    spareWeapon = item
            self.weapon = spareWeapon
            self.pockets.remove(spareWeapon)
            self.pockets.append(weapon)
            message = [self.name + ' меняет ' + weapon.name1 + ' на ' + spareWeapon.name1 + '.']
            tprint(game, message)
        return True

    def show(self):
        if self.weapon != '':
            string1 = ', а {0} в его руке добавляет к ней еще {1}+{2}.'.format(self.weapon.realname()[0],
                                                                               self.weapon.damage,
                                                                               self.weapon.permdamage())
        else:
            string1 = ' и он предпочитает сражаться голыми руками.'
        if self.shield != '':
            string2 = 'Его защищает {0} ({1}+{2})'.format(self.shield.realname()[0],
                                                           self.shield.protection,
                                                           self.shield.permprotection())
        else:
            string2 = 'У него нет защиты'
        tprint(self.game,
            '{0} - это смелый герой {7} уровня. Его сила - {1}{2} {3} и сейчас у него {4} здоровья, '
            'что составляет {5}% от максимально возможного.\n{0} имеет при себе {6} золотом.'.format(
                self.name, self.stren, string1, string2, howmany(self.health, 'единица,единицы,единиц'),
                self.health * 100 // self.startHealth, howmany(self.money.howmanymoney, 'монету,монеты,монет'),
                self.level))

    def defence(self, attacker):
        result = 0
        if self.shield != '':
            result += self.shield.protect(attacker)
        if self.armor != '':
            result += self.armor.protect(attacker)
        return result

    def lose(self, winner):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.currentPosition = 0

    def win(self, loser):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.wins += 1
        tprint(self.game, self.name + ' получает ' + howmany(loser.exp, 'единицу,единицы,единиц') + ' опыта!')
        self.exp += loser.exp
        if self.exp > self.levels[self.level]:
            self.levelup()

    def levelup(self):
        self.game.LEVEL_UP = True
        level_up_message = []
        level_up_message.append(self.name + ' получает новый уровень!')
        level_up_message.append('Что необходимо прокачать: здоровье, силу, ловкость или интеллект?')
        tprint(self.game, level_up_message, 'levelup')
        self.level += 1
        return True

    def gameover(self, goaltype, goal):
        if goaltype == 'killall':
            if self.game.newCastle.monsters() == 0:
                tprint(self.game, self.name + ' убил всех монстров в замке и выиграл в этой игре!')
                return True
            else:
                return False
        return False

    def lookaround(self, a=''):
        game = self.game
        newCastle = self.game.newCastle
        if a == '':
            newCastle.plan[self.currentPosition].show(game.player)
            newCastle.plan[self.currentPosition].map()
        elif a == 'себя':
            self.show()
        elif a == 'карманы':
            text = []
            text.append(self.name + ' осматривает свои карманы и обнаруживает в них:')
            for i in range(len(self.pockets)):
                text.append(str(i+1) + ': ' + self.pockets[i].show())
            text.append(self.money.show())
            tprint(game, text)
        elif a in self.directionsDict.keys():
            if newCastle.plan[self.currentPosition].doors[self.doorsDict[a]] == 0:
                tprint (game, self.name + ' осматривает стену и не находит ничего заслуживающего внимания.')
            else:
                tprint(game, self.name + ' заглядывает в замочную скважину и ' +
                       newCastle.plan[self.directionsDict[a]].showThroughKeyHole(self))

        if newCastle.plan[self.currentPosition].center != '':
            if (a == newCastle.plan[self.currentPosition].center.name or a == newCastle.plan[
                self.currentPosition].center.name1 or a == newCastle.plan[self.currentPosition].center.name[
                0]) and isinstance(newCastle.plan[self.currentPosition].center, Monster):
                tprint(game, showsides(self, newCastle.plan[self.currentPosition].center, newCastle))

        if self.weapon != '':
            if a == self.weapon.name or a == self.weapon.name1 or a == 'оружие':
                tprint(game, self.weapon.show())
        if self.shield != '':
            if a == self.shield.name or a == self.shield.name1 or a == 'защиту':
                tprint(game, self.shield.show())

        if len(self.pockets) > 0:
            text = []
            for i in self.pockets:
                if a == i.name or a == i.name1:
                    text.append(i.show())
            tprint(game, text)

    def go(self, direction):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if direction not in self.directionsDict.keys():
            tprint(game, self.name + ' не знает такого направления!')
            return False
        elif room.doors[self.doorsDict[direction]] == 0:
            if room.light:
                message = ['Там нет двери. ' + self.name + ' не может туда пройти!']
            else:
                message = ['В темноте ' + self.name + ' врезается во что-то носом.']
            tprint(game, message)
            return False
        elif room.doors[self.doorsDict[direction]] == 2:
            if room.light:
                message = ['Эта дверь заперта. ' + self.name + ' не может туда пройти, нужен ключ!']
            else:
                message = ['В темноте ' + self.name + ' врезается во что-то носом.']
            tprint(game, message)
            return False
        else:
            self.currentPosition += self.directionsDict[direction]
            room = newCastle.plan[self.currentPosition]
            room.visited = '+'
            room.show(self)
            room.map()
            if room.center != '':
                if room.center.agressive and room.light:
                    self.fight(room.center)
            return True

    def fight(self, enemy, agressive = False):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if isinstance(enemy, Monster):
            whoisfighting = enemy
        elif room.center != '':
            if not isinstance(room.center, Monster):
                tprint(game, 'Не нужно кипятиться. Тут некого атаковать')
                return False
            elif (room.center.name != enemy
                    and room.center.name1 != enemy
                    and room.center.name[0] != enemy) \
                    and enemy != '':
                tprint(game, self.name + ' не может атаковать. В комнате нет такого существа.')
                return False
            else:
                whoisfighting = room.center
        game.IN_FIGHT = True
        if agressive:
            whoFirst = 2
        else:
            whoFirst = dice(1, 2)
        if whoFirst == 1:
            tprint(game, game.player.name + ' начинает схватку!', 'fight')
            self.attack(whoisfighting, 'атаковать')
        else:
            if room.light:
                message = [whoisfighting.name + ' начинает схватку!']
            else:
                message = ['Что-то жуткое и непонятное нападает первым из темноты.']
            tprint(game, message, 'fight')
            tprint(game, whoisfighting.attack(self))
            return True

    def search(self, item=False):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        message = []
        print ('room.center: ', room.center)
        chestinroom = False
        enemyinroom = False
        if room.center != '':
            if isinstance(room.center, Monster):
                enemyinroom = room.center
        if room.ambush != '':
            enemyinambush = room.ambush
        else:
            enemyinambush = False
        if not room.light:
            message.append(['В комнате настолько темно, что невозможно что-то отыскать.'])
            tprint(game, message)
            return True
        if enemyinroom:
            message.append(enemyinroom.name + " мешает толком осмотреть комнату.")
            tprint(game, message)
            return True
        if enemyinambush and not item:
            room.center = enemyinambush
            room.ambush = ''
            enemyinambush = False
            enemyinroom = room.center
            message.append('Неожиданно из засады выскакивает ' + enemyinroom.name + ' и нападает на ' + self.name1)
            tprint (game, message)
            self.fight(enemyinroom, True)
            return True
        if not item:
            if chestinroom:
                message.append("В комнате стоит " + chestinroom.name)
            for furniture in room.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            if room.loot != '' and len(room.loot.pile) > 0:
                message.append('По всей комнате можно найти:')
                for i in room.loot.pile:
                    message.append(i.name)
            else:
                message.append('В комнате нет ничего интересного.')
            tprint(game, message)
            return True
        else:
            searchableItems = []
            searchableItems.extend(room.furniture)
            whatToSearch = False
            if chestinroom:
                searchableItems.append(chestinroom)
            for i in searchableItems:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    whatToSearch = i
            if not whatToSearch:
                message.append('В комнате нет такой вещи.')
            elif whatToSearch.locked:
                message.append('Нельзя обыскать ' + whatToSearch.name1 + '. Там заперто.')
            elif len(whatToSearch.loot.pile) > 0:
                message.append(self.name + ' осматривает ' + whatToSearch.name1 + ' и находит:')
                for i in whatToSearch.loot.pile:
                    message.append(i.name)
                    room.loot.pile.append(i)
                if len(whatToSearch.loot.pile) > 0:
                    message.append('Все эти вещи теперь лежат навиду.')
            elif len(whatToSearch.loot.pile) == 0:
                message.append(whatToSearch.name + ' ' + whatToSearch.empty)
            tprint(game, message)
            return True

    def can_take(self, object):
        classes = [Weapon, Shield, Armor]
        for i in classes:
            if isinstance(object, i):
                return False
        return True

    def take(self, item='все'):
        game = self.game
        newCastle = self.game.newCastle
        currentLoot = newCastle.plan[self.currentPosition].loot
        if currentLoot == '':
            tprint(game, 'Здесь нечего брать.')
            return False
        elif item == 'все' or item == 'всё' or item == '':
            for i in currentLoot.pile:
                if self.can_take(i):
                    i.take(self)
                    currentLoot.pile.remove(i)
            return True
        else:
            for i in currentLoot.pile:
                if i.name.lower() == item or i.name1.lower() == item:
                    i.take(self)
                    currentLoot.pile.remove(i)
                    return True
        tprint(game, 'Такой вещи здесь нет.')
        return False

    def drop(self, object):
        game = self.game
        newCastle = self.game.newCastle
        currentLoot = newCastle.plan[self.currentPosition].loot
        currentLoot.pile.append(object)
        if self.armor == object:
            self.armor = ''
        if self.shield == object:
            self.shield = ''
        if self.weapon == object:
            self.weapon = ''
        if object in self.pockets:
            self.pockets.remove(object)

    def open(self, item=''):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        key = False
        for i in self.pockets:
            if isinstance(i, Key):
                key = i
        if not key:
            message = ['Чтобы что-то открыть нужен хотя бы один ключ.']
            tprint(game, message)
            return False
        whatIsInRoom = []
        if len(room.furniture) > 0:
            for furniture in room.furniture:
                if furniture.locked:
                    whatIsInRoom.append(furniture)
        print (whatIsInRoom)
        print ('item: ', item)
        if item == '' or (not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0):
            if len(whatIsInRoom) == 0:
                if room.light:
                    message = ['В комнате нет вещей, которые можно открыть.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return False
            elif item == '' and len(whatIsInRoom) > 1:
                if room.light:
                    message = ['В комнате слишком много запертых вещей. ' +
                               self.name +
                               ' не понимает, что ему нужно открыть.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return False
            elif item != '':
                if room.light:
                    for furniture in whatIsInRoom:
                        if furniture.name.lower() == item.lower() or furniture.name1.lower() == item.lower():
                            self.pockets.remove(key)
                            furniture.locked = False
                            message = [self.name + ' отпирает ' + furniture.name1 + ' ключом.']
                            tprint(game, message)
                            return True
                    message = [self.name + ' не находит в комнате такой вещи. Отпирать нечего.']
                    tprint(game, message)
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return True
            else:
                if room.light:
                    self.pockets.remove(key)
                    whatIsInRoom[0].locked = False
                    message = [self.name + ' отпирает ' + whatIsInRoom[0].name1 + ' ключом.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return True
        else:
            if not room.light:
                message = [self.name + ' ничего не видит и не может нащупать замочную скважину.']
                tprint (game, message)
                return False
            if not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0:
                tprint(game, self.name + ' не может это открыть.')
                return False
            elif newCastle.plan[self.currentPosition].doors[self.doorsDict[item]] != 2:
                tprint(game, 'В той стороне нечего открывать.')
                return False
            else:
                self.pockets.remove(key)
                room.doors[self.doorsDict[item]] = 1
                j = self.doorsDict[item] + 2 if (self.doorsDict[item] + 2) < 4 else self.doorsDict[item] - 2
                newCastle.plan[self.currentPosition + self.directionsDict[item]].doors[j] = 1
                tprint(game, self.name + ' открывает дверь.')

    def use(self, item='', infight=False):
        game = self.game
        newCastle = self.game.newCastle
        if item == '':
            tprint(game, self.name + ' не понимает, что ему надо использовать.')
        elif item.isdigit():
            if int(item)-1 < len(self.pockets):
                i = self.pockets[int(item)-1]
                if isinstance(i, Potion) and i.use(self, False):
                    self.pockets.remove(i)
                elif not isinstance(i, Potion):
                    i.use(self, False)
                return True
            else:
                tprint(game, self.name + ' не нашел такой вещи у себя в карманах.')
                return False
        else:
            for i in self.pockets:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    if isinstance(i, Potion)  and i.use(self, inaction = False):
                        self.pockets.remove(i)
                    else:
                        i.use(self, inaction = False)
                    return True
            tprint(game, self.name + ' не нашел такой вещи у себя в карманах.')

    def enchant(self, item=''):
        game = self.game
        newCastle = self.game.newCastle
        runeList = self.inpockets(Rune)
        if len(runeList) == 0:
            tprint(game, self.name + 'не может ничего улучшать. В карманах не нашлось ни одной руны.')
            return False
        if item == '':
            tprint(game, self.name + ' не понимает, что ему надо улучшить.')
            return False
        elif item == 'оружие' and self.weapon != '':
            game.selectedItem = self.weapon
        elif item in ['защиту', 'защита'] and self.shield != '':
            game.selectedItem = self.shield
        elif item.isdigit() and int(item)-1 <= len(self.pockets):
            game.selectedItem = self.pockets[int(item)-1]
        else:
            for i in self.pockets:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    game.selectedItem = i
                else:
                    tprint(game, self.name + ' не нашел такой вещи у себя в карманах.')
                    return False
        if game.selectedItem != '' and isinstance(game.selectedItem, Weapon) or isinstance(game.selectedItem, Shield):
            text = []
            text.append(self.name + ' может использовать следующие руны:')
            for rune in runeList:
                text.append(str(runeList.index(rune)+1) + ': ' + str(rune))
            text.append('Введите номер руны или "отмена" для прекращения улучшения')
            #Здесь нужна доработка т.к. управление переходит на работу с рунами
            game.ENCHANTING = True
            tprint(game, text, 'enchant')
        else:
            tprint(game, self.name + ' не может улучшить эту вещь.')
            return False

    def do(self, command):
        commandDict = {'осмотреть': self.lookaround,
                       'идти': self.go,
                       'атаковать': self.fight,
                       'взять': self.take,
                       'обыскать': self.search,
                       'открыть': self.open,
                       'использовать': self.use,
                       'улучшить': self.enchant}
        a = command.find(' ')
        fullCommand = []
        if a < 0:
            a = len(command)
        fullCommand.append(command[:a])
        fullCommand.append(command[a + 1:])
        if fullCommand[0] == '?':
            text = []
            text.append(self.name + " может:")
            for i in commandDict.keys():
                text.append(i)
            tprint(self.game, text)
            return True
        c = commandDict.get(fullCommand[0], False)
        if not c:
            tprint(self.game, 'Такого ' + self.name + ' не умеет!')
        elif len(fullCommand) == 1:
            c()
        else:
            c(fullCommand[1])


class Monster:
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=False,
                 carryweapon=True, carryshield=True, wearArmor=True):
        self.game = game
        self.name = name
        self.name1 = name1
        self.stren = int(stren)
        self.health = int(health)
        self.actions = actions.split(',')
        self.state = state
        self.weapon = ''
        self.shield = ''
        self.armor = ''
        self.money = 5
        self.currentPosition = 0
        self.startHealth = self.health
        self.loot = Loot(self.game)
        self.hide = False
        self.run = False
        self.wounded = False
        self.keyHole = 'видит какую-то неясную фигуру.'
        if carryweapon == 'False':
            self.carryweapon = False
        else:
            self.carryweapon = True
        if wearArmor == 'False':
            self.wearArmor = False
        else:
            self.wearArmor = True
        if carryshield == 'False':
            self.carryshield = False
        else:
            self.carryshield = True
        if agressive == 'True':
            self.agressive = True
        else:
            self.agressive = False
        self.exp = self.stren * dice(1, 10) + dice(1, self.health)

    def on_create(self):
        return True

    def __str__(self):
        return self.name

    def give(self, item):
        if isinstance(item, Weapon) and self.weapon == '' and self.carryweapon:
            self.weapon = item
        elif isinstance(item, Shield) and self.shield == '' and self.carryshield:
            self.shield = item
        elif isinstance(item, Armor) and self.armor == '' and self.wearArmor:
            self.armor = item
        elif isinstance(item, Rune):
            if item.damage >= item.defence:
                if self.weapon != '':
                    if self.weapon.enchant(item):
                        return True
                if self.armor != '':
                    if self.armor.enchant(item):
                        return True
                if self.shield != '':
                    if self.shield.enchant(item):
                        return True
                self.loot.add(item)
                return True
            else:
                if self.shield != '':
                    if self.shield.enchant(item):
                        return True
                if self.armor != '':
                    if self.armor.enchant(item):
                        return True
                if self.weapon != '':
                    if not self.weapon.enchant(item):
                        return True
                self.loot.add(item)
                return True
        else:
            self.loot.add(item)

    def action(self):
        if self.weapon == '':
            return randomitem(self.actions)
        else:
            return randomitem(self.weapon.actions)

    def mele(self):
        room = self.game.newCastle.plan[self.currentPosition]
        if room.light:
            return dice(1, self.stren)
        else:
            return dice(1, self.stren) // dice(1, 3)

    def attack(self, target):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if room.light:
            selfName = self.name
            selfName1 = self.name1
        else:
            selfName = 'Кто-то страшный'
            selfName1 = 'черт знает кого'
        text = []
        meleAttack = self.mele()
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            text.append(selfName + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name1 \
                      + ' и наносит ' + str(meleAttack) + '+' \
                      + howmany(weaponAttack, 'единицу,единицы,единиц') + ' урона. ')
        else:
            weaponAttack = 0
            text.append(selfName + ' бьет ' + target.name1 + ' не используя оружия и наносит ' + howmany(
                meleAttack, 'единицу,единицы,единиц') + ' урона. ')
        targetDefence = target.defence(self)
        if (weaponAttack + meleAttack - targetDefence) > 0:
            totalDamage = weaponAttack + meleAttack - targetDefence
            if targetDefence == 0:
                text.append(target.name + ' беззащитен и теряет ' + howmany(totalDamage, 'жизнь,жизни,жизней') + '.')
            else:
                text.append(target.name + ' использует для защиты ' + target.shield.name + ' и теряет ' \
                          + howmany(totalDamage, 'жизнь,жизни,жизней') + '.')
        else:
            totalDamage = 0
            text.append(selfName + ' не смог пробить защиту ' + target.name1 + '.')
        target.health -= totalDamage
        if target.health <= 0:
            game.IN_FIGHT = False
            target.lose(self)
            text.append(target.name + ' терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(game, text, 'off')
        else:
            tprint(game, text)
        return True

    def defence(self, attacker):
        if self.shield == '':
            return 0
        else:
            return self.shield.protect(attacker)

    def lose(self, winner):
        game = self.game
        newCastle = self.game.newCastle
        result = dice(1, 10)
        where = newCastle.plan[self.currentPosition]
        if where.loot == '':
            b = Loot()
            where.loot = b
        if result < 6 or self.wounded:
            if self.money > 0:
                a = Money(self.money)
                where.loot.add(a)
                where.loot.pile += (self.loot.pile)
            if self.shield != '':
                where.loot.add(self.shield)
            if self.weapon != '':
                where.loot.add(self.weapon)
            where.center = ''
        else:
            self.wounded = True
            aliveString = self.name + ' остается вживых и '
            weaknessAmount = ceil(self.stren * 0.4)
            illAmount = ceil(self.startHealth * 0.4)
            if result < 10:
                if result == 6:
                    aliveString += 'получает легкое ранение в руку. '
                    if self.weapon != '':
                        aliveString += 'На пол падает ' + self.weapon.name + '. '
                        where.loot.add(self.weapon)
                        self.weapon = ''
                    elif self.shield != '':
                        aliveString += 'На пол падает ' + self.shield.neme + '. '
                        where.loot.add(self.shield)
                        self.shield = ''
                elif result == 7:
                    aliveString += 'истекает кровью, теряя при этом ' \
                                   + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы. '
                    self.stren -= weaknessAmount
                    self.health = self.startHealth
                elif result == 8:
                    aliveString += 'приходит в ярость, получая при этом ' \
                                   + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и теряя ' \
                                   + howmany(illAmount, 'жизнь,жизни,жизней') + '. '
                    self.stren += weaknessAmount
                    self.health = self.startHealth - illAmount
                else:
                    aliveString += 'получает контузию, теряя при этом ' \
                                   + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и получая ' \
                                   + howmany(illAmount, 'жизнь,жизни,жизней') + '. '
                    self.stren -= weaknessAmount
                    self.health = self.startHealth + illAmount
                runningMonsters = [self]
                if newCastle.inhabit(runningMonsters, 1, True):
                    aliveString += self.name + ' убегает из комнаты.'
                    tprint(game, aliveString)
                    where.center = ''
            else:
                aliveString += 'получает ранение в ногу и не может двигаться, теряя при этом '  \
                               + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и ' \
                               + howmany(illAmount, 'жизнь,жизни,жизней') + '.'
                self.stren -= weaknessAmount
                self.health = self.startHealth - illAmount
                tprint(game, aliveString)

    def win(self, loser):
        self.health = self.startHealth

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.center == '' and a.ambush == '')]
            room = randomitem(emptyRooms, False)
        if dice(1, 5) == 1:
            places_to_hide = []
            for i in room.furniture:
                if i.can_hide:
                    places_to_hide.append(i)
            places_to_hide.append(room)
            where_to_hide = randomitem(places_to_hide, False)
            print ('Прячется в ', where_to_hide)
            where_to_hide.ambush = self  # Монстр садится в засаду
        else:
            print('Встает в комнату')
            room.center = self
        self.currentPosition = room.position


class Plant(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='растёт', agressive=False,
                 carryweapon=False, carryshield=False):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.carryshield = False
        self.carryweapon = False
        self.wearArmor = False
        self.agressive = False

    def grow(self):
        newPlant = Plant(self.name, self.name1, self.stren, self.health, 'бьет', 'растет', False, False, False)
        return newPlant

    def win(self, loser):
        game = self.game
        newCastle = self.game.newCastle
        self.health = self.startHealth
        for i in range(4):
            if newCastle.plan[self.currentPosition].doors[i] == 1:
                if i == 0 and newCastle.plan[self.currentPosition - newCastle.rooms].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition - newCastle.rooms].center = copy
                    copy.currentPosition = self.currentPosition - newCastle.rooms
                elif i == 1 and newCastle.plan[self.currentPosition + 1].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition + 1].center = copy
                    copy.currentPosition = self.currentPosition + 1
                elif i == 2 and newCastle.plan[self.currentPosition + newCastle.rooms].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition + newCastle.rooms].center = copy
                    copy.currentPosition = self.currentPosition + newCastle.rooms
                elif i == 3 and newCastle.plan[self.currentPosition - 1].center == '':
                    copy = self.grow()
                    newCastle.plan[self.currentPosition - 1].center = copy
                    copy.currentPosition = self.currentPosition - 1

    def lose(self, winner):
        game = self.game
        newCastle = self.game.newCastle
        where = newCastle.plan[self.currentPosition]
        if where.loot == '':
            b = Loot()
            where.loot = b
        if self.money > 0:
            a = Money(self.money)
            where.loot.add(a)
            where.loot.pile += (self.loot.pile)
        if self.shield != '':
            where.loot.add(self.shield)
        if self.weapon != '':
            where.loot.add(self.weapon)
        where.center = ''

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.center == '' and a.ambush == '')]
            room = randomitem(emptyRooms, False)
        print('Встает в комнату')
        room.center = self
        self.currentPosition = room.position

class Walker(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=True, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)

class Berserk(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=True, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.agressive = True
        self.carryshield = False
        self.rage = 0
        self.base_health = health

    def mele(self):
        self.rage = (int(self.base_health) - int(self.health)) // 3
        return dice(1, (self.stren + self.rage))

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.center == '' and a.ambush == '')]
            room = randomitem(emptyRooms, False)
        print('Встает в комнату')
        room.center = self
        self.currentPosition = room.position

class Shapeshifter(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=False, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.shifted = False
        self.agressive = True

    def defence(self, attacker):
        if not self.shifted:
            self.shifted = True
            self.stren = attacker.stren
            if attacker.weapon != '' and self.weapon == '':
                self.weapon = attacker.weapon
                weaponString = ' и ' + self.weapon.name + ' в руках.'
            else:
                weaponString = ''
            tprint(self.game, self.name +
                   ' меняет форму и становится точь в точь как ' +
                   attacker.name +
                   '. У него теперь сила ' +
                   str(self.stren) +
                   weaponString)
        if self.shield == '':
            return 0
        else:
            return self.shield.protect(attacker)

    def lose(self, winner):
        where = self.game.newCastle.plan[self.currentPosition]
        if where.loot == '':
            b = Loot()
            where.loot = b
        if self.money > 0:
            a = Money(self.money)
            where.loot.add(a)
            where.loot.pile += (self.loot.pile)
        if self.shield != '':
            where.loot.add(self.shield)
        where.center = ''


class Vampire(Monster):
    def __init__(self, game, name='', name1='', stren=10, health=20, actions='бьет', state='стоит', agressive=False,
                 carryweapon=True, carryshield=True):
        super().__init__(game, name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)

    def attack(self, target):
        game = self.game
        newCastle = self.game.newCastle
        room = newCastle.plan[self.currentPosition]
        if room.light:
            selfName = self.name
            selfName1 = self.name1
        else:
            selfName = 'Кто-то страшный'
            selfName1 = 'черт знает кого'
        text = []
        meleAttack = self.mele()
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            text.append(selfName +
                        ' ' +
                        self.action() +
                        ' ' +
                        target.name1 +
                        ' используя ' +
                        self.weapon.name +
                        ' и наносит ' +
                        str(meleAttack) +
                        '+' +
                        str(weaponAttack) +
                        ' единиц урона. ')
        else:
            weaponAttack = 0
            text.append(selfName +
                        ' ' +
                        self.action() +
                        ' ' +
                        target.name1 +
                        ' не используя оружия и наносит ' +
                        howmany(meleAttack, 'единицу,единицы,единиц') +
                        ' урона. ')
        targetDefence = target.defence(self)
        if (weaponAttack + meleAttack - targetDefence) > 0:
            totalDamage = weaponAttack + meleAttack - targetDefence
        else:
            totalDamage = 0
        if totalDamage == 0:
            text.append(selfName + ' не смог пробить защиту ' + target.name1 + '.')
        elif targetDefence == 0:
            text.append(target.name + ' беззащитен и теряет ' +
                        howmany(totalDamage, 'жизнь,жизни,жизней') +
                        '. ' +
                        selfName +
                        ' высасывает ' +
                        str(totalDamage // 2) +
                        ' себе.')
        else:
            text.append(target.name +
                        ' использует для защиты ' +
                        target.shield.name +
                        ' и теряет ' +
                        howmany(totalDamage, 'жизнь,жизни,жизней') +
                        '.' +
                        selfName +
                        ' высасывает ' +
                        str(totalDamage // 2) +
                        ' себе.')
        target.health -= totalDamage
        self.health += totalDamage // 2
        if target.health <= 0:
            game.IN_FIGHT = False
            target.lose(self)
            text.append(target.name + ' терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(game, text, 'off')
        else:
            tprint(game, text)
        return True

    def place(self, castle, roomr_to_place = None):
        if roomr_to_place:
            room = roomr_to_place
        else:
            emptyRooms = [a for a in castle.plan if (a.ambush == '' and not a.light)]
            room = randomitem(emptyRooms, False)
        places_to_hide = []
        for i in room.furniture:
            if i.can_hide:
                places_to_hide.append(i)
        places_to_hide.append(room)
        where_to_hide = randomitem(places_to_hide, False)
        print ('Прячется в ', where_to_hide)
        where_to_hide.ambush = self  # Монстр садится в засаду
        self.currentPosition = room.position
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
        self.center = center
        self.money = 0
        self.loot = loot
        self.locked = False
        self.position = -1
        self.visited = ' '
        self.ambush = ''
        self.runePlace = ''
        self.light = True
        self.furniture = []
        self.torchDice = dice(1, 5)
        if not self.light or self.torchDice != 4:
            self.torch = False
        else:
            self.torch = True

    def show(self, player):
        game = self.game
        if self.light:
            if self.torch:
                self.decoration1 = 'освещенную факелом ' + self.decoration1
            if self.center == '':
                whoIsHere = 'Не видно ничего интересного.'
            else:
                whoIsHere = self.decoration3 + ' ' + self.center.state + ' ' + self.center.name + '.'
            message = []
            message.append(player.name + ' попадает в {0} комнату {1}. {2}'.format(self.decoration1,
                                                                          self.decoration2,
                                                                          self.decoration4))
            for furniture in self.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            message.append(whoIsHere)
            tprint(game, message, state = 'direction')
        else:
            message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
            if isinstance(self.center, Monster):
                message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
            tprint(game, message, state = 'direction')

    def showThroughKeyHole(self, who):
        if self.center == '':
            return 'не может ничего толком разглядеть.'
        else:
            return self.center.keyHole

    def furniture_types(self):
        types = []
        for furniture in self.furniture:
            if furniture.type not in types:
                types.append(furniture.type)
        return types

    def map(self):
        game=self.game
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '║', '1': ' ', '2': '|'}
        string1 = '=={0}=='.format(doorsHorizontal[str(self.doors[0])])
        string2 = '║   ║'
        string3 = '{0} '.format(doorsVertical[str(self.doors[3])])
        if self.center != '':
            string3 += self.center.name[0]
        else:
            string3 += ' '
        string3 += ' {0}'.format(doorsVertical[str(self.doors[1])])
        string4 = '=={0}=='.format(doorsHorizontal[str(self.doors[2])])
        if self.light:
            pprint(game, string1 + '\n' + string2 + '\n' + string3 + '\n' + string2 + '\n' + string4, 100, 120)
            return True
        else:
            return False

    def lock(self, lockOrNot=2):
        game=self.game
        a = [-game.newCastle.rooms, 1, game.newCastle.rooms, -1]
        for i in range(4):
            if self.doors[i] == 1:
                self.doors[i] = lockOrNot
                j = i + 2 if (i + 2) < 4 else i - 2
                game.newCastle.plan[self.position + a[i]].doors[j] = lockOrNot
        self.locked = True
        return None


class Castle:
    def __init__(self, game, floors=5, rooms=5):
        self.game = game
        self.floors = floors
        self.rooms = rooms
        f = self.floors
        r = self.rooms
        self.allRooms = [2] * r
        if f > 2: self.allRooms += ([2] + [3] * (r - 2) + [2]) * (f - 2)
        if f > 1: self.allRooms += [2] * r
        self.allDoors = []
        for j in range(f * r):
            self.allDoors.append([0, 0, 0, 0])
        for i in range(f * r):
            floor = i // r
            room = i % r
            if f > 1 and r > 1:
                while self.allDoors[i].count(1) < self.allRooms[i]:
                    q = dice(0, 3)
                    if self.allDoors[i][q] != 1:
                        if q == 0 and floor != 0:
                            self.allDoors[i][0] = 1
                            self.allDoors[i - r][2] = 1
                        elif q == 2 and floor < f - 1:
                            self.allDoors[i][2] = 1
                            self.allDoors[i + r][0] = 1
                        elif q == 3 and room != 0:
                            self.allDoors[i][3] = 1
                            self.allDoors[i - 1][1] = 1
                        elif q == 1 and room < r - 1:
                            self.allDoors[i][1] = 1
                            self.allDoors[i + 1][3] = 1
        self.plan = []
        for i in range(f * r):
            newLoot = Loot(self.game)
            a = Room(self.game, self.allDoors[i], '', newLoot)
            a.position = i
            self.plan.append(a)
        self.lights_off() #Выключаем свет в некоторых комнатах

    def lights_off(self):
        self.how_many_dark_rooms = len(self.plan) // 8
        darkRooms = randomitem(self.plan, False, self.how_many_dark_rooms)
        for room in darkRooms:
            room.light = False

    def lockDoors(self):
        howManyLockedRooms = len(self.plan) // 8
        for i in range(howManyLockedRooms):
            while True:
                a = randomitem(self.plan)
                if a != self.plan[0]:
                    newMoney = Money(self.game, dice(25, 75))
                    a.lock(2)
                    if a.center == '':
                        a.loot.pile.append(newMoney)
                    else:
                        a.center.loot.pile.append(newMoney)
                    newKey = Key(self.game)
                    newKey.place(self)
                    break
        return True

    def map(self):
        f = self.floors
        r = self.rooms
        game = self.game
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '║', '1': ' ', '2': '|'}
        text = []
        text.append('======' * r + '=')
        for i in range(f):
            text.append('║' + '     ║' * r)
            line1 = '║'
            line2 = ''
            for j in range(r):
                a = game.player.name[0] if game.player.currentPosition == i * r + j else self.plan[i*r+j].visited
                line1 += '  {0}  {1}'.format(a, doorsVertical[str(self.allDoors[i * r + j][1])])
                line2 += '==={0}=='.format(doorsHorizontal[str(self.allDoors[i * r + j][2])])
            text.append(line1)
            text.append('║' + '     ║' * r)
            text.append(line2 + '=')
        pprint(game, text, r*72, f*90)

    def monsters(self): #Возвращает количество живых монстров, обитающих в замке в данный момент
        roomsWithMonsters = [a for a in self.plan if ((a.center != '' and isinstance(a.center, Monster))
                                                      or (a.ambush != '' and isinstance(a.ambush, Monster)))]
        return len(roomsWithMonsters)

class Game():
    def __init__(self, chat_id, howMany=0, hero=None):
        self.IN_FIGHT = False  # Константа, отвечающая за то, что сейчас бой
        self.LEVEL_UP = False  # Константа, отвечающая за то, что сейчас происходит прокачка
        self.ENCHANTING = False  # Константа, отвечающая за то, что сейчас происходит улучшение шмотки
        self.selectedItem = ''
        self.gameIsOn = False
        self.chat_id = chat_id
        self.newCastle = Castle(self, 5, 5)  # Генерируем замок
        if howMany == 0:
            self.howMany = {'монстры': 10,
                       'оружие': 10,
                       'щит': 5,
                       'доспех': 5,
                       'зелье': 10,
                       'мебель': 10,
                       'книга': 5,
                       'руна': 10}  # Количество всяких штук, которые разбрасываются по замку
        else:
            self.howMany = howMany
        if not hero:
            self.player = Hero(self, 'Артур', 'Артура', 'male', 10, 2, 1, 25, '', '',
                                'бьет,калечит,терзает,протыкает')  # Создаем персонажа
        else:
            self.player = hero
        # Создаем мебель и разбрасываем по замку
        self.allFurniture = self.readobjects(file='furniture.json',
                                        howmany=self.howMany['мебель'],
                                        random=True)
        for furniture in self.allFurniture:
            furniture.place(castle=self.newCastle)
        # Читаем монстров из файла и разбрасываем по замку
        self.allMonsters = self.readobjects(file='monsters.json',
                                       howmany=self.howMany['монстры'])
        for monster in self.allMonsters:
            monster.place(self.newCastle)
        # Читаем оружие из файла и разбрасываем по замку
        self.allWeapon = self.readobjects(file='weapon.json',
                                     howmany=self.howMany['оружие'],
                                     object_class=Weapon)
        for weapon in self.allWeapon:
            weapon.place(self.newCastle)
        # Читаем щиты из файла и разбрасываем по замку
        self.allShields = self.readobjects(file='shields.json',
                                      howmany=self.howMany['щит'],
                                      object_class=Shield)
        for shield in self.allShields:
            shield.place(self.newCastle)
        # Читаем доспехи из файла и разбрасываем по замку
        self.allArmor = self.readobjects(file='armor.json',
                                    howmany=self.howMany['доспех'],
                                    object_class=Armor)
        for armor in self.allArmor:
            armor.place(self.newCastle)
        # Читаем зелья из файла и разбрасываем по замку
        self.allPotions = self.readobjects(file='potions.json',
                                      howmany=self.howMany['зелье'],
                                      object_class=Potion)
        for potion in self.allPotions:
            potion.place(self.newCastle)
        # Создаем руны и разбрасываем по замку
        self.allRunes = [Rune(self) for i in range(self.howMany['руна'])]
        for rune in self.allRunes:
            rune.place(self.newCastle)
        # Создаем книги и разбрасываем по замку
        self.allBooks = self.readobjects(file='books.json',
                                    howmany=self.howMany['книга'],
                                    random=True,
                                    object_class=Book)
        for book in self.allBooks:
            book.place(self.newCastle)
        self.newCastle.lockDoors()  # Создаем запертые комнаты
        map = Map(self)
        map.place(self.newCastle)  # Создаем и прячем карту
        matches = Matches(self)
        matches.place(self.newCastle)  # Создаем и прячем спички
        self.newCastle.plan[0].visited = '+'  # Делаем первую комнату посещенной
        newKey = Key(self)  # Создаем ключ
        self.player.pockets.append(newKey)  # Отдаем ключ игроку
        self.gameIsOn = False  # Выключаем игру для того, чтобы игрок запустил ее в Телеграме

    def __del__ (self):
        print("="*40)
        print('Игра удалена')
        print("=" * 40)

    def readobjects(self, file=None, howmany=None, object_class=None, random=False):
        objects = []
        if file:
            with open(file, encoding='utf-8') as read_data:
                parsed_data = json.load(read_data)
            if not random:
                for i in parsed_data:
                    object = classes[i['class']](self)
                    for param in i:
                        vars(object)[param] = i[param]
                    object.on_create()
                    objects.append(object)
            else:
                for n in range(howmany):
                    i = randomitem(parsed_data, False)
                    object = classes[i['class']](self)
                    for param in i:
                        vars(object)[param] = i[param]
                    object.on_create()
                    objects.append(object)
        if howmany:
            while len(objects) > howmany:
                spareObject = randomitem(objects, False)
                objects.remove(spareObject)
            if object_class:
                while len(objects) < howmany:
                    newObject = object_class(0)
                    objects.append(newObject)
        return objects


# Еще константы
classes = { 'монстр': Monster,
            'герой': Hero,
            'оружие': Weapon,
            'защита': Protection,
            'щит': Shield,
            'доспех': Armor,
            'притворщик': Shapeshifter,
            'мебель': Furniture,
            'вампир': Vampire,
            'берсерк': Berserk,
            'ходок': Walker,
            'растение': Plant,
            'ключ': Key,
            'карта': Map,
            'спички': Matches,
            'книга': Book,
            'зелье': Potion,
            'руна': Rune,
            'заклинание': Spell,
            }

# Функция чтения данных из JSON. Принимает на вход имя файла.
# Читает данные из файла, создает объекты класса, указанного в JSON в параметре class.
# Наполняет созданный объект значениями параметров из JSON. для каждого объекта выполняется его функция on_create().
# Если передан howmany, функция всячески старается вернуть список такой длины. Если объектов больше,
# случайные объекты выкидываются из списка.
# Если передан object_class и получается слишком коротки список,
# то в него добавляются случайные объекты переданного класса.
# Отдает список полученных объектов
# def readobjects(game, file = None, howmany = None, object_class = None, random = False):
#     objects = []
#     if file:
#         with open(file, encoding='utf-8') as read_data:
#             parsed_data = json.load(read_data)
#         if not random:
#             for i in parsed_data:
#                 object = classes[i['class']](game)
#                 for param in i:
#                     vars(object)[param] = i[param]
#                 object.on_create()
#                 objects.append(object)
#         else:
#             for n in range(howmany):
#                 i = randomitem(parsed_data, False)
#                 object = classes[i['class']](game)
#                 for param in i:
#                     vars(object)[param] = i[param]
#                 object.on_create()
#                 objects.append(object)
#     if howmany:
#         while len(objects) > howmany:
#             spareObject = randomitem(objects, False)
#             objects.remove(spareObject)
#         if object_class:
#             while len(objects) < howmany:
#                 newObject = object_class(0)
#                 objects.append(newObject)
#     return objects

# # Подготовка
# newCastle = Castle(5, 5)  # Генерируем замок
# # Создаем мебель и разбрасываем по замку
# allFurniture = readobjects(file='furniture.json', howmany=howMany['мебель'], random=True)
# for furniture in allFurniture:
#     furniture.place(castle=newCastle)
# # Читаем монстров из файла и разбрасываем по замку
# allMonsters = readobjects(file='monsters.json', howmany=howMany['монстры'])
# for monster in allMonsters:
#     print(monster.name, monster.agressive)
#     print('-'*20)
#     monster.place(newCastle)
# # Читаем оружие из файла и разбрасываем по замку
# allWeapon = readobjects(file='weapon.json', howmany=howMany['оружие'], object_class=Weapon)
# for weapon in allWeapon:
#     weapon.place(newCastle)
# # Читаем щиты из файла и разбрасываем по замку
# allShields = readobjects(file='shields.json', howmany=howMany['щит'], object_class=Shield)
# for shield in allShields:
#     shield.place(newCastle)
# # Читаем доспехи из файла и разбрасываем по замку
# allArmor = readobjects(file='armor.json', howmany=howMany['доспех'], object_class=Armor)
# for armor in allArmor:
#     armor.place(newCastle)
# # Читаем зелья из файла и разбрасываем по замку
# allPotions = readobjects(file='potions.json', howmany=howMany['зелье'], object_class=Potion)
# for potion in allPotions:
#     potion.place(newCastle)
# # Создаем руны и разбрасываем по замку
# allRunes = [Rune() for i in range(howMany['руна'])]
# for rune in allRunes:
#     rune.place(newCastle)
# # Создаем книги и разбрасываем по замку
# allBooks = readobjects(file='books.json', howmany=howMany['книга'], random=True, object_class=Book)
# for book in allBooks:
#     book.place(newCastle)
# newCastle.lockDoors() # Создаем запертые комнаты
# map = Map()
# map.place(newCastle) # Создаем и прячем карту
# matches = Matches()
# matches.place(newCastle) # Создаем и прячем спички
#
# newCastle.plan[0].visited = '+' # Делаем первую комнату посещенной
# player = Hero('Артур', 'Артура', 'male', 10, 2, 1, 25, '', '', 'бьет,калечит,терзает,протыкает') # Создаем персонажа
# newKey = Key() # Создаем ключ
# player.pockets.append(newKey) # Отдаем ключ игроку
# gameIsOn = False # Выключаем игру для того, чтобы игрок запустил ее в Телеграме
# shield1 = Shield('Простой щит')
# print (shield1.name, shield1.protection, shield1.permprotection())
# shield2 = Shield('Непростой щит')
# newCastle.plan[0].loot.pile.append(shield1)
# newCastle.plan[0].loot.pile.append(shield2)
# sword1 = Weapon(0)
# print (sword1.name, sword1.name1)
# sword2 = Weapon(0)
# print (sword2.name, sword2.name1)
# sword3 = Weapon(0)
# print (sword3.name, sword3.name1)
# newCastle.plan[0].loot.pile.append(sword1)
# newCastle.plan[0].loot.pile.append(sword2)
# newCastle.plan[0].loot.pile.append(sword3)

# Основная программа

# Запускаем бота
bot = telebot.TeleBot(TOKEN)
IN_FIGHT = False
#Функции бота

def tprint (game, text, state=''):
    global bot
    global chat_id
    if state == 'off':
        markup = types.ReplyKeyboardRemove(selective=False)
    elif state == 'fight':
        canUse = []
        for i in game.player.pockets:
            if i.canUseInFight:
                canUse.append(i)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        item1 = types.KeyboardButton('ударить')
        item2 = types.KeyboardButton('')
        item3 = types.KeyboardButton('')
        item5 = types.KeyboardButton('')
        if game.player.shield != '':
            item2 = types.KeyboardButton('защититься')
        if len(canUse) > 0:
            item3 = types.KeyboardButton('использовать')
        item4 = types.KeyboardButton('бежать')
        haveSpareWeapon = False
        for item in game.player.pockets:
            if isinstance(item, Weapon):
                haveSpareWeapon = True
        if game.player.weapon != '' and haveSpareWeapon:
            item5 = types.KeyboardButton('сменить оружие')
        markup.add(item1, item2, item3, item4, item5)
    elif state == 'direction':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        item1 = types.KeyboardButton('идти вверх')
        item2 = types.KeyboardButton('идти вниз')
        item3 = types.KeyboardButton('идти налево')
        item4 = types.KeyboardButton('идти направо')
        markup.add(item1, item2, item3, item4)
    elif state == 'levelup':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        item1 = types.KeyboardButton('Здоровье')
        item2 = types.KeyboardButton('Силу')
        item3 = types.KeyboardButton('Ловкость')
        item4 = types.KeyboardButton('Интеллект')
        markup.add(item1, item2, item3, item4)
    elif state == 'enchant':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
        item1 = types.KeyboardButton('Отмена')
        markup.add(item1)
    else:
        markup = ''
    if isinstance(text, str):
        bot.send_message(game.chat_id, text, reply_markup=markup)
    elif isinstance(text, list):
        final_text = ''
        for line in text:
            final_text = final_text + str(line) + '\n'
        bot.send_message(game.chat_id, final_text.rstrip('\n'), reply_markup=markup)

def pprint (game, text, width = 200, height = 200, color = '#FFFFFF'):
    pic = Image.new('RGB', (width,height), color=(color))
    font = ImageFont.truetype('PTMono-Regular.ttf', size=18)
    draw_text = ImageDraw.Draw(pic)
    if isinstance(text, str):
        draw_text.text(
            (10, 10),
            text,
            font=font,
            fill=('#000000')
        )
        bot.send_photo(game.chat_id, pic)
    elif isinstance(text, list):
        final_text = ''
        for line in text:
            final_text = final_text + str(line) + '\n'
        draw_text.text(
            (10, 10),
            final_text,
            font=font,
            fill=('#000000')
        )
        bot.send_photo(game.chat_id, pic)

@bot.message_handler(commands=['start', 'старт', 's'])
def welcome(message):
    global chat_id
    chat_id = message.chat.id
    game = game_sessions.get(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Новая игра')
    itembtn2 = types.KeyboardButton('Отмена')
    if game:
        if game.gameIsOn:
            markup.add(itembtn1, itembtn2)
            bot.reply_to(message, "Игра уже запущена.\nТы точно хочешь начать новую игру?\n", reply_markup=markup)
        else:
            markup.add(itembtn1)
            bot.reply_to(message, "Привет!\nХочешь начать игру?\n", reply_markup=markup)
    else:
        markup.add(itembtn1)
        bot.reply_to(message, "Привет!\nХочешь начать игру?\n", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Новая игра')
def start_game(message):
    chat_id = message.chat.id
    newGame = Game(chat_id)
    game_sessions[chat_id] = newGame
    player = newGame.player
    print('='*40)
    print(game_sessions)
    newGame.gameIsOn = True
    newGame.newCastle.plan[player.currentPosition].show(player)
    newGame.newCastle.plan[player.currentPosition].map()


def is_common_comand(message):
    if not game_sessions.get(message.chat.id):
        return False
    else:
        if message.text.lower().split(' ')[0] in telegram_commands and \
                not game_sessions[message.chat.id].IN_FIGHT and \
                not game_sessions[message.chat.id].LEVEL_UP and \
                not game_sessions[message.chat.id].ENCHANTING:
            return True
        else:
            return False

@bot.message_handler(func=is_common_comand)
def get_command(message):
    chat_id = message.chat.id
    game = game_sessions[chat_id]
    if not game.player.gameover('killall', game.howMany['монстры']):
        game.player.do(message.text.lower())

def is_levelup_comand(message):
    if not game_sessions.get(message.chat.id):
        return False
    else:
        if message.text.lower().split(' ')[0] in level_up_commands and game_sessions[message.chat.id].LEVEL_UP:
            return True
        else:
            return False

@bot.message_handler(is_levelup_comand)
def get_level_up_command(message):
    chat_id = message.chat.id
    game = game_sessions[chat_id]
    a = message.text.lower().split(' ')[0]
    if a == 'здоровье':
        game.player.health += 3
        game.player.startHealth += 3
        tprint(game.player.name + ' получает 3 единицы здоровья.', 'off')
        game.LEVEL_UP = False
    elif a == 'силу':
        game.player.stren += 1
        game.player.startStren += 1
        tprint(game.player.name + ' увеличивает свою силу на 1.', 'off')
        game.LEVEL_UP = False
    elif a == '3' or a == 'ловкость':
        game.player.dext += 1
        game.player.startDext += 1
        tprint(game.player.name + ' увеличивает свою ловкость на 1.', 'off')
        game.LEVEL_UP = False
    elif a == '4' or a == 'интеллект':
        game.player.intel += 1
        game.player.startIntel += 1
        tprint(game.player.name + ' увеличивает свой интеллект на 1.', 'off')
        game.LEVEL_UP = False

def is_enchantinf_comand(message):
    if not game_sessions.get(message.chat.id):
        return False
    else:
        if message.text.lower().split(' ')[0] and game_sessions[message.chat.id].ENCHANTING:
            return True
        else:
            return False

@bot.message_handler(func=is_enchantinf_comand)
def get_enchanting_command(message):
    chat_id = message.chat.id
    game = game_sessions[chat_id]
    answer = message.text.lower()
    runeList = game.player.inpockets(Rune)
    if answer == 'отмена':
        game.ENCHANTING = False
        return True
    elif answer.isdigit() and int(answer) - 1 < len(runeList):
        if game.selectedItem.enchant(runeList[int(answer) - 1]):
            tprint(game, game.player.name + ' улучшает ' + game.selectedItem.name1 + ' новой руной.', 'off')
            game.player.pockets.remove(runeList[int(answer) - 1])
            game.ENCHANTING = False
            return True
        else:
            tprint(game, 'Похоже, что ' +
                   game.player.name +
                   'не может вставить руну в ' +
                   game.selectedItem.name1 +
                   '.', 'off')
            game.ENCHANTING = False
            return False
    else:
        tprint(game, game.player.name + ' не находит такую руну у себя в карманах.', 'off')

def is_fight_comand(message):
    if not game_sessions.get(message.chat.id):
        return False
    else:
        if message.text.lower().split(' ')[0] in fight_commands and game_sessions[message.chat.id].IN_FIGHT:
            return True
        else:
            return False

@bot.message_handler(func=is_fight_comand)
def get_in_fight_command(message):
    chat_id = message.chat.id
    game = game_sessions[chat_id]
    enemy = game.newCastle.plan[game.player.currentPosition].center
    tprint(game, game.player.attack(enemy, message.text))
    if game.IN_FIGHT:
        if enemy.run:
            game.IN_FIGHT = False
        elif enemy.health > 0:
            enemy.attack(game.player)
        else:
            tprint(game, game.player.name + ' побеждает в бою!', 'off')
            game.IN_FIGHT = False
            game.player.win(enemy)
            enemy.lose(game.player)

bot.polling(none_stop=True, interval=0)

while not player.gameover('killall', howMany['монстры']):
    player.do(input('Что требуется от ' + player.name1 + '? ---->'))