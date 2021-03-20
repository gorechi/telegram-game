#!/usr/bin/python
# -*- coding: utf-8 -*-
# Импортируем необходимые модули

import telebot
from telebot import types
from functions import *
from PIL import Image, ImageDraw, ImageFont



# Константы
TOKEN = '1528705199:AAH_tVPWr6GuxBLdxOhGNUd25tNEc23pSp8'
IN_FIGHT = False
LEVEL_UP = False
ENCHANTING = False
selectedItem = ''
telegram_commands = ['обыскать',
                     '?',
                     'осмотреть',
                     'идти',
                     'атаковать',
                     'взять',
                     'открыть',
                     'использовать',
                     'улучшить']
fight_commands = ['ударить',
                  '?',
                  'защититься',
                  'бежать',
                  'использовать']
level_up_commands = ['здоровье',
                     'силу',
                     'ловкость',
                     'интеллект']
howMany = {'монстры': 10, 'оружие': 10, 'защита': 10, 'зелье': 8, 'руна': 15}
decor1 = readfile('decorate1', False)
decor2 = readfile('decorate2', False)
decor3 = readfile('decorate3', False)
decor4 = readfile('decorate4', False)
weakness = {1: [3, 3], 2: [3, 6], 3: [7, 7], 4: [3, 7], 6: [7, 14], 7: [12, 12], 8: [3, 12], 10: [7, 12], 12: [1, 1],
            13: [1, 3], 14: [12, 24], 15: [1, 7], 19: [1, 12], 24: [1, 2]}
elementDictionary = {1: 'огня', 2: 'пламени', 3: 'воздуха', 4: 'дыма', 6: 'ветра', 7: 'земли', 8: 'лавы', 10: 'пыли',
                     12: 'воды', 13: 'пара', 14: 'камня', 15: 'дождя', 19: 'грязи', 24: 'потопа'}

# Описываем классы

class Item:
    def __init__(self):
        self.name = 'штука'
        self.name1 = 'штуку'
        self.canUseInFight = False
        self.description = self.name

    def __str__(self):
        return self.name

    def take(self, who=''):
        who.pockets.append(self)
        tprint(who.name + ' забирает ' + self.name + ' себе.')

    def use(self, whoisusing, inaction=False):
        tprint(whoisusing.name + ' не знает, как использовать такие штуки.')

    def show(self):
        return self.description

class Rune:
    def __init__(self):
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

    def element(self):
        return int(self.element)

    def take(self, who=''):
        who.pockets.append(self)
        tprint(who.name + ' забирает ' + self.name1 + ' себе.')

    def show(self):
        return self.name + ' ' + elementDictionary[self.element] + ' - урон + ' + str(self.damage) + \
               ' или защита + ' + str(self.defence)

    def use(self, whoisusing, inaction=False):
        tprint(whoisusing.name + ' не знает, как использовать такие штуки.')


class Spell:
    def __init__(self, name='Обычное заклинание', name1='Обычного заклинания', element='магия', minDamage=1,
                 maxDamage=5, minDamageMult=1, maxDamageMult=1, actions='кастует'):
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
    def __init__(self, name, name1='оружие', damage=0, actions='бьет,ударяет'):
        if name != 0:
            self.name = name
            self.damage = int(damage)
            self.name1 = name1
        else:
            n1 = [['Большой', 'Большая', 'Большой', 'Большую'], ['Малый', 'Малая', 'Малый', 'Малую'],
                  ['Старый', 'Старая', 'Старый', 'Старую'], ['Тяжелый', 'Тяжелая', 'Тяжелый', 'Тяжелую'],
                  ['Новый', 'Новая', 'Новый', 'Новую']]
            n2 = [['меч', 0, 'меч'], ['сабля', 1, 'саблю'], ['катана', 1, 'катану'], ['топор', 0, 'топор'],
                  ['кинжал', 0, 'кинжал'], ['дубина', 1, 'дубину'], ['шпага', 1, 'шпагу']]
            a1 = dice(0, len(n1) - 1)
            a2 = dice(0, len(n2) - 1)
            self.name = n1[a1][n2[a2][1]] + ' ' + n2[a2][0]
            self.name1 = n1[a1][n2[a2][1]+2] + ' ' + n2[a2][2]
            self.damage = dice(3, 12)
        self.actions = actions.split(',')
        self.canUseInFight = True
        self.runes = []

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
        if who.weapon == '':
            who.weapon = self
            tprint(who.name + ' берет ' + self.name1 + ' в руку.')
        else:
            who.pockets.append(self)
            tprint(who.name + ' забирает ' + self.name1 + ' себе.')

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
        tprint(whoUsing.name + ' теперь использует ' + self.name1 + ' в качестве оружия!')


class Shield:
    def __init__(self, name, name1='защиту', protection=0, actions=''):
        if name != 0:
            self.name = name
            self.name1 = name1
            self.protection = int(protection)
        else:
            n1 = [['Большой', 'Большая', 'Большой', 'Большую'], ['Малый', 'Малая', 'Малый', 'Малую'],
                  ['Старый', 'Старая', 'Старый', 'Старую'], ['Тяжелый', 'Тяжелая', 'Тяжелый', 'Тяжелую'],
                  ['Новый', 'Новая', 'Новый', 'Новую']]
            n2 = [['щит', 0, 'щит'], ['броня', 1, 'броню'], ['кольчуга', 1, 'кольчугу'], ['защита', 1, 'защиту'],
                  ['панцырь', 0, 'панцырь']]
            a1 = dice(0, len(n1) - 1)
            a2 = dice(0, len(n2) - 1)
            self.name = n1[a1][n2[a2][1]] + ' ' + n2[a2][0]
            self.name1 = n1[a1][n2[a2][1]+2] + ' ' + n2[a2][2]
            self.protection = dice(2, 5)
        self.actions = actions.split(',')
        self.canUseInFight = True
        self.runes = []

    def __str__(self):
        protectionString = str(self.protection)
        if self.permprotection() != 0:
            protectionString += '+' + str(self.permprotection())
        return self.name + self.enchantment() + ' (' + protectionString + ')'

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
        tprint('Множитель защиты - ' + str(multiplier))
        if who.hide:
            who.hide = False
            return self.protection + self.permprotection()
        else:
            return ceil((dice(1, self.protection) + self.permprotection())*multiplier)

    def take(self, who):
        if who.shield == '':
            who.shield = self
            tprint(who.name + ' использует ' + self.name1 + ' как защиту.')
        else:
            player.pockets.append(self)
            tprint(who.name + ' забирает ' + self.name1 + ' себе.')

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
        tprint(whoUsing.name + ' теперь использует ' + self.name1 + ' в качестве защиты!')


class Map(Item):
    def __init__(self):
        super().__init__()
        self.name = 'карта'
        self.name1 = 'карту'
        self.description = 'Карта, показывающая расположение комнат замка'
        a = randomitem(newCastle.plan, False)
        if a.center != '':
            a.center.loot.add(self)
        else:
            a.loot.add(self)

    def place(self):
        a = randomitem(newCastle.plan, False)
        if a.center != '':
            a.center.loot.add(self)
        else:
            a.loot.add(self)

    def use(self, whoisusing, inaction=False):
        if not inaction:
            tprint(whoisusing.name + ' смотрит на карту замка.')
            newCastle.map()
            return True
        else:
            tprint('Во время боя это совершенно неуместно!')
            return False


class Key(Item):
    def __init__(self):
        super().__init__()
        self.name = 'ключ'
        self.name1 = 'ключ'
        self.description = 'Ключ, пригодный для дверей и сундуков'

    def __str__(self):
        return self.description


class Potion(Item):
    def __init__(self, name, effect=0, type=0, canUseInFight=True, ):
        super().__init__()
        self.name = name
        self.name1 = self.name
        self.effect = int(effect)
        self.type = int(type)
        self.canUseInFight = canUseInFight
        descriptions = ['Лечебное зелье восстанавливает некоторое количество единиц здоровья.',
                        'Зелье здоровья увеличивает максимальный запас здоровья персонажа.',
                        'Зелье силы увеличивает максимальное значение силы персонажа.',
                        'Зелье усиления временно добавляет персонажу силы.',
                        'Зелье ловкости увеличивает максимальное значение ловкости персонажа.',
                        'Зелье увертливости временно добавляет персонажу ловкости.',
                        'Зелье ума увеличивает максимальное значение силы интеллекта.',
                        'Зелье просветления временно добавляет персонажу интеллекта.']
        self.description = descriptions[self.type]

    def use(self, whoUsing, inaction = False):
        if not inaction:
            if self.type == 1:
                whoUsing.startHealth += self.effect
                whoUsing.health += self.effect
                tprint (whoUsing.name + ' увеличивает свое максмальное здоровье на ' + str(self.effect) + ' до ' + str(whoUsing.health) + '.')
                return True
            elif self.type == 2:
                whoUsing.stren += self.effect
                whoUsing.startStren += self.effect
                tprint (whoUsing.name + ' увеличивает свою силу на ' + str(self.effect) + ' до ' + str(whoUsing.stren) + '.')
                return True
            elif self.type == 4:
                whoUsing.dext += self.effect
                whoUsing.startDext += self.effect
                tprint (whoUsing.name + ' увеличивает свою ловкость на ' + str(self.effect) + ' до ' + str(whoUsing.dext) + '.')
                return True
            elif self.type == 6:
                whoUsing.intel += self.effect
                whoUsing.startIntel += self.effect
                tprint (whoUsing.name + ' увеличивает свой интеллект на ' + str(self.effect) + ' до ' + str(whoUsing.intel) + '.')
                return True
            else:
                tprint('Это зелье можно использовать только в бою!')
                return False
        else:
            if self.type == 0:
                if (whoUsing.startHealth - whoUsing.health) < self.effect:
                    heal = dice(1, (whoUsing.startHealth - whoUsing.health))
                else:
                    heal = dice(1, self.effect)
                whoUsing.health += heal
                tprint (whoUsing.name + ' восполняет ' + howmany(heal, 'единицу жизни,единицы жизни,единиц жизни'))
                return True
            elif self.type == 3:
                whoUsing.stren += self.effect
                tprint ('На время боя ' + whoUsing.name + ' увеличивает свою силу на ' + str(self.effect) + ' до ' + str(whoUsing.stren) + '.')
                return True
            elif self.type == 5:
                whoUsing.dext += self.effect
                tprint ('На время боя ' + whoUsing.name + ' увеличивает свою ловкость на ' + str(self.effect) + ' до ' + str(whoUsing.dext) + '.')
                return True
            elif self.type == 7:
                whoUsing.intel += self.effect
                tprint ('На время боя ' + whoUsing.name + ' увеличивает свой интеллект на ' + str(self.effect) + ' до ' + str(whoUsing.intel) + '.')
                return True
            else:
                tprint('Это зелье нельзя использовать в бою!')
                return False
    def __str__(self):
        return self.description


class Loot:
    def __init__(self):
        self.pile = []

    def __str__(self):
        return 'loot'

    def __add__(self, other):
        self.pile += other.pile

    def add(self, obj):
        self.pile.append(obj)

    def remove(self, obj):
        self.pile.remove(obj)


class Chest:
    def __init__(self, name):
        self.loot = ""
        self.locked = False
        self.opened = False
        self.name = name
        self.state = 'стоит'
        self.name1 = 'сундук'
        self.agressive = False
        self.keyHole = 'видит какой-то крупный предмет.'

    def __str__(self):
        return self.name


class Money:
    def __init__(self, howmanymoney):
        self.howmanymoney = howmanymoney
        if 0 < self.howmanymoney <= 10:
            self.name = 'Несколько монет'
            self.name1 = 'Несколько монет'
        elif 10 < self.howmanymoney <= 20:
            self.name = 'Кучка монет'
            self.name1 = 'Кучку монет'
        elif 20 < self.howmanymoney <= 30:
            self.name = 'Груда монет'
            self.name1 = 'Груду монет'
        elif 30 < self.howmanymoney:
            self.name = 'Много монет'
            self.name1 = 'Много монет'

    def __str__(self):
        return self.name + ' (' + self.howmanymoney + ')'

    def take(self, luckyOne):
        luckyOne.money.howmanymoney += self.howmanymoney
        tprint(luckyOne.name + ' забрал ' + howmany(self.howmanymoney, 'монету,монеты,монет'))

    def show(self):
        if self.howmanymoney > 0:
            return howmany(self.howmanymoney, 'монету,монеты,монет')
        else:
            return 'Денег нет'

    def __add__(self, other):
        self.howmanymoney += other.howmanymoney


class Hero:
    def __init__(self, name, name1, gender, stren=10, dext=2, intel=0, health=20, weapon='', shield='', actions='бьет',
                 pockets=[]):
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
        self.shield = shield
        self.pockets = pockets
        self.money = Money(0)
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
        self.directionsDict = {0: (0 - newCastle.rooms),
                               1: 1,
                               2: newCastle.rooms,
                               3: (0 - 1),
                               'наверх': (0 - newCastle.rooms),
                               'направо': 1,
                               'вправо': 1,
                               'налево': (0 - 1),
                               'лево': (0 - 1),
                               'влево': (0 - 1),
                               'вниз': newCastle.rooms,
                               'низ': newCastle.rooms,
                               'вверх': (0 - newCastle.rooms),
                               'верх': (0 - newCastle.rooms),
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

    def run_away(self, target):
        global IN_FIGHT
        room = newCastle.plan[self.currentPosition]
        tprint(self.name + ' сбегает с поля боя.')
        a = dice(1, 2)
        if a == 1 and self.weapon != '':
            tprint('Убегая ' + self.name + ' роняет из рук ' + self.weapon.name1)
            if target.weapon == '' and target.carryweapon:
                target.weapon = self.weapon
            else:
                room.loot.add(self.weapon)
            self.weapon = ''
        elif a == 2 and self.shield != '':
            tprint('Убегая ' + self.name + ' теряет ' + self.shield.name1)
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
            tprint(text)
        availableDirections = []
        for i in range(4):
            if room.doors[i] == 1:
                availableDirections.append(i)
        self.currentPosition += self.directionsDict[availableDirections[dice(0,len(availableDirections)-1)]]
        room = newCastle.plan[self.currentPosition]
        room.visited = '+'
        IN_FIGHT = False
        self.lookaround()
        if room.center != '':
            if room.center.agressive and room.light:
                self.fight(room.center, True)
        return self.name + ' еле стоит на ногах.'

    def attack(self, target, action):
        global IN_FIGHT
        self.run = False
        if self.rage > 1:
            rage = dice(2, self.rage)
        else:
            rage = 1
        meleAttack = dice(1, self.stren) * rage
        canUse = []
        for i in self.pockets:
            if i.canUseInFight:
                canUse.append(i)

        if action == '' or action == 'у' or action == 'ударить':
            tprint(showsides(self, target))
            self.rage = 0
            if self.weapon != '':
                weaponAttack = self.weapon.attack()
                string1 = self.name + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name + \
                          ' и наносит ' + str(meleAttack) + '+' + howmany(weaponAttack, 'единицу,единицы,единиц') + \
                          ' урона. '
            else:
                weaponAttack = 0
                string1 = self.name + ' бьет ' + target.name1 + ' не используя оружие и наносит ' + howmany(
                    meleAttack, 'единицу,единицы,единиц') + ' урона. '
            targetDefence = target.defence(self)
            if (weaponAttack + meleAttack - targetDefence) > 0:
                totalDamage = weaponAttack + meleAttack - targetDefence
            else:
                totalDamage = 0
            if totalDamage == 0:
               string2 = self.name + ' не смог пробить защиту ' + target.name1 + '.'
            elif targetDefence == 0:
               string2 = target.name + ' беззащитен и теряет ' + howmany(totalDamage, 'жизнь,жизни,жизней') + '.'
            else:
               string2 = target.name + ' использует для защиты ' + target.shield.name1 + ' и теряет ' + howmany(
                    totalDamage, 'жизнь,жизни,жизней') + '.'
            target.health -= totalDamage
            return string1 + string2
        elif action == 'з' or action == 'защититься' or action == 'защита':
            tprint(showsides(self, target))
            self.hide = True
            self.rage += 1
            return (self.name + ' уходит в глухую защиту, терпит удары и накапливает ярость.')
        elif action == 'б' or action == 'бежать' or action == 'убежать':
            return self.run_away(target)
        elif (action == 'и' or action == 'использовать') and len(canUse) > 0:
            tprint('Во время боя ' + self.name + ' может использовать:')
            for i in self.pockets:
                if i.canUseInFight:
                    tprint(i.name)
            while True:
                a = input('Что нужно использовать? ---->')
                if a == 'ничего' or a == '':
                    break
                else:
                    itemUsed = False
                    for i in canUse:
                        if i.name == a or i.name1 == a:
                            if i.use(self, inaction=True) and isinstance(i, Potion):
                                self.pockets.remove(i)
                            itemUsed = True
                            # self.use(a, True)
                            break
                    if itemUsed:
                        break
                    tprint('Что-то не выходит')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        item1 = types.KeyboardButton('ударить')
        item2 = types.KeyboardButton('')
        item3 = types.KeyboardButton('')
        line = self.name + ' может (у)дарить'
        if self.shield != '':
            line += ', (з)ащититься'
            item2 = types.KeyboardButton('защититься')
        if len(canUse) > 0:
            line += ', (и)спользовать'
            item3 = types.KeyboardButton('использовать')
        line += ' или (б)ежать ---->'
        item4 = types.KeyboardButton('бежать')
        markup.add(item1, item2, item3, item4)
        tprint(line)

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
        tprint(
            '{0} - это смелый герой {7} уровня. Его сила - {1}{2} {3} и сейчас у него {4} здоровья, что составляет {5}% от максимально возможного.\n{0} имеет при себе {6} золотом.'.format(
                self.name, self.stren, string1, string2, howmany(self.health, 'единица,единицы,единиц'),
                self.health * 100 // self.startHealth, howmany(self.money.howmanymoney, 'монету,монеты,монет'),
                self.level))

    def defence(self, attacker):
        if self.shield == '':
            return 0
        else:
            return self.shield.protect(attacker)

    def lose(self, winner):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.currentPosition = 0
        #tprint('После поражения в схватке ' + self.name + ' очнулся у входа в замок.')

    def win(self, loser):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.wins += 1
        tprint(self.name + ' получает ' + howmany(loser.exp, 'единицу,единицы,единиц') + ' опыта!')
        self.exp += loser.exp
        if self.exp > self.levels[self.level]:
            self.levelup()

    def levelup(self):
        global LEVEL_UP
        LEVEL_UP = True
        level_up_message = []
        level_up_message.append(self.name + ' получает новый уровень!')
        level_up_message.append('Что необходимо прокачать: здоровье, силу, ловкость или интеллект?')
        tprint(level_up_message, 'levelup')
        self.level += 1
        return True

    def gameover(self, goaltype, goal):
        if goaltype == 'killall':
            if newCastle.monsters() == 0:
                tprint(self.name + ' убил всех монстров в замке и выиграл в этой игре!')
                return True
            else:
                return False
        return False

    def lookaround(self, a=''):
        if a == '':
            newCastle.plan[self.currentPosition].show(player)
            newCastle.plan[self.currentPosition].map()
        elif a == 'себя':
            self.show()
        elif a == 'карманы':
            text = []
            text.append(self.name + ' осматривает свои карманы и обнаруживает в них:')
            for i in range(len(self.pockets)):
                text.append(str(i+1) + ': ' + self.pockets[i].show())
            text.append(self.money.show())
            tprint(text)
        elif a in self.directionsDict.keys():
            if newCastle.plan[self.currentPosition].doors[self.doorsDict[a]] == 0:
                tprint (self.name + ' осматривает стену и не находит ничего заслуживающего внимания.')
            else:
                tprint(self.name + ' заглядывает в замочную скважину и ' + newCastle.plan[self.directionsDict[a]].showThroughKeyHole(self))

        if newCastle.plan[self.currentPosition].center != '':
            if (a == newCastle.plan[self.currentPosition].center.name or a == newCastle.plan[
                self.currentPosition].center.name1 or a == newCastle.plan[self.currentPosition].center.name[
                0]) and isinstance(newCastle.plan[self.currentPosition].center, Monster):
                print(showsides(self, newCastle.plan[self.currentPosition].center))

        if self.weapon != '':
            if a == self.weapon.name or a == self.weapon.name1 or a == 'оружие':
                tprint(self.weapon.show())
        if self.shield != '':
            if a == self.shield.name or a == self.shield.name1 or a == 'защиту':
                tprint(self.shield.show())

        if len(self.pockets) > 0:
            text = []
            for i in self.pockets:
                if a == i.name or a == i.name1:
                    text.append(i.show())
            tprint(text)

    def go(self, direction):
        room = newCastle.plan[self.currentPosition]
        if direction not in self.directionsDict.keys():
            tprint(self.name + ' не знает такого направления!')
            return False
        elif room.doors[self.doorsDict[direction]] == 0:
            if room.light:
                message = ['Там нет двери. ' + self.name + ' не может туда пройти!']
            else:
                message = ['В темноте ' + self.name + ' врезается во что-то носом.']
            tprint(message)
            return False
        elif room.doors[self.doorsDict[direction]] == 2:
            if room.light:
                message = ['Эта дверь заперта. ' + self.name + ' не может туда пройти, нужен ключ!']
            else:
                message = ['В темноте ' + self.name + ' врезается во что-то носом.']
            tprint(message)
            return False
        else:
            self.currentPosition += self.directionsDict[direction]
            room = newCastle.plan[self.currentPosition]
            room.visited = '+'
            self.lookaround()
            if room.center != '':
                if room.center.agressive and room.light:
                    self.fight(room.center)
            return True

    def fight(self, enemy, agressive = False):
        global IN_FIGHT
        if isinstance(enemy, Monster):
            whoisfighting = enemy
        elif newCastle.plan[self.currentPosition].center != '':
            if not isinstance(newCastle.plan[self.currentPosition].center, Monster):
                tprint('Не нужно кипятиться. Тут некого атаковать')
                return False
            elif (newCastle.plan[self.currentPosition].center.name != enemy
                    and newCastle.plan[self.currentPosition].center.name1 != enemy
                    and newCastle.plan[self.currentPosition].center.name[0] != enemy) \
                    and enemy != '':
                tprint(self.name + ' не может атаковать. В комнате нет такого существа.')
                return False
            else:
                whoisfighting = newCastle.plan[self.currentPosition].center
        IN_FIGHT = True
        if agressive:
            whoFirst = 2
        else:
            whoFirst = dice(1, 2)
        if whoFirst == 1:
            tprint(player.name + ' начинает схватку!', 'fight')
            self.attack(whoisfighting, 'атаковать')
        else:
            tprint(whoisfighting.name + ' начинает схватку!', 'fight')
            tprint(whoisfighting.attack(self))
            return True

    def search(self, item=''):
        room = newCastle.plan[self.currentPosition]
        enemyinroom = newCastle.plan[self.currentPosition].center
        enemyinambush = newCastle.plan[self.currentPosition].ambush
        if not room.light:
            message = ['В комнате настолько темно, что невозможно что-то отыскать.']
            tprint(message)
            return True
        if enemyinroom != '':
            if isinstance(enemyinroom, Monster):
                tprint(room.center.name + " мешает толком осмотреть комнату.")
            elif isinstance(enemyinroom, Chest):
                message = ["В комнате стоит " + room.center.name]
                if room.loot != '' and \
                        len(room.loot.pile) > 0:
                    message.append('Вокруг сундука валяются:')
                    for i in room.loot.pile:
                        message.append(i.name)
                tprint(message)
        elif enemyinambush != '' and item == '':
            room.center = enemyinambush
            room.ambush = ''
            enemyinroom = room.center
            tprint ('Неожиданно из засады выскакивает ' + enemyinroom.name + ' и нападает на ' + self.name1)
            self.fight(enemyinroom, True)
        else:
            if item == '' and room.loot != '' and len(
                    room.loot.pile) > 0:
                text = []
                text.append('В комнате есть:')
                for i in room.loot.pile:
                    text.append(i.name)
                tprint(text)
            elif item == '':
                tprint('В комнате нет ничего интересного.')

    def take(self, item='все'):
        currentLoot = newCastle.plan[self.currentPosition].loot
        if currentLoot == '':
            tprint('Здесь нечего брать.')
            return False
        elif item == 'все' or item == 'всё' or item == '':
            for i in currentLoot.pile:
                i.take(self)
            newCastle.plan[self.currentPosition].loot = ''
            return True
        else:
            for i in currentLoot.pile:
                if i.name.lower() == item or i.name1.lower() == item:
                    i.take(self)
                    currentLoot.pile.remove(i)
                    return True
        tprint('Такой вещи здесь нет.')
        return False

    def open(self, item=''):
        room = newCastle.plan[self.currentPosition]
        whatIsInRoom = room.center
        if item == '' or (not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0):
            if whatIsInRoom == '':
                if room.light:
                    message = ['В комнате нет вещей, которые можно открыть.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(message)
                return False
            elif not isinstance(whatIsInRoom, Chest):
                if room.light:
                    message = ['Пожалуй, ' + self.name + ' не сможет это открыть.']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(message)
                return False
            elif whatIsInRoom.opened:
                if room.light:
                    message =['Этот ' + whatIsInRoom.name1 + ' уже открыт. Зачем его открывать во второй раз?']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(message)
                return False
            elif whatIsInRoom.locked:
                key = False
                for i in self.pockets:
                    if isinstance(i, Key):
                        key = i
                if room.light:
                    if key:
                        self.pockets.remove(key)
                        whatIsInRoom.locked = False
                        message = [self.name + ' отпирает сундук ключом.']
                    else:
                        message = ['Чтобы открыть этот сундук нужен ключ']
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(message)
            if not whatIsInRoom.locked:
                if room.light:
                    message = [self.name + ' открывает ' + whatIsInRoom.name]
                    if room.loot == '':
                        room.loot = []
                    room.loot.pile += whatIsInRoom.loot.pile
                    if len(whatIsInRoom.loot.pile) > 0:
                        message.append(self.name + ' роется в сундуке и обнаруживает в нем:')
                        for i in whatIsInRoom.loot.pile:
                            message.append(i.name1)
                        message.append('Все эти вещи теперь разбросаны по всей комнате.')
                        whatIsInRoom.loot.pile = []
                    else:
                        message = ['В сундуке пусто.']
                    whatIsInRoom.opened = True
                    whatIsInRoom.name = 'открытый пустой ' + whatIsInRoom.name
                    whatIsInRoom.inside = ''
                else:
                    message = [self.name + ' шарит в темноте руками, но не нащупывает ничего интересного']
                tprint (message)
                return True
        else:
            key = False
            if not room.light:
                message = [self.name + ' ничего не видит и не может нащупать замочную скважину.']
                tprint (message)
                return False
            for i in self.pockets:
                if isinstance(i, Key):
                    key = i
            if not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0:
                tprint(self.name + ' не может это открыть.')
                return False
            elif newCastle.plan[self.currentPosition].doors[self.doorsDict[item]] != 2:
                tprint('В той стороне нечего открывать.')
                return False
            elif not key:
                tprint('Нужен ключ.')
                return False
            else:
                self.pockets.remove(key)
                room.doors[self.doorsDict[item]] = 1
                j = self.doorsDict[item] + 2 if (self.doorsDict[item] + 2) < 4 else self.doorsDict[item] - 2
                newCastle.plan[self.currentPosition + self.directionsDict[item]].doors[j] = 1
                tprint(self.name + ' открывает дверь.')

    def use(self, item='', infight=False):
        if item == '':
            tprint(self.name + ' не понимает, что ему надо использовать.')
        elif item.isdigit():
            if int(item)-1 < len(self.pockets):
                i = self.pockets[int(item)-1]
                if isinstance(i, Potion) and i.use(self, False):
                    self.pockets.remove(i)
                elif not isinstance(i, Potion):
                    i.use(self, False)
                return True
            else:
                tprint(self.name + ' не нашел такой вещи у себя в карманах.')
                return False
        else:
            for i in self.pockets:
                if i.name == item or i.name1 == item:
                    if isinstance(i, Potion)  and i.use(self, inaction = False):
                        self.pockets.remove(i)
                    else:
                        i.use(self, inaction = False)
                    return True
            tprint(self.name + ' не нашел такой вещи у себя в карманах.')

    def enchant(self, item=''):
        global ENCHANTING
        global selectedItem
        runeList = self.inpockets(Rune)
        if len(runeList) == 0:
            tprint(self.name + 'не может ничего улучшать. В карманах не нашлось ни одной руны.')
            return False
        if item == '':
            tprint(self.name + ' не понимает, что ему надо улучшить.')
            return False
        elif item == 'оружие' and self.weapon != '':
            selectedItem = self.weapon
        elif item in ['защиту', 'защита'] and self.shield != '':
            selectedItem = self.shield
        elif item.isdigit() and int(item)-1 <= len(self.pockets):
            selectedItem = self.pockets[int(item)-1]
        else:
            for i in self.pockets:
                if i.name.lower() == item.lower() or i.name1.lower() == item.lower():
                    selectedItem = i
                else:
                    tprint(self.name + ' не нашел такой вещи у себя в карманах.')
                    return False
        if selectedItem != '' and isinstance(selectedItem, Weapon) or isinstance(selectedItem, Shield):
            text = []
            text.append(self.name + ' может использовать следующие руны:')
            for rune in runeList:
                text.append(str(runeList.index(rune)+1) + ': ' + str(rune))
            text.append('Введите номер руны или "отмена" для прекращения улучшения')
            #Здесь нужна доработка т.к. управление переходит на работу с рунами
            ENCHANTING = True
            tprint(text, 'enchant')
        else:
            tprint(self.name + ' не может улучшить эту вещь.')
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
            tprint(text)
            return True
        c = commandDict.get(fullCommand[0], False)
        if not c:
            tprint('Такого ' + self.name + ' не умеет!')
        elif len(fullCommand) == 1:
            c()
        else:
            c(fullCommand[1])


class Monster:
    def __init__(self, name, name1, stren=10, health=20, actions='бьет', state='стоит', agressive=False,
                 carryweapon=True, carryshield=True):
        self.name = name
        self.name1 = name1
        self.stren = int(stren)
        self.health = int(health)
        self.actions = actions.split(',')
        self.state = state
        self.weapon = ''
        self.shield = ''
        self.money = 5
        self.currentPosition = 0
        self.startHealth = self.health
        self.loot = Loot()
        self.hide = False
        self.run = False
        self.wounded = False
        self.keyHole = 'видит какую-то неясную фигуру.'
        if carryweapon == 'True':
            self.carryweapon = True
        else:
            self.carryweapon = False
        if carryshield == 'True':
            self.carryshield = True
        else:
            self.carryshield = False
        if agressive == 'True':
            self.agressive = True
        else:
            self.agressive = False
        self.exp = self.stren * dice(1, 10) + dice(1, self.health)

    def __str__(self):
        return self.name

    def give(self, item):
        if isinstance(item, Weapon) and self.weapon == '':
            self.weapon = item
        elif isinstance(item, Shield) and self.shield == '':
            self.shield = item
        elif isinstance(item, Rune):
            if item.damage >= item.defence:
                if self.weapon != '':
                    if self.weapon.enchant(item):
                        return True
                    elif self.shield != '':
                        if not self.shield.enchant(item):
                            self.loot.add(item)
                            return True
                    else:
                        self.loot.add(item)
                        return True
                elif self.shield != '':
                    if not self.shield.enchant(item):
                        self.loot.add(item)
                        return True
                else:
                    self.loot.add(item)
                    return True
            else:
                if self.shield != '':
                    if self.shield.enchant(item):
                        return True
                    elif self.weapon != '':
                        if not self.weapon.enchant(item):
                            self.loot.add(item)
                            return True
                    else:
                        self.loot.add(item)
                        return True
                elif self.weapon != '':
                    if not self.weapon.enchant(item):
                        self.loot.add(item)
                        return True
                else:
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
        return dice(1, self.stren)

    def attack(self, target):
        global IN_FIGHT
        text = []
        meleAttack = self.mele()
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            text.append(self.name + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name \
                      + ' и наносит ' + str(meleAttack) + '+' \
                      + howmany(weaponAttack, 'единицу,единицы,единиц') + ' урона. ')
        else:
            weaponAttack = 0
            text.append(self.name + ' бьет ' + target.name1 + ' не используя оружия и наносит ' + howmany(
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
            text.append(self.name + ' не смог пробить защиту ' + target.name1 + '.')
        target.health -= totalDamage
        if target.health <= 0:
            IN_FIGHT = False
            target.lose(self)
            text.append(target.name + ' терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(text, 'off')
        else:
            tprint(text)
        return True

    def defence(self, attacker):
        if self.shield == '':
            return 0
        else:
            return self.shield.protect(attacker)

    def lose(self, winner):
        result = dice(1, 10)
        #tprint('RESULT = ' + str(result))
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
            #tprint('weaknessAmount = ' + str(weaknessAmount))
            illAmount = ceil(self.startHealth * 0.4)
            #tprint('illAmount = ' + str(illAmount))
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
                    tprint(aliveString)
                    where.center = ''
            else:
                aliveString += 'получает ранение в ногу и не может двигаться, теряя при этом '  \
                               + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и ' \
                               + howmany(illAmount, 'жизнь,жизни,жизней') + '.'
                self.stren -= weaknessAmount
                self.health = self.startHealth - illAmount
                tprint(aliveString)

    def win(self, loser):
        self.health = self.startHealth

class Plant(Monster):
    def __init__(self, name, name1, stren=10, health=20, actions='бьет', state='растёт', agressive=False,
                 carryweapon=False, carryshield=False):
        super().__init__(name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.carryshield = False
        self.carryweapon = False
        self.agressive = False

    def grow(self):
        newPlant = Plant(self.name, self.name1, self.stren, self.health, 'бьет', 'растет', False, False, False)
        return newPlant

    def win(self, loser):
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

class Walker(Monster):
    def __init__(self, name, name1, stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=True, carryshield=True):
        super().__init__(name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)

class Berserk(Monster):
    def __init__(self, name, name1, stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=True, carryshield=True):
        super().__init__(name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
        self.agressive = True
        self.carryshield = False
        self.rage = 0
        self.base_health = health

    def mele(self):
        self.rage = (self.base_health - self.health) // 3
        return dice(1, (self.stren + self.rage))



class Shapeshifter(Monster):
    def __init__(self, name, name1, stren=10, health=20, actions='бьет', state='стоит', agressive=True,
                 carryweapon=False, carryshield=True):
        super().__init__(name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)
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
            tprint(self.name +
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
        where.center = ''


class Vampire(Monster):
    def __init__(self, name, name1, stren=10, health=20, actions='бьет', state='стоит', agressive=False,
                 carryweapon=True, carryshield=True):
        super().__init__(name, name1, stren, health, actions, state, agressive, carryweapon, carryshield)

    def attack(self, target):
        text = []
        meleAttack = self.mele()
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            text.append(self.name +
                        ' ' +
                        self.action() +
                        ' ' +
                        target.name1 +
                        ' используя ' +
                        self.weapon.name +
                        ' и наносит ' +
                        howmany(meleAttack, 'единицу,единицы,единиц') +
                        '+' +
                        str(weaponAttack) +
                        ' урона. ')
        else:
            weaponAttack = 0
            text.append(self.name +
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
            text.append(self.name + ' не смог пробить защиту ' + target.name1 + '.')
        elif targetDefence == 0:
            text.append(target.name + ' беззащитен и теряет ' +
                        howmany(totalDamage, 'жизнь,жизни,жизней') +
                        '.' +
                        self.name +
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
                        self.name +
                        ' высасывает ' +
                        str(totalDamage // 2) +
                        ' себе.')
        target.health -= totalDamage
        self.health += totalDamage // 2
        if target.health <= 0:
            IN_FIGHT = False
            target.lose(self)
            text.append(target.name + ' терпит сокрушительное поражение и позорно убегает ко входу в замок.')
            tprint(text, 'off')
        else:
            tprint(text)
        return True


class Room:
    def __init__(self, doors, center='', loot=''):
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
        self.torchDice = dice(1, 5)
        if not self.light or self.torchDice != 4:
            self.torch = False
        else:
            self.torch = True

    def show(self, player):
        if self.light:
            if self.torch:
                self.decoration1 = 'освещенную факелом ' + self.decoration1
            if self.center == '':
                whoIsHere = 'Не видно ничего интересного.'
            else:
                whoIsHere = self.decoration3 + ' ' + self.center.state + ' ' + self.center.name + '.'
            tprint(player.name + ' попадает в {0} комнату {1}. {2} {3}'.format(self.decoration1,
                                                                          self.decoration2,
                                                                          whoIsHere,
                                                                          self.decoration4), state = 'direction')
        else:
            message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
            if isinstance(self.center, Monster):
                message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
            tprint(message, state = 'direction')

    def showThroughKeyHole(self, who):
        if self.center == '':
            return 'не может ничего толком разглядеть.'
        else:
            return self.center.keyHole

    def map(self):
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
            pprint(string1 + '\n' + string2 + '\n' + string3 + '\n' + string2 + '\n' + string4, 100, 120)
            return True
        else:
            return False

    def lock(self, lockOrNot=2):
        a = [-newCastle.rooms, 1, newCastle.rooms, -1]
        for i in range(4):
            if self.doors[i] == 1:
                self.doors[i] = lockOrNot
                j = i + 2 if (i + 2) < 4 else i - 2
                newCastle.plan[self.position + a[i]].doors[j] = lockOrNot
        self.locked = True
        return None


class Castle:
    def __init__(self, floors=5, rooms=5):
        self.floors = floors
        self.rooms = rooms
        self.chestType = ["Обычный",
             "Кованный",
             "Большой",
             "Деревянный",
             "Железный",
             "Маленький",
             "Старинный",
             "Антикварный",
             "Странный",
             "Обычный"]
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
            newLoot = Loot()
            a = Room(self.allDoors[i], '', newLoot)
            a.position = i
            self.plan.append(a)
        self.howManyChests = len(self.plan) // 5 + 1
        self.allChests = self.createchests(50, 50)  # Создаем сундуки
        self.lights_off() #Выключаем свет в некоторых комнатах
        self.plan[0].light = False
        #self.plan[0].torch = True

    def lights_off(self):
        self.how_many_dark_rooms = len(self.plan) // 8
        darkRooms = randomitem(self.plan, False, self.how_many_dark_rooms)
        print ("darkRooms: ", darkRooms )
        for room in darkRooms:
            room.light = False

    def createchests(self, money, probability):
        list = []
        for i in range(self.howManyChests):
            name = randomitem(self.chestType) + ' сундук'
            newChest = Chest(name)
            newLoot = Loot()
            newChest.loot = newLoot
            if dice(1, 4) == 1:
                newChest.locked = True
                veryNewKey = Key()
                self.hide(veryNewKey)
            if dice(1, 100) <= probability:
                newChest.inside = []
                newMoney = Money(dice(1, money))
                newChest.loot.pile.append(newMoney)
            else:
                newChest.loot.pile = []
            list.append(newChest)
        self.inhabit(list, self.howManyChests, True)  # Расставляем сундуки
        return True

    def hide(self, item):
        while True:
            b = randomitem(self.plan)
            if not b.locked:
                if b.center == '':
                    b.loot.pile.append(item)
                else:
                    b.center.loot.pile.append(item)
                break
        return True

    def lockDoors(self):
        howManyLockedRooms = len(self.plan) // 8
        for i in range(howManyLockedRooms):
            while True:
                a = randomitem(self.plan)
                if a != self.plan[0]:
                    newMoney = Money(dice(25, 75))
                    a.lock(2)
                    if a.center == '':
                        a.loot.pile.append(newMoney)
                    else:
                        a.center.loot.pile.append(newMoney)
                    newKey = Key()
                    self.hide(newKey)
                    break
        return True

    def map(self):
        f = self.floors
        r = self.rooms
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '║', '1': ' ', '2': '|'}
        text = []
        text.append('======' * r + '=')
        for i in range(f):
            text.append('║' + '     ║' * r)
            line1 = '║'
            line2 = ''
            for j in range(r):
                a = player.name[0] if player.currentPosition == i * r + j else self.plan[i*r+j].visited
                line1 += '  {0}  {1}'.format(a, doorsVertical[str(self.allDoors[i * r + j][1])])
                line2 += '==={0}=='.format(doorsHorizontal[str(self.allDoors[i * r + j][2])])
            text.append(line1)
            text.append('║' + '     ║' * r)
            text.append(line2 + '=')
        pprint(text, r*72, f*90)

    def inhabit(self, itemsList, howManyItems, emptyRoomsOnly=True):  # Расселяем штуки из списка по замку
        tossedItems = toss(itemsList, len(itemsList))  # Перетасовываем штуки
        for i in range(howManyItems):
            if emptyRoomsOnly:
                emptyRooms = [a for a in self.plan if (a.center == '' and a.ambush == '')]
                if len(emptyRooms) == 0:
                    return False
                room = randomitem(emptyRooms, False)
                if isinstance(tossedItems[i], Monster) and dice(1,3) == 1:
                    room.ambush = tossedItems[i] # Монстр садится в засаду
                else:
                    room.center = tossedItems[i]  # Вытягиваем следующую штуку из колоды и кладем в комнату
                tossedItems[i].currentPosition = room.position

            else:
                room = randomitem(self.plan, False)
                if room.center != '':
                    if isinstance(room.center, Monster):
                        room.center.give(tossedItems[i])
                    else:
                        room.center.loot.add(tossedItems[i])
                else:
                    room.loot.add(tossedItems[i])
        return True

    def monsters(self): #Возвращает количество живых монстров, обитающих в замке в данный момент
        roomsWithMonsters = [a for a in self.plan if ((a.center != '' and isinstance(a.center, Monster))
                                                      or (a.ambush != '' and isinstance(a.ambush, Monster)))]
        return len(roomsWithMonsters)


# Еще константы
classes = {'монстр': Monster,
           'герой': Hero,
           'оружие': Weapon,
           'защита': Shield,
           'притворщик': Shapeshifter,
           'сундук': Chest,
           'вампир': Vampire,
           'берсерк': Berserk,
           'ходок': Walker,
           'растение': Plant,
           'ключ': Key,
           'карта': Map,
           'зелье': Potion,
           'руна': Rune,
           'заклинание': Spell,
           }

# Подготовка

allMonsters = readmonsters(classes)  # Читаем монстров из файла
allSpells = readspells(classes) #Читаем из файла заклинания
allWeapon = readitems('оружие', howMany, classes)
allShields = readitems('защита', howMany, classes)
allPotions = readitems('зелье', howMany, classes)
newCastle = Castle(5, 5)  # Генерируем замок
newCastle.inhabit(allMonsters, howMany['монстры'], True)  # Населяем замок монстрами
newCastle.inhabit(allWeapon, howMany['оружие'], False)
newCastle.inhabit(allShields, howMany['защита'], False)
allRunes = [Rune() for i in range(howMany['руна'])]
newCastle.inhabit(allRunes, howMany['руна'], False)
newCastle.inhabit(allPotions, howMany['зелье'], False)
newCastle.lockDoors() # Создаем запертые комнаты
map = Map()  # Прячем карту
newCastle.plan[0].visited = '+' # Делаем первую комнату посещенной
player = Hero('Артур', 'Артура', 'male', 10, 2, 1, 25, '', '', 'бьет,калечит,терзает,протыкает') # Создаем персонажа
newKey = Key() # Создаем ключ
player.pockets.append(newKey) # Отдаем ключ игроку
gameIsOn = False # Выключаем игру для того, чтобы игрок запустил ее в Телеграме

#Функция рестарта игры
def restart():
    global newCastle
    global map
    global player
    global newKey
    newCastle = None
    player = None
    newCastle = Castle(5, 5)  # Генерируем замок
    newCastle.inhabit(allMonsters, howMany['монстры'], True)  # Населяем замок монстрами
    newCastle.inhabit(allWeapon, howMany['оружие'], False)
    newCastle.inhabit(allShields, howMany['защита'], False)
    newCastle.inhabit(allRunes, howMany['руна'], False)
    newCastle.inhabit(allPotions, howMany['зелье'], False)
    newCastle.lockDoors()  # Создаем запертые комнаты
    map = Map()  # Прячем карту
    newCastle.plan[0].visited = '+'  # Делаем первую комнату посещенной
    player = Hero('Артур', 'Артура', 'male', 10, 2, 1, 25, '', '',
                  'бьет,калечит,терзает,протыкает')  # Создаем персонажа
    newKey = Key()  # Создаем ключ
    player.pockets.append(newKey)  # Отдаем ключ игроку

# Основная программа

# Запускаем бота
bot = telebot.TeleBot(TOKEN)
chat_id = 0

#Функции бота

def tprint (text, state=''):
    global bot
    global chat_id
    if state == 'off':
        markup = types.ReplyKeyboardRemove(selective=False)
    elif state == 'fight':
        canUse = []
        for i in player.pockets:
            if i.canUseInFight:
                canUse.append(i)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        item1 = types.KeyboardButton('ударить')
        item2 = types.KeyboardButton('')
        item3 = types.KeyboardButton('')
        if player.shield != '':
            item2 = types.KeyboardButton('защититься')
        if len(canUse) > 0:
            item3 = types.KeyboardButton('использовать')
        item4 = types.KeyboardButton('бежать')
        markup.add(item1, item2, item3, item4)
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
        bot.send_message(chat_id, text, reply_markup=markup)
    elif isinstance(text, list):
        final_text = ''
        for line in text:
            final_text = final_text + str(line) + '\n'
        bot.send_message(chat_id, final_text.rstrip('\n'), reply_markup=markup)

def pprint (text, width = 200, height = 200, color = '#FFFFFF'):
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
        bot.send_photo(chat_id, pic)
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
        bot.send_photo(chat_id, pic)

@bot.message_handler(commands=['start', 'старт', 's'])
def welcome(message):
    global chat_id
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Новая игра')
    itembtn2 = types.KeyboardButton('Отмена')
    if gameIsOn:
        markup.add(itembtn1, itembtn2)
        bot.reply_to(message, "Игра уже запущена.\nТы точно хочешь начать новую игру?\n", reply_markup=markup)
    else:
        markup.add(itembtn1)
        bot.reply_to(message, "Привет!\nХочешь начать игру?\n", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Новая игра')
def start_game(message):
    global gameIsOn
    gameIsOn = True
    newCastle.plan[player.currentPosition].show(player)
    newCastle.plan[player.currentPosition].map()


@bot.message_handler(func=lambda message: message.text.lower().split(' ')[0] in telegram_commands
                                          and not IN_FIGHT
                                          and not LEVEL_UP
                                          and not ENCHANTING)
def get_command(message):
    if not player.gameover('killall', howMany['монстры']):
        player.do(message.text.lower())

@bot.message_handler(func=lambda message: message.text.lower().split(' ')[0] in level_up_commands
                                          and LEVEL_UP)
def get_level_up_command(message):
    global LEVEL_UP
    global player
    a = message.text.lower().split(' ')[0]
    if a == 'здоровье':
        player.health += 3
        player.startHealth += 3
        tprint(player.name + ' получает 3 единицы здоровья.', 'off')
        LEVEL_UP = False
    elif a == 'силу':
        player.stren += 1
        player.startStren += 1
        tprint(player.name + ' увеличивает свою силу на 1.', 'off')
        LEVEL_UP = False
    elif a == '3' or a == 'ловкость':
        player.dext += 1
        player.startDext += 1
        tprint(player.name + ' увеличивает свою ловкость на 1.', 'off')
        LEVEL_UP = False
    elif a == '4' or a == 'интеллект':
        player.intel += 1
        player.startIntel += 1
        tprint(player.name + ' увеличивает свой интеллект на 1.', 'off')
        LEVEL_UP = False

@bot.message_handler(func=lambda message: message.text.lower().split(' ')[0]
                                          and ENCHANTING)
def get_enchanting_command(message):
    global ENCHANTING
    global selectedItem
    global player
    answer = message.text.lower()
    runeList = player.inpockets(Rune)
    if answer == 'отмена':
        ENCHANTING = False
        return True
    elif answer.isdigit() and int(answer) - 1 < len(runeList):
        if selectedItem.enchant(runeList[int(answer) - 1]):
            tprint(player.name + ' улучшает ' + selectedItem.name1 + ' новой руной.', 'off')
            player.pockets.remove(runeList[int(answer) - 1])
            ENCHANTING = False
            return True
        else:
            tprint('Похоже, что ' + player.name + 'не может вставить руну в ' + selectedItem.name1 + '.', 'off')
            ENCHANTING = False
            return False
    else:
        tprint(self.name + ' не находит такую руну у себя в карманах.', 'off')


@bot.message_handler(func=lambda message: message.text.lower().split(' ')[0] in fight_commands
                                          and IN_FIGHT)
def get_in_fight_command(message):
    global IN_FIGHT
    enemy = newCastle.plan[player.currentPosition].center
    tprint(player.attack(enemy, message.text))
    if IN_FIGHT:
        if enemy.run:
            IN_FIGHT = False
        elif enemy.health > 0:
            enemy.attack(player)
        else:
            tprint(player.name + ' побеждает в бою!', 'off')
            IN_FIGHT = False
            player.win(enemy)
            enemy.lose(player)

bot.polling(none_stop=True, interval=0)

while not player.gameover('killall', howMany['монстры']):
    player.do(input('Что требуется от ' + player.name1 + '? ---->'))
