#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint as dice
from telebot import types
from PIL import Image, ImageDraw, ImageFont
from random import sample as toss
from time import sleep as pause
from math import ceil
from math import sqrt
from math import floor
import json


# Функции

def readfile(filename, divide, divider='|'):
    filelines = []
    with open(filename, encoding='utf-8') as new_file:
        for line in new_file:
            if divide:
                filelines.append(line.rstrip('\n').split(divider))
            else:
                filelines.append(line.rstrip('\n'))
    return filelines


# Функция генерирует описание сторон схватки.
# На вход получает объекты сторон (например, героя и монстра), а также замок, в котором происходит схватка.
# Возвращает список, состоящий из строк, описывающих стороны схватки.
def showsides(side1, side2, castle):
    room = castle.plan[side1.currentPosition]
    message = []
    line = f'{side1.name}: сила - d{str(side1.stren)}'
    if not side1.weapon.empty:
        line += f'+d{str(side1.weapon.damage)}+{str(side1.weapon.permdamage())}'
    if not side1.shield.empty and side1.armor.empty:
        line += f', защита - d{str(side1.shield.protection)}+{str(side1.shield.permprotection())}'
    elif side1.shield.empty and not side1.armor.empty:
        line += f', защита - d{str(side1.armor.protection)}+{str(side1.armor.permprotection())}'
    elif not side1.shield.empty and not side1.armor.empty:
        line += f', защита - d{str(side1.armor.protection)}+{str(side1.armor.permprotection())} + d{str(side1.shield.protection)}+{str(side1.shield.permprotection())}'
    line += f', жизней - {str(side1.health)}. '
    message.append(line)
    if room.light:
        line = f'{side2.name}: сила - d{str(side2.stren)}'
        if not side2.weapon.empty:
            line += f'+d{str(side2.weapon.damage)}+{str(side2.weapon.permdamage())}'
        if not side2.shield.empty and side2.armor.empty:
            line += f', защита - d{str(side2.shield.protection)}+{str(side2.shield.permprotection())}'
        elif side2.shield.empty and not side2.armor.empty:
            line += f', защита - d{str(side2.armor.protection)}+{str(side2.armor.permprotection())}'
        elif not side2.shield.empty and not side2.armor.empty:
            line += f', защита - d{str(side2.armor.protection)}+{str(side2.armor.permprotection())} + d{str(side2.shield.protection)}+{str(side2.shield.permprotection())}'
        line += f', жизней - {str(side2.health)}.'
        message.append(line)
    else:
        message.append(f'В темноте кто-то есть, но {side1.name} не понимает кто это.')
    return message


# Возвращает случайные элементы списка
# list - список, из которого нужно начитать случайный элемент
# neednumber (boolean) - признак того, что кроме самого элемента нужно вернуть и его номер в списке
# howMany (integer) - число случайных элементов списка, которые нужно вернуть
# Если howMany > 1, возвращается список из howMany случайных элементов списка list. Элементы не повторяются.
def randomitem(list, neednumber=False, how_many=1):
    if not how_many or int(how_many) < 2:
        a = dice(0, len(list) - 1)
        if not neednumber:
            return list[a]
        else:
            return list[a], a
    else:
        result = []
        while how_many > 0:
            a = dice(0, len(list) - 1)
            if list[a] not in result:
                result.append(list[a])
                how_many -= 1
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


def readspells(classes):
    spellslist = readfile('spells', True, '\\')
    for i in range(len(spellslist)):
        spellslist[i] = classes[spellslist[i][0]](spellslist[i][1],
                                                  spellslist[i][2],
                                                  spellslist[i][3],
                                                  spellslist[i][4],
                                                  spellslist[i][5],
                                                  spellslist[i][6],
                                                  spellslist[i][7],
                                                  spellslist[i][8])
    return spellslist


def readitems(what_kind, how_many, classes):
    allItems = readfile('items', True, '\\')
    itemsList = []
    for i in allItems:
        if i[0] == what_kind:
            item = classes[i[0]](i[1], i[2], i[3], i[4])
            itemsList.append(item)
    while len(itemsList) < how_many[what_kind]:
        new = classes[what_kind](0)
        itemsList.append(new)
    return itemsList


def tprint(game, text, state=''):
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
        if game.player.weapon != '' and game.player.second_weapon():
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
        game.bot.send_message(game.chat_id, text, reply_markup=markup)
    elif isinstance(text, list):
        final_text = ''
        for line in text:
            final_text = final_text + str(line) + '\n'
        game.bot.send_message(game.chat_id, final_text.rstrip('\n'), reply_markup=markup)


def pprint(game, text, width=200, height=200, color='#FFFFFF'):
    pic = Image.new('RGB', (width, height), color=color)
    font = ImageFont.truetype('PTMono-Regular.ttf', size=18)
    draw_text = ImageDraw.Draw(pic)
    if isinstance(text, str):
        draw_text.text(
            (10, 10),
            text,
            font=font,
            fill='#000000'
        )
        game.bot.send_photo(game.chat_id, pic)
    elif isinstance(text, list):
        final_text = ''
        for line in text:
            final_text = final_text + str(line) + '\n'
        draw_text.text(
            (10, 10),
            final_text,
            font=font,
            fill='#000000'
        )
        game.bot.send_photo(game.chat_id, pic)


# Функция принимает на вход нормальную строку текста, слова разделены пробелами.
# Подразумевается, что строка будет перечислением чего-либо.
# На выход выдается преобразованная строка, где все слова разделены запятыми, а последнее отделяется союзом "и".
# В параметр exclude передается символ, перед которым не надо ставить запятую. Это может быть, например, скобка.
# Таким образом, строка 'один два три (четыре) пять (шесть)'
# может быть преобразована в 'один, два, три (четыре) и пять (шесть)'.

def normal_count(input_string, exclude=None):
    input_string = input_string.replace(' ', ' и ')
    if exclude:
        input_string = input_string.replace(' и ' + str(exclude), ' ' + str(exclude))
    count = input_string.count(' и ')
    input_string = input_string.replace(' и ', ', ', count - 1)
    return input_string
