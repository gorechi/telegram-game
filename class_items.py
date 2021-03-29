from functions import *
from class_basic import *
from constants import *

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
        tprint(self.game, who.name + ' забирает ' + self.name1 + ' себе.')

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
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

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

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.name + ' себе.')


class Matches():
    def __init__(self, game):
        self.game = game
        self.canUseInFight = False
        self.name = 'спички'
        self.name1 = 'спички'
        self.description = 'Спички, которыми можно что-то поджечь'
        self.room = None

    def show(self):
        return self.description

    def place(self, castle, room_to_place = None):
        game = self.game
        if room_to_place:
            room = room_to_place
        else:
            done = False
            while not done:
                room = randomitem(game.newCastle.plan, False)
                if not room.locked and room.light:
                    done = True
            self.room = room
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

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


class Map():
    def __init__(self, game):
        self.game = game
        self.canUseInFight = False
        self.name = 'карта'
        self.name1 = 'карту'
        self.description = 'Карта, показывающая расположение комнат замка'

    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

    def show(self):
        return self.description

    def use(self, whoisusing, inaction=False):
        if not inaction:
            tprint(self.game, whoisusing.name + ' смотрит на карту замка.')
            self.game.newCastle.map()
            return True
        else:
            tprint(self.game, 'Во время боя это совершенно неуместно!')
            return False

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.name + ' себе.')


class Key():
    def __init__(self, game):
        self.game = game
        self.canUseInFight = False
        self.name = 'ключ'
        self.name1 = 'ключ'
        self.description = 'Ключ, пригодный для дверей и сундуков'

    def __str__(self):
        return self.description

    def show(self):
        return self.description

    def on_create(self):
        return True

    def place(self, castle, room_to_place = None):
        furniture = False
        if room_to_place:
            room = room_to_place
        else:
            unlockedRooms = [a for a in castle.plan if (not a.locked)]
            room = randomitem(unlockedRooms, False)
        if len(room.furniture) > 0:
            for i in room.furniture:
                if not i.locked:
                    furniture = i
            if furniture:
                furniture.put(self)
                return True
        room.loot.pile.append(self)

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.name + ' себе.')


class Potion():
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

    def show(self):
        return self.description

    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
            return True
        room.loot.pile.append(self)

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

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.name + ' себе.')


class Book():
    def __init__(self, game, name=''):
        self.game = game
        self.name = name

    def on_create(self):
        self.type = dice(0,2)
        description = randomitem(self.descriptions, False)
        self.name = description[0] + ' ' + self.name + ' ' + self.decorations[self.type]
        self.alt_name = description[1] + ' ' + self.name1 + ' ' + self.decorations[self.type]
        self.name1 = 'книгу'
        available_texts = []
        for i in self.texts:
            if i[0] == self.type:
                available_texts.append(i[1])
        self.text = randomitem(available_texts, False)
        self.weapon_type = self.weapon_types[self.type]
        self.armor_type = self.armor_types[self.type]
        self.shield_type = self.shield_types[self.type]
        return True

    def print_mastery(self, who):
        message = [who.name + ' теперь немного лучше знает, как использовать ' + self.weapon_type + ' оружие.']
        return message

    def place(self, castle, room_to_place = None):
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
            return True
        room.loot.pile.append(self)

    def show(self):
        return self.description

    def use(self, whoUsing, inaction = False):
        if inaction:
            tprint(self.game, 'Сейчас абсолютно не подходящее время для чтения.')
            return False
        else:
            return whoUsing.read(self)

    def __str__(self):
        return self.name

    def take(self, who=''):
        if who == '':
            return False
        who.pockets.append(self)
        tprint(self.game, who.name + ' забирает ' + self.alt_name + ' себе.')
