from functions import *
from constants import *
from settings import *

class Weapon:
    def __init__(self, game, name='', name1='оружие', damage=1, actions='бьет,ударяет', empty=False):
        self.game = game
        if name != 0:
            self.name = name
            self.damage = int(damage)
            self.name1 = name1
            self.twohanded = False
        else:
            n1 = [[['Большой', 'Большой'], ['Большая', 'Большую'], ['Большое', 'Большое']],
                       [['Малый', 'Малый'], ['Малая', 'Малую'], ['Малое', 'Малое']],
                       [['Старый', 'Старый'], ['Старая', 'Старую'], ['Старое', 'Старое']],
                       [['Тяжелый', 'Тяжелый'], ['Тяжелая', 'Тяжелую'], ['Тяжелое', 'Тяжелое']],
                       [['Новый', 'Новый'], ['Новая', 'Новую'], ['Новое', 'Новое']]]
            n2 = [['меч', 0, 'меч', 'рубящее', False],
                        ['сабля', 1, 'саблю', 'рубящее', False],
                        ['катана', 1, 'катану', 'рубящее', False],
                        ['рапира', 1, 'рапиру', 'колющее', False],
                        ['пика', 1, 'пику', 'колющее', True],
                        ['копье', 2, 'копье', 'колющее', True],
                        ['топор', 0, 'топор', 'рубящее', False],
                        ['кинжал', 0, 'кинжал', 'колющее', False],
                        ['дубина', 1, 'дубину', 'ударное', False],
                        ['палица', 1, 'палицу', 'ударное', False],
                        ['булава', 1, 'булаву', 'ударное', False],
                        ['молот', 0, 'молот', 'ударное', True],
                        ['шпага', 1, 'шпагу', 'колющее', False]]
            a1 = dice(0, len(n1) - 1)
            a2 = dice(0, len(n2) - 1)
            self.name = n1[a1][n2[a2][1]][0] + ' ' + n2[a2][0]
            self.name1 = n1[a1][n2[a2][1]][1] + ' ' + n2[a2][2]
            self.damage = dice(3, 12)
            self.type = n2[a2][3]
            self.twohanded = n2[a2][4]
            self.gender = n2[a2][1]
        self.actions = actions.split(',')
        self.canUseInFight = True
        self.runes = []
        self.twohanded_dict = ['двуручный', 'двуручная', 'двуручное']
        self.empty = empty

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
            names.append(self.name + ' ' + s_elements_dictionary[self.element()])
            names.append(self.name1 + ' ' + s_elements_dictionary[self.element()])
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
        if len(self.runes) > 1 or self.empty:
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
            return ' ' + s_elements_dictionary[element]

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
        message = [f'{who.name} берет {self.name1}.']
        second_weapon = who.second_weapon()
        if who.weapon.empty:
            who.weapon = self
            message.append(f'{who.name} теперь использует {self.name1} в качестве оружия.')
            if who.weapon.twohanded and not who.shield.empty:
                shield = who.shield
                who.shield = self.game.noShield
                who.removed_shield = shield
                message.append('Из-за того, что герой взял двуручное оружие, ему пришлось убрать ' +
                               shield.realname()[1] +
                               ' за спину.')
        else:
            if not second_weapon.empty:
                message.append('В рюкзаке для нового оружия нет места, поэтому приходится бросить ' +
                               who.weapon.name +
                               '.')
                who.drop(who.weapon)
                who.weapon = self
            else:
                message.append('В рюкзаке находится место для второго оружия. Во время схватки можно "Сменить" оружие.')
                who.pockets.append(self)
        tprint(game, message)

    def show(self):
        damageString = str(self.damage)
        if self.permdamage() != 0:
            damageString += '+' + str(self.permdamage())
        if self.twohanded:
            name = self.twohanded_dict[self.gender] + ' ' + self.name
        else:
            name = self.name + self.enchantment()
        return f'{name} ({damageString})'

    def use(self, whoUsing, inaction=False):
        if whoUsing.weapon.empty:
            whoUsing.weapon = self
        else:
            whoUsing.pockets.append(whoUsing.weapon)
            whoUsing.weapon = self
            whoUsing.pockets.remove(self)
            message = [f'{whoUsing.name} теперь использует {self.name1} в качестве оружия.']
            if not whoUsing.shield.empty and self.twohanded:
                shield = whoUsing.shield
                whoUsing.removed_shield = shield
                whoUsing.shield = self.game.noShield
                message.append('Из-за того, что новое оружие двуручное, щит пришлось убрать за спину.')
            if not whoUsing.removed_shield.empty and not self.twohanded:
                shield = whoUsing.removed_shield
                whoUsing.shield = shield
                whoUsing.removed_shield = self.game.noShield
                message.append('Из-за того, что новое оружие одноручное, герой теперь держит во второй руке' +
                               shield.realname()[1] +
                               '.')
        tprint(self.game, message)

    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            rooms = castle.plan
            room = randomitem(rooms, False)
        if room.monster():
            monster = room.monster()
            if monster.carryweapon:
                monster.give(self)
                return True
        elif room.ambush != '':
            monster = room.ambush
            if monster.carryweapon:
                monster.give(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.loot.pile.append(self)
