from functions import *
from constants import *

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
