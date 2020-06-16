#!/usr/bin/python
# -*- coding: utf-8 -*-
# Импортируем необходимые модули

from random import randint as dice
from random import sample as toss
from time import sleep as pause
from math import ceil
from math import sqrt
from math import floor
import copy


# Функции

def readfile(filename, divide, divider='|'):
    filelines = []
    newfile = open(filename, encoding='utf-8')
    for line in newfile:
        if divide:
            filelines.append(line.rstrip('\n').split(divider))
        else:
            filelines.append(line.rstrip('\n'))
    newfile.close()
    return filelines


def showsides(side1, side2):
    line = side1.name + ': сила - d' + str(side1.stren)
    if side1.weapon != '':
        line += '+d' + str(side1.weapon.damage) + '+' + str(side1.weapon.permdamage())
    if side1.shield != '':
        line += ', защита - d' + str(side1.shield.protection) + '+' + str(side1.shield.permprotection())
    line += ', жизней - ' + str(side1.health) + '. '
    line += side2.name + ': сила - d' + str(side2.stren)
    if side2.weapon != '':
        line += '+d' + str(side2.weapon.damage) + '+' + str(side2.weapon.permdamage())
    if side2.shield != '':
        line += ', защита - d' + str(side2.shield.protection) + '+' + str(side2.shield.permprotection())
    line += ', жизней - ' + str(side2.health) + '.'
    return line


def randomitem(list, neednumber=False):
    a = dice(0, len(list) - 1)
    if not neednumber:
        return list[a]
    else:
        return list[a], a


def howmany(a, string):
    b = string.split(',')
    a1, a2 = int(a % 10), int(a % 100)
    if a1 == 1 and a2 != 11:
        return str(a) + ' ' + b[0]
    elif 1 < a1 < 5 and (a2 < 12 or a2 > 14):
        return str(a) + ' ' + b[1]
    else:
        return str(a) + ' ' + b[2]

# Константы

howManyMonsters = 10
howManyWeapon = 10
howManyShields = 10
howManyPotions = 8
howManyRunes = 10
decor1 = readfile('decorate1', False)
decor2 = readfile('decorate2', False)
decor3 = readfile('decorate3', False)
decor4 = readfile('decorate4', False)
chestType = ["Обычный",
             "Кованный",
             "Большой",
             "Деревянный",
             "Железный",
             "Маленький",
             "Старинный",
             "Антикварный",
             "Странный",
             "Обычный"]
weakness = {'огонь': "магия", "магия": "воздух", "воздух": "земля", "земля": "вода", "вода": "огонь"}
elementDictionary = {1: 'огня', 2: 'пламени', 3: 'воздуха', 4: 'дыма', 6: 'ветра', 7: 'земли', 8: 'лавы', 10: 'пыли',
                     12: 'воды', 13: 'пара', 14: 'камня', 15: 'дождя', 19: 'грязи', 24: 'потопа'}

# Описываем классы

class Item:
    def __init__(self):
        self.name = 'штука'
        self.name1 = 'штуку'
        self.canUseInFight = False
        self.description = self.name

    def take(self, who=''):
        who.pockets.append(self)
        print(who.name + ' забирает ' + self.name + ' себе.')

    def use(self, whoisusing, inaction=False):
        print(whoisusing.name + ' не знает, как использовать такие штуки.')

    def show(self):
        return self.description

class Rune:
    def __init__(self):
        self.damage = 4 - floor(sqrt(dice(1, 15)))
        self.defence = 3 - floor(sqrt(dice(1, 8)))
        self.elements = [1, 3, 7, 12]
        self.element = self.elements[dice(0,3)]
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
        print(who.name + ' забирает ' + self.name1 + ' себе.')

    def show(self):
        return self.name + ' ' + elementDictionary[self.element] + ' - урон + ' + str(self.damage) + \
               ' или защита + ' + str(self.defence)


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
        self.element = ''

    def __str__(self):
        return 'weapon'

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
                element += i.element()
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
            print(who.name + ' берет ' + self.name1 + ' в руку.')
        else:
            who.pockets.append(self)
            print(who.name + ' забирает ' + self.name1 + ' себе.')

    def show(self):
        damageString = str(self.damage)
        if self.permdamage() != 0:
            damageString += '+' + str(self.permdamage())
        return self.name + self.enchantment() + ' (' + damageString + ')'

    def use(self, whoUsing, inaction = False):
        if whoUsing.weapon == '':
            whoUsing.weapon = self
        else:
            whoUsing.pockets.append(whoUsing.weapon)
            whoUsing.weapon = self
            whoUsing.pockets.remove(self)
        print(whoUsing.name + ' теперь использует ' + self.name1 + ' в качестве оружия!')


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
        self.element = ''

    def __str__(self):
        return 'shield'

    def permprotection(self):
        protection = 0
        if len(self.runes) in [1, 2]:
            for rune in self.runes:
                protection += rune.damage
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
                element += i.element()
            return ' ' + elementDictionary[element]

    def protect(self, who):
        multiplier = 1
        if who.weapon and who.weapon.element and self.element and weakness[self.element] == who.weapon.element:
            multiplier = 1.5
        elif who.weapon and who.weapon.element and self.element and weakness[who.weapon.element] == self.element:
            multiplier = 0.67
        if who.hide:
            who.hide = False
            return self.protection + self.permprotection()
        else:
            return ceil((dice(1, self.protection) + self.permprotection())*multiplier)

    def take(self, who):
        if who.shield == '':
            who.shield = self
            print(who.name + ' берет ' + self.name1 + ' в руку.')
        else:
            player.pockets.append(self)
            print(who.name + ' забирает ' + self.name1 + ' себе.')

    def show(self):
        protectionString = str(self.protection)
        if self.permprotection() != 0:
            protectionString += '+' + str(self.permprotection())
        return self.name + self.enchantment() + ' (' + protectionString + ')'

    def use(self, whoUsing):
        if whoUsing.shield == '':
            whoUsing.shield = self
        else:
            whoUsing.pockets.append(whoUsing.shield)
            whoUsing.shield = self
            whoUsing.pockets.remove(self)
        print(whoUsing.name + ' теперь использует ' + self.name1 + ' в качестве защиты!')


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
            print(whoisusing.name + ' смотрит на карту замка.')
            newCastle.map()
            return True
        else:
            print('Во время боя это совершенно неуместно!')
            return False


class Key(Item):
    def __init__(self):
        super().__init__()
        self.name = 'ключ'
        self.name1 = 'ключ'
        self.description = 'Ключ, пригодный для дверей и сундуков'

    def __str__(self):
        return 'key'


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
                print (whoUsing.name + ' увеличивает свое максмальное здоровье на ' + str(self.effect) + ' до ' + str(whoUsing.health) + '.')
                return True
            elif self.type == 2:
                whoUsing.stren += self.effect
                whoUsing.startStren += self.effect
                print (whoUsing.name + ' увеличивает свою силу на ' + str(self.effect) + ' до ' + str(whoUsing.stren) + '.')
                return True
            elif self.type == 4:
                whoUsing.dext += self.effect
                whoUsing.startDext += self.effect
                print (whoUsing.name + ' увеличивает свою ловкость на ' + str(self.effect) + ' до ' + str(whoUsing.dext) + '.')
                return True
            elif self.type == 6:
                whoUsing.intel += self.effect
                whoUsing.startIntel += self.effect
                print (whoUsing.name + ' увеличивает свой интеллект на ' + str(self.effect) + ' до ' + str(whoUsing.intel) + '.')
                return True
            else:
                print('Это зелье можно использовать только в бою!')
                return False
        else:
            if self.type == 0:
                if (whoUsing.startHealth - whoUsing.health) < self.effect:
                    heal = dice(1, (whoUsing.startHealth - whoUsing.health))
                else:
                    heal = dice(1, self.effect)
                whoUsing.health += heal
                print (whoUsing.name + ' восполняет ' + howmany(heal, 'единицу жизни,единицы жизни,единиц жизни'))
                return True
            elif self.type == 3:
                whoUsing.stren += self.effect
                print ('На время боя ' + whoUsing.name + ' увеличивает свою силу на ' + str(self.effect) + ' до ' + str(whoUsing.stren) + '.')
                return True
            elif self.type == 5:
                whoUsing.dext += self.effect
                print ('На время боя ' + whoUsing.name + ' увеличивает свою ловкость на ' + str(self.effect) + ' до ' + str(whoUsing.dext) + '.')
                return True
            elif self.type == 7:
                whoUsing.intel += self.effect
                print ('На время боя ' + whoUsing.name + ' увеличивает свой интеллект на ' + str(self.effect) + ' до ' + str(whoUsing.intel) + '.')
                return True
            else:
                print('Это зелье нельзя использовать в бою!')
                return False
    def __str__(self):
        return 'potion'


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
        return 'chest'


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
        return 'money'

    def take(self, luckyOne):
        luckyOne.money.howmanymoney += self.howmanymoney
        print(luckyOne.name + ' забрал ' + howmany(self.howmanymoney, 'монету,монеты,монет'))

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
        self.directionsDict = {'наверх': (0 - newCastle.rooms), 'направо': 1, 'вправо': 1, 'налево': (0 - 1), 'лево': (0 - 1),
                          'влево': (0 - 1), 'вниз': newCastle.rooms, 'низ': newCastle.rooms, 'вверх': (0 - newCastle.rooms), 'верх': (0 - newCastle.rooms), 'право': 1}
        self.doorsDict = {'наверх': 0, 'направо': 1, 'вправо': 1, 'право': 1, 'налево': 3, 'влево': 3, 'лево': 3, 'вниз': 2, 'низ': 2, 'вверх': 0, 'верх': 0}

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

    def attack(self, target):
        self.run = False
        if self.rage > 1:
            rage = dice(2, self.rage)
        else:
            rage = 1
        meleAttack = dice(1, self.stren) * rage
        print(showsides(self, target))
        canUse = []
        for i in self.pockets:
            if i.canUseInFight:
                canUse.append(i)

        line = self.name + ' может (у)дарить'
        if self.shield != '':
            line += ', (з)ащититься'
        if len(canUse) > 0:
            line += ', (и)спользовать'
        line += ' или (б)ежать ---->'
        while True:
            action = input(line)
            if action == '' or action == 'у' or action == 'ударить':
                self.rage = 0
                if self.weapon != '':
                    weaponAttack = self.weapon.attack()
                    if target.shield !='':
                        if target.shield.element != '' and self.weapon.element != '':
                            if target.shield.element == weakness[self.weapon.element]:
                                weaponAttack += weaponAttack // 2
                    string1 = self.name + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name + ' и наносит ' + str(
                        meleAttack) + '+' + howmany(weaponAttack, 'единицу,единицы,единиц') + ' урона. '
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
                self.hide = True
                self.rage += 1
                return (self.name + ' уходит в глухую защиту, терпит удары и накапливает ярость.')
            elif action == 'б' or action == 'бежать' or action == 'убежать':
                a = dice(1, 2)
                if a == 1 and self.weapon != '':
                    print('Убегая ' + self.name + ' роняет из рук ' + self.weapon.name)
                    if target.weapon == '' and target.carryweapon:
                        target.weapon = self.weapon
                    else:
                        newCastle.plan[self.currentPosition].loot.add(self.weapon)
                    self.weapon = ''
                elif a == 2 and self.shield != '':
                    print('Убегая ' + self.name + ' роняет из рук ' + self.shield.name)
                    if target.shield == '' and target.carryshield:
                        target.shield = self.shield
                    else:
                        newCastle.plan[self.currentPosition].loot.add(self.shield)
                    self.shield = ''
                a = dice(0, len(self.pockets))
                for i in range(a):
                    b = dice(0, len(self.pockets) - 1)
                    print(self.name + ' не замечает, как из его карманов вываливается ' + self.pockets[b].name)
                    newCastle.plan[self.currentPosition].loot.add(self.pockets[b])
                    self.pockets.pop(b)
                self.run = True
                return self.name + ' сбегает с поля боя.'
            elif (action == 'и' or action == 'использовать') and len(canUse) > 0:
                print('Во время боя ' + self.name + ' может использовать:')
                for i in self.pockets:
                    if i.canUseInFight:
                        print(i.name)
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
                        print('Что-то не выходит')

    def show(self):
        if self.weapon != '':
            string1 = ', а {0} в его руке добавляет к ней еще {1}+{2}.'.format(self.weapon.name, self.weapon.damage,
                                                                               self.weapon.permdamage())
        else:
            string1 = ' и он предпочитает сражаться голыми руками.'
        if self.shield != '':
            string2 = 'Его защищает ' + self.shield.name + ' (' + str(self.shield.protection) + '+' + str(
                self.shield.permprotection()) + ')'
        else:
            string2 = 'У него нет защиты'
        print(
            '{0} - это смелый герой {7} уровня. Его сила - {1}{2} {3} и сейчас у него {4} здоровья, что составляет {5}% от максимально возможного.\n{0} имеет при себе {6} золотом.'.format(
                self.name, self.stren, string1, string2, howmany(self.health, 'единица,единицы,единиц'),
                self.health * 100 // self.startHealth, howmany(self.money.howmanymoney, 'монету,монеты,монет'),
                self.level))

    def defence(self, attacker):
        if self.shield == '':
            return 0
        else:
            defence = self.shield.protect(self)
            if attacker.weapon !='':
                if attacker.weapon.element != '' and self.shield.element != '':
                    if attacker.weapon.element == weakness[self.shield.element]:
                        defence += defence // 2
            return defence

    def lose(self, winner):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.currentPosition = 0
        pause(2)
        print('После поражения в схватке ' + self.name + ' очнулся у входа в замок.')

    def win(self, loser):
        self.health = self.startHealth
        self.stren = self.startStren
        self.dext = self.startDext
        self.intel = self.startIntel
        self.wins += 1
        print(self.name + ' получает ' + howmany(loser.exp, 'единицу,единицы,единиц') + ' опыта!')
        self.exp += loser.exp
        if self.exp > self.levels[self.level]:
            self.levelup()

    def levelup(self):
        print(self.name, ' получает новый уровень!')
        while True:
            a = input('Что необходимо прокачать: (1)здоровье, (2)силу, (3)ловкость или 4(интеллект)? ---->')
            if a == '1' or a == 'здоровье':
                self.health += 3
                self.startHealth += 3
                print(self.name + ' получает 3 единицы здоровья.')
                break
            elif a == '2' or a == 'силу':
                self.stren += 1
                self.startStren += 1
                print(self.name + ' увеличивает свою силу на 1.')
                break
            elif a == '3' or a == 'ловкость':
                self.dext += 1
                self.startDext += 1
                print(self.name + ' увеличивает свою ловкость на 1.')
                break
            elif a == '4' or a == 'интеллект':
                self.intel += 1
                self.startIntel += 1
                print(self.name + ' увеличивает свой интеллект на 1.')
                break
        self.level += 1

    def gameover(self, goaltype, goal):
        if goaltype == 'killall':
            if newCastle.monsters() == 0:
                print(self.name + ' убил всех монстров в замке и выиграл в этой игре!')
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
            print(self.name + ' осматривает свои карманы и обнаруживает в них:')
            for i in range(len(self.pockets)):
                print(str(i+1) + ': ' + self.pockets[i].show())
            print(self.money.show())
        elif a in self.directionsDict.keys():
            if newCastle.plan[self.currentPosition].doors[self.doorsDict[a]] == 0:
                print (self.name + ' осматривает стену и не находит ничего заслуживающего внимания.')
            else:
                print(self.name + ' заглядывает в замочную скважину и ' + newCastle.plan[self.directionsDict[a]].showThroughKeyHole(self))

        if newCastle.plan[self.currentPosition].center != '':
            if (a == newCastle.plan[self.currentPosition].center.name or a == newCastle.plan[
                self.currentPosition].center.name1 or a == newCastle.plan[self.currentPosition].center.name[
                0]) and isinstance(newCastle.plan[self.currentPosition].center, Monster):
                print(showsides(self, newCastle.plan[self.currentPosition].center))

        if self.weapon != '':
            if a == self.weapon.name or a == self.weapon.name1 or a == 'оружие':
                print(self.weapon.show())
        if self.shield != '':
            if a == self.shield.name or a == self.shield.name1 or a == 'защиту':
                print(self.shield.show())

        if len(self.pockets) > 0:
            for i in self.pockets:
                if a == i.name or a == i.name1:
                    print(i.show())

    def go(self, direction):
        if direction not in self.directionsDict.keys():
            print(self.name + ' не знает такого направления!')
            return False
        elif newCastle.plan[self.currentPosition].doors[self.doorsDict[direction]] == 0:
            print('Там нет двери. ' + self.name + ' не может туда пройти!')
            return False
        elif newCastle.plan[self.currentPosition].doors[self.doorsDict[direction]] == 2:
            print('Эта дверь заперта. ' + self.name + ' не может туда пройти, нужен ключ!')
            return False
        else:
            self.currentPosition += self.directionsDict[direction]
            newCastle.plan[self.currentPosition].visited = '+'
            self.lookaround()
            if newCastle.plan[self.currentPosition].center != '':
                if newCastle.plan[self.currentPosition].center.agressive:
                    fight(newCastle.plan[self.currentPosition].center, self)
            return True

    def fight(self, enemy):
        if (newCastle.plan[self.currentPosition].center == '' or (
                            newCastle.plan[self.currentPosition].center.name != enemy and newCastle.plan[
                        self.currentPosition].center.name1 != enemy and
                        newCastle.plan[self.currentPosition].center.name[
                            0] != enemy)) and enemy != '':
            print(self.name + ' не может атаковать. В комнате нет такого существа.')
            return False
        elif str(newCastle.plan[self.currentPosition].center) != 'monster':
            print('Не нужно кипятиться. Тут некого атаковать')
        else:
            fight(self, newCastle.plan[self.currentPosition].center)
            return True

    def search(self, item=''):
        if str(newCastle.plan[self.currentPosition].center) == 'monster':
            print(newCastle.plan[self.currentPosition].center.name + " мешает толком осмотреть комнату.")
        elif newCastle.plan[self.currentPosition].ambush != '' and item == '':
            ambusher = newCastle.plan[self.currentPosition].ambush
            print ('Неожиданно из засады выскакивает ' + ambusher.name + ' и нападает на ' + self.name1)
            newCastle.plan[self.currentPosition].center = ambusher
            newCastle.plan[self.currentPosition].ambush = ''
            fight(self, newCastle.plan[self.currentPosition].center)
        else:
            if item == '' and newCastle.plan[self.currentPosition].loot != '' and len(
                    newCastle.plan[self.currentPosition].loot.pile) > 0:
                print('В комнате есть:')
                for i in newCastle.plan[self.currentPosition].loot.pile:
                    print(i.name)
            elif item == '':
                print('В комнате нет ничего интересного.')

    def take(self, item='все'):
        currentLoot = newCastle.plan[self.currentPosition].loot
        if currentLoot == '':
            print('Здесь нечего брать.')
            return False
        elif item == 'все' or item == 'всё' or item == '':
            for i in currentLoot.pile:
                i.take(self)
            newCastle.plan[self.currentPosition].loot = ''
            return True
        else:
            for i in currentLoot.pile:
                if i.name == item or i.name1 == item:
                    i.take(self)
                    currentLoot.pile.remove(i)
                    return True
        print('Такой вещи здесь нет.')
        return False

    def open(self, item=''):
        whatIsInRoom = newCastle.plan[self.currentPosition].center
        if item == '' or (not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0):
            if whatIsInRoom == '':
                print('В комнате нет вещей, которые можно открыть.')
                return False
            elif not isinstance(whatIsInRoom, Chest):
                print('Пожалуй, ' + self.name + ' не сможет это открыть.')
                return False
            elif whatIsInRoom.opened:
                print('Этот ' + whatIsInRoom.name1 + ' уже открыт. Зачем его открывать во второй раз?')
                return False
            elif whatIsInRoom.locked:
                key = False
                for i in self.pockets:
                    if isinstance(i, Key):
                        key = i
                if key:
                    self.pockets.remove(key)
                    whatIsInRoom.locked = False
                    print (self.name + ' отпирает сундук ключом.')
                else:
                    print ('Чтобы открыть этот сундук нужен ключ')
            if not whatIsInRoom.locked:
                print(self.name + ' открывает ' + whatIsInRoom.name)
                newCastle.plan[self.currentPosition].loot.pile += whatIsInRoom.loot.pile
                if len(whatIsInRoom.loot.pile) > 0:
                    print(self.name + ' роется в сундуке и обнаруживает в нем:')
                    for i in whatIsInRoom.loot.pile:
                        print(i.name1)
                    print('Все эти вещи теперь разбросаны по всей комнате.')
                    whatIsInRoom.loot.pile = []
                else:
                    print('В сундуке пусто.')
                whatIsInRoom.opened = True
                whatIsInRoom.name = 'открытый пустой ' + whatIsInRoom.name
                whatIsInRoom.inside = ''
                return True
        else:
            key = False
            for i in self.pockets:
                if isinstance(i, Key):
                    key = i
            if not self.doorsDict.get(item, False) and self.doorsDict.get(item, True) != 0:
                print(self.name + ' не может это открыть.')
                return False
            elif newCastle.plan[self.currentPosition].doors[self.doorsDict[item]] != 2:
                print('В той стороне нечего открывать.')
                return False
            elif not key:
                print('Нужен ключ.')
                return False
            else:
                self.pockets.remove(key)
                newCastle.plan[self.currentPosition].doors[self.doorsDict[item]] = 1
                j = self.doorsDict[item] + 2 if (self.doorsDict[item] + 2) < 4 else self.doorsDict[item] - 2
                newCastle.plan[self.currentPosition + self.directionsDict[item]].doors[j] = 1
                print(self.name + ' открывает дверь.')

    def use(self, item='', infight=False):
        if item == '':
            print(self.name + ' не понимает, что ему надо использовать.')
        elif item.isdigit():
            if int(item)-1 <= len(self.pockets):
                i = self.pockets[int(item)-1]
                if isinstance(i, Potion) and i.use(self, inaction=False):
                    self.pockets.remove(i)
                elif not isinstance(i, Potion):
                    i.use(self, inaction=False)
                return True
            else:
                print(self.name + ' не нашел такой вещи у себя в карманах.')
                return False
        else:
            for i in self.pockets:
                if i.name == item or i.name1 == item:
                    if isinstance(i, Potion)  and i.use(self, inaction = False):
                        self.pockets.remove(i)
                    else:
                        i.use(self, inaction = False)
                    return True
            print(self.name + ' не нашел такой вещи у себя в карманах.')

    def enchant(self, item=''):
        selectedItem = ''
        runeList = self.inpockets(Rune)
        if len(runeList) == 0:
            print(self.name + 'не может ничего улучшать. В карманах не нашлось ни одной руны.')
            return False
        if item == '':
            print(self.name + ' не понимает, что ему надо улучшить.')
            return False
        elif item == 'оружие' and self.weapon != '':
            selectedItem = self.weapon
        elif item in ['защиту', 'защита'] and self.shield != '':
            selectedItem = self.shield
        elif item.isdigit() and int(item)-1 <= len(self.pockets):
            selectedItem = self.pockets[int(item)-1]
        else:
            for i in self.pockets:
                if i.name == item or i.name1 == item:
                    selectedItem = i
                else:
                    print(self.name + ' не нашел такой вещи у себя в карманах.')
                    return False
        if selectedItem != '' and isinstance(selectedItem, Weapon) or isinstance(selectedItem, Shield):
            print(self.name + ' может использовать следующие руны:')
            for rune in runeList:
                print(str(runeList.index(rune)+1) + ': ' + str(rune))
            print('Введите "отмена" для прекрашения улучшения')
            while True:
                answer = input('Какую по номеру руну выберет ' + player.name1 + '? ---->')
                if answer == 'отмена':
                    return False
                elif answer.isdigit() and int(answer)-1 <= len(runeList):
                    if selectedItem.enchant(runeList[int(answer)-1]):
                        return True
                    else:
                        print('Похоже, что ' + self.name + 'не может вставить руну в ' + selectedItem.name1 + '.')
                        return False
                else:
                    print(self.name + ' не находит такую руну у себя в карманах.')
        else:
            print(self.name + ' не может улучшить эту вещь.')
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
            print(self.name + " может:")
            for i in commandDict.keys():
                print(i)
            return True
        c = commandDict.get(fullCommand[0], False)
        if not c:
            print('Такого ' + self.name + ' не умеет!')
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
        elif carryweapon == 'False':
            self.carryweapon = False
        if carryshield == 'True':
            self.carryshield = True
        elif carryshield == 'False':
            self.carryshield = False
        if agressive == 'True':
            self.agressive = True
        elif agressive == 'False':
            self.agressive = False
        self.exp = self.stren * dice(1, 10) + dice(1, self.health)

    def __str__(self):
        return 'monster'

    def give(self, item):
        if isinstance(item, Weapon) and self.weapon == '':
            self.weapon = item
        elif isinstance(item, Shield) and self.shield == '':
            self.shield = item
        else:
            self.loot.add(item)

    def action(self):
        if self.weapon == '':
            return randomitem(self.actions)
        else:
            return randomitem(self.weapon.actions)

    def attack(self, target):
        meleAttack = dice(1, self.stren)
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            string1 = self.name + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name \
                      + ' и наносит ' + str(meleAttack) + '+' \
                      + howmany(weaponAttack, 'единицу,единицы,единиц') + ' урона. '
        else:
            weaponAttack = 0
            string1 = self.name + ' бьет ' + target.name1 + ' не используя оружия и наносит ' + howmany(
                meleAttack, 'единицу,единицы,единиц') + ' урона. '
        targetDefence = target.defence(self)
        if (weaponAttack + meleAttack - targetDefence) > 0:
            totalDamage = weaponAttack + meleAttack - targetDefence
            if targetDefence == 0:
                string2 = target.name + ' беззащитен и теряет ' + howmany(totalDamage, 'жизнь,жизни,жизней') + '.'
            else:
                string2 = target.name + ' использует для защиты ' + target.shield.name + ' и теряет ' \
                          + howmany(totalDamage, 'жизнь,жизни,жизней') + '.'
        else:
            totalDamage = 0
            string2 = self.name + ' не смог пробить защиту ' + target.name1 + '.'
        target.health -= totalDamage
        return string1 + string2

    def defence(self, attacker):
        if self.shield == '':
            return 0
        else:
            return self.shield.protect(self)

    def lose(self, winner):
        result = dice(1, 10)
        print('RESULT = ' + str(result))
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
            print('weaknessAmount = ' + str(weaknessAmount))
            illAmount = ceil(self.startHealth * 0.4)
            print('illAmount = ' + str(illAmount))
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
                    print(aliveString)
                    where.center = ''
            else:
                aliveString += 'получает ранение в ногу и не может двигаться, теряя при этом '  \
                               + howmany(weaknessAmount, 'единицу,единицы,единиц') + ' силы и ' \
                               + howmany(illAmount, 'жизнь,жизни,жизней') + '.'
                self.stren -= weaknessAmount
                self.health = self.startHealth - illAmount
                print(aliveString)

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
            print(
                self.name + ' меняет форму и становится точь в точь как ' + attacker.name + '. У него теперь сила ' + str(
                    self.stren) + weaponString)
        if self.shield == '':
            return 0
        else:
            return self.shield.protect(self)

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
        meleAttack = dice(1, self.stren)
        if self.weapon != '':
            weaponAttack = self.weapon.attack()
            string1 = self.name + ' ' + self.action() + ' ' + target.name1 + ' используя ' + self.weapon.name + ' и наносит ' + howmany(
                meleAttack, 'единицу,единицы,единиц') + '+' + str(weaponAttack) + ' урона. '
        else:
            weaponAttack = 0
            string1 = self.name + ' ' + self.action() + ' ' + target.name1 + ' не используя оружия и наносит ' + howmany(
                meleAttack, 'единицу,единицы,единиц') + ' урона. '
        targetDefence = target.defence(self)
        if (weaponAttack + meleAttack - targetDefence) > 0:
            totalDamage = weaponAttack + meleAttack - targetDefence
        else:
            totalDamage = 0
        if totalDamage == 0:
            string2 = self.name + ' не смог пробить защиту ' + target.name1 + '.'
        elif targetDefence == 0:
            string2 = target.name + ' беззащитен и теряет ' + howmany(totalDamage,
                                                                      'жизнь,жизни,жизней') + '.' + self.name + ' высасывает ' + str(
                totalDamage // 2) + ' себе.'
        else:
            string2 = target.name + ' использует для защиты ' + target.shield.name + ' и теряет ' + howmany(totalDamage,
                                                                                                            'жизнь,жизни,жизней') + '.' + self.name + ' высасывает ' + str(
                totalDamage // 2) + ' себе.'
        target.health -= totalDamage
        self.health += totalDamage // 2
        return string1 + string2


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

    def show(self, player):
        if self.center == '':
            whoIsHere = 'Не видно ничего интересного.'
        else:
            whoIsHere = self.decoration3 + ' ' + self.center.state + ' ' + self.center.name + '.'
        print(player.name + ' попадает в {0} комнату {1}. {2} {3}'.format(self.decoration1,
                                                                          self.decoration2,
                                                                          whoIsHere,
                                                                          self.decoration4))

    def showThroughKeyHole(self, who):
        if self.center == '':
            return 'не может ничего толком разглядеть.'
        else:
            return self.center.keyHole

    def map(self):
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '\u01C1', '1': ' ', '2': '|'}
        string1 = '=={0}=='.format(doorsHorizontal[str(self.doors[0])])
        string2 = '\u01C1   \u01C1'
        string3 = '{0} '.format(doorsVertical[str(self.doors[3])])
        if self.center != '':
            string3 += self.center.name[0]
        else:
            string3 += ' '
        string3 += ' {0}'.format(doorsVertical[str(self.doors[1])])
        string4 = '=={0}=='.format(doorsHorizontal[str(self.doors[2])])
        print(string1 + '\n' + string2 + '\n' + string3 + '\n' + string2 + '\n' + string4)
        return True

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

    def map(self):
        f = self.floors
        r = self.rooms
        doorsHorizontal = {'0': '=', '1': ' ', '2': '-'}
        doorsVertical = {'0': '\u01C1', '1': ' ', '2': '|'}
        print('======' * r + '=')
        for i in range(f):
            print('\u01C1' + '     \u01C1' * r)
            line1 = '\u01C1'
            line2 = ''
            for j in range(r):
                a = player.name[0] if player.currentPosition == i * r + j else self.plan[i*r+j].visited
                line1 += '  {0}  {1}'.format(a, doorsVertical[str(self.allDoors[i * r + j][1])])
                line2 += '==={0}=='.format(doorsHorizontal[str(self.allDoors[i * r + j][2])])
            print(line1)
            print('\u01C1' + '     \u01C1' * r)
            print(line2 + '=')

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
           'растение': Plant,
           'ключ': Key,
           'карта': Map,
           'зелье': Potion,
           'руна': Rune,
           'заклинание': Spell}


# Еще функции

def readmonsters():
    monsterslist = readfile('monsters', True, '\\')
    for i in range(len(monsterslist)):
        monsterslist[i] = classes[monsterslist[i][0]](monsterslist[i][1], monsterslist[i][2], monsterslist[i][3],
                                                      monsterslist[i][4], monsterslist[i][5], monsterslist[i][6],
                                                      monsterslist[i][7], monsterslist[i][8])
    return monsterslist

def readspells():
    spellslist = readfile('spells', True, '\\')
    for i in range(len(spellslist)):
        spellslist[i] = classes[spellslist[i][0]](spellslist[i][1], spellslist[i][2], spellslist[i][3],
                                                      spellslist[i][4], spellslist[i][5], spellslist[i][6],
                                                      spellslist[i][7], spellslist[i][8])
    return spellslist


def readitems(whatkind):
    allItems = readfile('items', True, '\\')
    allWeapons = []
    allShields = []
    allPotions = []
    itemTypes = {'оружие': allWeapons, 'защита': allShields, 'зелье': allPotions}
    howMany = {'оружие': howManyWeapon, 'защита': howManyShields, 'зелье': howManyPotions}
    for i in allItems:
        if i[0] == whatkind:
            item = classes[i[0]](i[1], i[2], i[3], i[4])
            itemTypes[i[0]].append(item)
    while len(itemTypes[whatkind]) < howMany[whatkind]:
        new = classes[whatkind](0)
        itemTypes[whatkind].append(new)
    return itemTypes[whatkind]


def fight(side1, side2):
    whoWon = ''
    whoFirst = dice(1, 2)
    if whoFirst == 2:
        side1, side2 = side2, side1
    print(side1.name + ' начинает схватку!')
    while whoWon == '':
        print(side1.attack(side2))
        if side1.run:
            break
        elif side2.health > 0:
            side1, side2 = side2, side1
        else:
            print(side1.name + ' побеждает в бою!')
            side1.win(side2)
            side2.lose(side1)
            break
        pause(1)

    return whoWon

def createchests(a, money, probability):
    list = []
    for i in range(a):
        name = randomitem(chestType) + ' сундук'
        newchest = Chest(name)
        newLoot = Loot()
        newchest.loot = newLoot
        if dice (1,4) == 1:
            newchest.locked = True
            veryNewKey = Key()
            hide(veryNewKey)
        if dice(1, 100) <= probability:
            newchest.inside = []
            newMoney = Money(dice(1, money))
            newchest.loot.pile.append(newMoney)
        else:
            newchest.loot.pile = []
        list.append(newchest)
    return list

def hide (item):
    while True:
        b = randomitem(newCastle.plan)
        if not b.locked:
            if b.center == '':
                b.loot.pile.append(item)
            else:
                b.center.loot.pile.append(item)
            break
    return True

def lockDoors():
    howManyLockedRooms = len(newCastle.plan) // 8
    for i in range(howManyLockedRooms):
        while True:
            a = randomitem(newCastle.plan)
            if a != newCastle.plan[0]:
                newMoney = Money(dice(25, 75))
                a.lock(2)
                if a.center == '':
                    a.loot.pile.append(newMoney)
                else:
                    a.center.loot.pile.append(newMoney)
                newKey = Key()
                hide (newKey)
                break
    return True

# Подготовка
allMonsters = readmonsters()  # Читаем монстров из файла
allSpells = readspells() #Читаем из файла заклинания
allWeapon = readitems('оружие')
allShields = readitems('защита')
allPotions = readitems('зелье')
newCastle = Castle(5, 5)  # Генерируем замок
newCastle.inhabit(allMonsters, howManyMonsters, True)  # Населяем замок монстрами
howManyChests = len(newCastle.plan) // 5 + 1
allChests = createchests(howManyChests, 50, 50)  # Создаем сундуки
newCastle.inhabit(allChests, howManyChests, True)  # Расставляем сундуки
newCastle.inhabit(allWeapon, howManyWeapon, False)
newCastle.inhabit(allShields, howManyShields, False)
allRunes = [Rune() for i in range(howManyRunes)]
newCastle.inhabit(allRunes, howManyRunes, False)
newCastle.inhabit(allPotions, howManyPotions, False)
lockDoors()  # Создаем запертые комнаты
map = Map()  # Прячем карту
newCastle.plan[0].visited = '+'
Arthur = Hero('Артур', 'Артура', 'male', 10, 2, 1, 25, '', '', 'бьет,калечит,терзает,протыкает')
randomSword = Weapon(0)
player = Arthur
newKey = Key()
player.pockets.append(newKey)

# Основная программа

newCastle.plan[player.currentPosition].show(player)
newCastle.plan[player.currentPosition].map()
while not player.gameover('killall', howManyMonsters):
    player.do(input('Что требуется от ' + player.name1 + '? ---->'))
