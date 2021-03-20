#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint as dice
from telebot import types
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


def showsides(side1, side2, castle):
    room = castle.plan[side1.currentPosition]
    message = []
    line = side1.name + ': сила - d' + str(side1.stren)
    if side1.weapon != '':
        line += '+d' + str(side1.weapon.damage) + '+' + str(side1.weapon.permdamage())
    if side1.shield != '':
        line += ', защита - d' + str(side1.shield.protection) + '+' + str(side1.shield.permprotection())
    line += ', жизней - ' + str(side1.health) + '. '
    message.append(line)
    if room.light:
        line = side2.name + ': сила - d' + str(side2.stren)
        if side2.weapon != '':
            line += '+d' + str(side2.weapon.damage) + '+' + str(side2.weapon.permdamage())
        if side2.shield != '':
            line += ', защита - d' + str(side2.shield.protection) + '+' + str(side2.shield.permprotection())
        line += ', жизней - ' + str(side2.health) + '.'
        message.append(line)
    else:
        message.append('В темноте кто-то есть, но ' + side1.name + ' не понимает кто это.')
    return message


# Возвращает случайные элементы списка
# list - список, из которого нужно начитать случайный элемент
# neednumber (boolean) - признак того, что кроме самого элемента нужно вернуть и его номер в списке
# howMany (integer) - число случайных элементов списка, которые нужно вернуть
# Если howMany > 1, возвращается список из howMany случайных элементов списка list. Элементы не повторяются.
def randomitem(list, neednumber=False, howMany=1):
    if not howMany or int(howMany) < 2:
        a = dice(0, len(list) - 1)
        if not neednumber:
            return list[a]
        else:
            return list[a], a
    else:
        result = []
        while howMany > 0:
            a = dice(0, len(list) - 1)
            if list[a] not in result:
                result.append(list[a])
                howMany -= 1
        return result


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

def tprint (text, state=''):
    global bot
    global chat_id
    global player
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
