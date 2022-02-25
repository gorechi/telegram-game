from math import ceil
from random import randint as dice

from functions import randomitem, tprint
from settings import *


class Weapon:
    def __init__(self, game, name='', name1='оружие', damage=1, actions='бьет,ударяет', empty=False, weapon_type=None):
        self.game = game
        if name != 0:
            self.name = name
            self.damage = int(damage)
            self.name1 = name1
            self.twohanded = False
            self.type = ''
            self.hit_chance = 0
        else:
            n1 = s_weapon_first_words_dictionary
            n2 = []
            for i in s_weapon_types_dictionary:
                if not weapon_type or i[3] == weapon_type:
                    n2.append(i)
            a1 = dice(0, len(n1) - 1)
            a2 = dice(0, len(n2) - 1)
            self.name = n1[a1][n2[a2][1]][0] + ' ' + n2[a2][0]
            self.name1 = n1[a1][n2[a2][1]][1] + ' ' + n2[a2][2]
            self.damage = dice(3, 12)
            self.type = n2[a2][3]
            self.twohanded = n2[a2][4]
            self.gender = n2[a2][1]
            self.hit_chance = n2[a2][5]
        self.actions = actions.split(',')
        self.can_use_in_fight = True
        self.runes = []
        self.twohanded_dict = s_weapon_twohanded_dictionary
        self.empty = empty
        self.mastery_level = 1
        self.mastery_counter = 0

    def on_create(self):
        return True

    def __str__(self):
        damage_string = str(self.damage)
        if self.perm_damage() != 0:
            damage_string += '+' + str(self.perm_damage())
        return f'{self.name}{self.enchantment()} ({damage_string})'

    def mastery(self):
        if self.empty:
            return False
        self.mastery_counter += dice(1, 10)/100
        if self.mastery_counter > self.mastery_level:
            self.mastery_counter = 0
            self.mastery_level += 1
            return True
        return False
    
    def real_name(self):
        names = []
        if self.element() != 0:
            name1 = f'{self.name} {s_elements_dictionary[self.element()]}'.capitalize()
            name2 = f'{self.name1} {s_elements_dictionary[self.element()]}'.capitalize()
        else:
            name1 = self.name.capitalize()
            name2 = self.name1.capitalize()
        names.append(name1)
        names.append(name2)
        return names

    def element(self):
        element_sum = 0
        for rune in self.runes:
            element_sum += rune.element
        return element_sum

    def is_poisoned(self):
        for i in self.runes:
            if i.poison:
                return True
        return False
    
    def enchant(self, rune):
        if len(self.runes) > 1 or self.empty:
            return False
        else:
            self.runes.append(rune)
            return True

    def enchantment(self):
        """Функция генерирует название элемента оружия. 
        Элемент складывается из сочетания рун, прикрепленных к оружию.

        Returns:
            string: Строка элемента для добавления к названию оружия.\n
            Пример: " огня" для формирования названия "Большой топор огня".
        """
        if len(self.runes) not in [1, 2]:
            return ''
        else:
            element = 0
            for i in self.runes:
                element += int(i.element)
            return ' ' + s_elements_dictionary[element]

    def perm_damage(self):
        damage = 0
        if len(self.runes) in [1, 2]:
            for rune in self.runes:
                damage += rune.damage
        return damage

    def attack(self, who=None):
        """Функция рассчитывает урон, который наносит оружие конкретному монстру

        Args:
            who (object Monster, optional): Монстр, которого атакуют оружием. Defaults to None.

        Returns:
            integer: Значение нанесенного урона
        """
        damage = dice(1, int(self.damage))
        big_damage = damage + self.perm_damage()
        if who:
            damage_multiplier = who.get_weakness([self])[0]
        else:
            damage_multiplier = 1
        full_damage = ceil(big_damage * damage_multiplier)
        return full_damage

    def take(self, who):
        game = self.game
        message = [f'{who.name} берет {self.name1}.']
        second_weapon = who.second_weapon()
        if who.weapon.empty:
            who.weapon = self
            message.append(f'{who.name} теперь использует {self.name1} в качестве оружия.')
            if who.weapon.twohanded and not who.shield.empty:
                shield = who.shield
                who.shield = self.game.no_shield
                who.removed_shield = shield
                message.append(f'Из-за того, что {who.g(["герой взял", "героиня взяла"])} двуручное оружие, '
                               f'{who.g(["ему", "ей"])} пришлось убрать {shield.real_name()[1]} за спину.')
        else:
            if not second_weapon.empty:
                message.append(f'В рюкзаке для нового оружия нет места, поэтому приходится бросить {who.weapon.name}.')
                who.drop(who.weapon.name)
                who.weapon = self
            else:
                message.append('В рюкзаке находится место для второго оружия. Во время схватки можно "Сменить" оружие.')
                who.pockets.append(self)
        tprint(game, message)

    def show(self):
        damage_string = str(self.damage)
        if self.perm_damage() != 0:
            damage_string += '+' + str(self.perm_damage())
        if self.twohanded:
            name = self.twohanded_dict[self.gender] + ' ' + self.name + self.enchantment()
        else:
            name = self.name + self.enchantment()
        return f'{name} ({damage_string}), {self.type}'.capitalize()

    def use(self, who, in_action=False):
        game = self.game
        if who.weapon.empty:
            who.weapon = self
        else:
            who.pockets.append(who.weapon)
            who.weapon = self
            who.pockets.remove(self)
            message = [f'{who.name} теперь использует {self.name1} в качестве оружия.']
            if not who.shield.empty and self.twohanded:
                shield = who.shield
                who.removed_shield = shield
                who.shield = game.no_shield
                message.append('Из-за того, что новое оружие двуручное, щит пришлось убрать за спину.')
            if not who.removed_shield.empty and not self.twohanded:
                shield = who.removed_shield
                who.shield = shield
                who.removed_shield = game.no_shield
                message.append(f'Из-за того, что новое оружие одноручное, '
                               f'{who.g(["герой", "героиня"])} теперь держит во второй руке {shield.real_name()[1]}.')
        tprint(game, message)

    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan, False)
        monster = room.monster()
        if not monster:
            monster = room.monster_in_ambush()
        if monster:
            if monster.carry_weapon:
                monster.give(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture, False)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.loot.add(self)
