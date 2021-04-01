from functions import *
from constants import *


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
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if room.monster():
            monster = room.monster()
            if monster.wearArmor:
                monster.give(self)
                return True
        elif room.ambush != '':
            monster = room.ambush
            if monster.wearArmor:
                monster.give(self)
                return True
            elif len(room.furniture) > 0:
                furniture = randomitem(room.furniture, False)
                if furniture.can_contain_weapon:
                    furniture.put(self)
                    return True
        room.loot.pile.append(self)

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
        self.accumulated_damage = 0

    def on_create(self):
        return True

    def show(self):
        damage_dict = {1: 'поцарапанный',
                       2: 'потрепанный',
                       3: 'почти сломанный',
                       4: 'еле живой',
                       }
        damage = damage_dict.get(self.accumulated_damage//1)
        protectionString = str(self.protection)
        text = ''
        if self.permprotection() != 0:
            protectionString += '+' + str(self.permprotection())
        if damage:
            text += (damage + ' ')
        text += self.name + self.enchantment() + ' (' + protectionString + ')'
        return text

    def realname(self):
        damage_dict = {1: 'поцарапанный',
                       2: 'потрепанный',
                       3: 'почти сломанный',
                       4: 'еле живой',
                       }
        damage = damage_dict.get(self.accumulated_damage // 1)
        names = []
        if damage:
            name = damage + ' ' + self.name
            name1 = damage + ' ' + self.name1
        else:
            name = self.name
            name1 = self.name1
        if self.element() != 0:
            names.append(name + ' ' + elementDictionary[self.element()])
            names.append(name1 + ' ' + elementDictionary[self.element()])
        else:
            names.append(name)
            names.append(name1)
        return names

    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if room.monster():
            monster = room.monster()
            if monster.carryshield:
                monster.give(self)
                return True
        elif room.ambush != '':
            monster = room.ambush
            if monster.carryshield:
                monster.give(self)
                return True
            elif len(room.furniture) > 0:
                furniture = randomitem(room.furniture, False)
                if furniture.can_contain_weapon:
                    furniture.put(self)
                    print('Положен в мебель: ' + furniture.name)
                    return True
        room.loot.pile.append(self)

# Щит можно взять в руку. Если в руке ужесть щит, персонаж выбрасывает его и он становится частью лута комнаты.
    def take(self, who):
        if who.shield != '':
            oldShield = who.shield
        if who.removed_shield != '':
            oldShield = who.removed_shield
        if who.weapon != '':
            if who.weapon.twohanded:
                who.removed_shield = self
                message = [who.name + ' помещает ' + self.name1 + ' за спину.']
            else:
                who.shield = self
                message = [who.name + ' берет ' + self.name1 + ' в руку.']
        else:
            who.shield = self
            message = [who.name + ' берет ' + self.name1 + ' в руку.']
        if oldShield != '':
            print('old shield: ', oldShield)
            message.append('При этом он бросает ' + oldShield.realname()[1] + ' и оставляет валяться на полу.')
            who.drop(oldShield)
        tprint(self.game, message)
