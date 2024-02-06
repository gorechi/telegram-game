from random import randint

from PIL import Image, ImageDraw, ImageFont
from telebot import types


def roll(dice:list) -> int:
    """Функция имитирует бросок нескольких кубиков сразу

    Args:
        dice (list of integers): Список, состоящий из целочисленных значений размера кубиков

    Returns:
        int: Результат броска всех кубиков
    """
    result = 0 
    for i in dice:
        result += randint(1, int(i))
    return result

def readfile(filename, divide, divider='|'):
    filelines = []
    with open(filename, encoding='utf-8') as new_file:
        for line in new_file:
            if divide:
                filelines.append(line.rstrip('\n').split(divider))
            else:
                filelines.append(line.rstrip('\n'))
    return filelines


def showsides(side1, side2, castle) -> list:
    
    """
    Функция генерирует описание сторон схватки. 
    На вход получает объекты сторон (например, героя и монстра), 
    а также замок, в котором происходит схватка. 
    Возвращает список, состоящий из строк, описывающих стороны схватки.
    
    """
    
    room = side1.current_position
    message = []
    line = f'{side1.name}: сила - d{str(side1.stren)}'
    if not side1.weapon.empty:
        line += f'+d{str(side1.weapon.damage)}+{str(side1.weapon.perm_damage())}'
    if not side1.shield.empty and side1.armor.empty:
        line += f', защита - d{str(side1.shield.protection)}+{str(side1.shield.perm_protection())}'
    elif side1.shield.empty and not side1.armor.empty:
        line += f', защита - d{str(side1.armor.protection)}+{str(side1.armor.perm_protection())}'
    elif not side1.shield.empty and not side1.armor.empty:
        line += f', защита - d{str(side1.armor.protection)}+{str(side1.armor.perm_protection())} + d{str(side1.shield.protection)}+{str(side1.shield.perm_protection())}'
    line += f', жизней - {str(side1.health)}. '
    message.append(line)
    if room.light:
        line = f'{side2.name}: сила - d{str(side2.stren)}'
        if not side2.weapon.empty:
            line += f'+d{str(side2.weapon.damage)}+{str(side2.weapon.perm_damage())}'
        if not side2.shield.empty and side2.armor.empty:
            line += f', защита - d{str(side2.shield.protection)}+{str(side2.shield.perm_protection())}'
        elif side2.shield.empty and not side2.armor.empty:
            line += f', защита - d{str(side2.armor.protection)}+{str(side2.armor.perm_protection())}'
        elif not side2.shield.empty and not side2.armor.empty:
            line += f', защита - d{str(side2.armor.protection)}+{str(side2.armor.perm_protection())} + d{str(side2.shield.protection)}+{str(side2.shield.perm_protection())}'
        line += f', жизней - {str(side2.health)}.'
        message.append(line)
    else:
        message.append(f'В темноте кто-то есть, но {side1.name} не понимает кто это.')
    return message

def randomitem(list, neednumber=False, how_many:int=1):
    """Возвращает случайные элементы списка

    Args:
        list - список, из которого нужно начитать случайный элемент\n
        neednumber (boolean) - признак того, что кроме самого элемента нужно вернуть и его номер в списке\n
        howMany (integer) - число случайных элементов списка, которые нужно вернуть\n

    Returns:
        Если howMany = 1, возвращается один случайный элемент списка list\n
        Если howMany > 1, возвращается список из howMany случайных элементов списка list. Элементы не повторяются.
    """
    if len(list) == 0:
        return None
    if not how_many or how_many < 2:
        a = randint(0, len(list) - 1)
        if neednumber:
            return list[a], a
        return list[a]
    else:
        result = []
        while how_many > 0:
            a = randint(0, len(list) - 1)
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


def readitems(what_kind, how_many, classes):
    all_items = readfile('items', True, '\\')
    items_list = []
    for i in all_items:
        if i[0] == what_kind:
            item = classes[i[0]](i[1], i[2], i[3], i[4])
            items_list.append(item)
    while len(items_list) < how_many[what_kind]:
        new = classes[what_kind](0)
        items_list.append(new)
    return items_list


def generate_keyboard(keys:list, keys_in_row:int) -> list:
    for i in range(0, len(keys), keys_in_row):
        yield keys[i : i + keys_in_row]


def get_fight_markup(game) -> types.ReplyKeyboardMarkup:
    
    """ 
    Функция генерирует раскладку клавиатуры для схватки. 
    Функция получает на вход объект игры. Раскладка генерируется динамически 
    в зависимости от различных состояний героя. 
    
    """
    
    keys = []
    can_use = game.player.backpack.get_items_for_fight()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    keys.append('ударить')
    if not game.player.shield.empty:
        keys.append('защититься')
    if can_use:
        keys.append('использовать')
    keys.append('бежать')
    if not game.player.weapon.empty and game.player.second_weapon():
        keys.append('сменить оружие')
    keyboard = list(generate_keyboard(keys=keys, keys_in_row=2))
    markup.keyboard = keyboard
    return markup


def get_direction_markup() -> types.ReplyKeyboardMarkup:
    keyboard = [['идти вверх', 'идти вниз'], ['идти налево', 'идти направо']]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    markup.keyboard = keyboard
    return markup


def get_levelup_markup() -> types.ReplyKeyboardMarkup:
    keyboard = [['здоровье', 'силу'], ['ловкость', 'интеллект']]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    markup.keyboard = keyboard
    return markup    


def get_cancel_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=False)
    markup.add(types.KeyboardButton('Отмена'))
    return markup


def get_markup(game, state:str):
    if state == 'off':
        return types.ReplyKeyboardRemove(selective=False)
    elif state == 'fight':
        return get_fight_markup(game)
    elif state == 'direction':
        return get_direction_markup()
    elif state == 'levelup':
        return get_levelup_markup()
    elif state in ['enchant', 'use_in_fight']:
        return get_cancel_markup()
    else:
        return ''


def tprint(game, text, state=''):
    if not text:
        return False
    markup = get_markup(game, state)
    if isinstance(text, str):
        text_to_print = text
    elif isinstance(text, list):
        final_text = ''
        for line in text:
            if line:
                final_text = final_text + str(line) + '\n'
        text_to_print = final_text.rstrip('\n')
    game.bot.send_message(game.chat_id, text_to_print, reply_markup=markup)


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


def normal_count(input_string, exclude=None, divider=' '):
    
    """ 
    Функция принимает на вход нормальную строку текста, слова разделены пробелами.
    Подразумевается, что строка будет перечислением чего-либо.
    На выход выдается преобразованная строка, где все слова разделены запятыми, а последнее отделяется союзом "и".
    В параметр exclude передается символ, перед которым не надо ставить запятую. Это может быть, например, скобка.
    Таким образом, строка 'один два три (четыре) пять (шесть)'
    может быть преобразована в 'один, два, три (четыре) и пять (шесть)'.
    
    """
    
    input_string = input_string.replace(divider, ' и ')
    if exclude:
        input_string = input_string.replace(' и ' + str(exclude), ' ' + str(exclude))
    count = input_string.count(' и ')
    input_string = input_string.replace(' и ', ', ', count - 1)
    return input_string
