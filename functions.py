#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint as dice
from random import sample as toss
from time import sleep as pause
from math import ceil
from math import sqrt
from math import floor

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

def readmonsters(classes):
    monsterslist = readfile('monsters', True, '\\')
    for i in range(len(monsterslist)):
        monsterslist[i] = classes[monsterslist[i][0]](monsterslist[i][1], monsterslist[i][2], monsterslist[i][3],
                                                      monsterslist[i][4], monsterslist[i][5], monsterslist[i][6],
                                                      monsterslist[i][7], monsterslist[i][8])
    return monsterslist

def readspells(classes):
    spellslist = readfile('spells', True, '\\')
    for i in range(len(spellslist)):
        spellslist[i] = classes[spellslist[i][0]](spellslist[i][1], spellslist[i][2], spellslist[i][3],
                                                      spellslist[i][4], spellslist[i][5], spellslist[i][6],
                                                      spellslist[i][7], spellslist[i][8])
    return spellslist


def readitems(whatkind, howMany, classes):
    allItems = readfile('items', True, '\\')
    allWeapons = []
    allShields = []
    allPotions = []
    itemTypes = {'оружие': allWeapons, 'защита': allShields, 'зелье': allPotions}
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
