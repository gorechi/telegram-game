from functions import showsides, randomitem, howmany, tprint, normal_count
from class_items import Money, Potion, Key, Rune, Book
from class_weapon import Weapon
from class_protection import Shield, Armor
from class_monsters import Monster
from random import randint as dice
from settings import *


class Hero:
    def __init__(self,
                 game,
                 name,
                 name1,
                 gender,
                 stren=10,
                 dext=2,
                 intel=0,
                 health=20,
                 actions=None,
                 weapon=None,
                 shield=None,
                 pockets=None,
                 armor=None):
        if actions is None:
            self.actions = ['бьет']
        else:
            self.actions = actions
        if pockets is None:
            self.pockets = []
        else:
            self.pockets = pockets
        self.game = game
        self.name = name
        self.name1 = name1
        self.gender = gender
        self.stren = int(stren)
        self.start_stren = self.stren
        self.dext = int(dext)
        self.start_dext = self.dext
        self.intel = int(intel)
        self.start_intel = self.intel
        self.health = int(health)
        if weapon is None:
            self.weapon = self.game.no_weapon
        else:
            self.weapon = weapon
        if armor is None:
            self.armor = self.game.no_armor
        else:
            self.armor = armor
        if shield is None:
            self.shield = self.game.no_shield
        else:
            self.shield = shield
        self.removed_shield = self.game.no_shield
        self.money = Money(self.game, 0)
        self.current_position = 0
        self.game_is_over = False
        self.start_health = self.health
        self.wins = 0
        self.rage = 0
        self.hide = False
        self.run = False
        self.level = 1
        self.exp = 0
        self.fear = 0
        self.drunk = 0
        self.levels = [0, 100, 200, 350, 500, 750, 1000, 1300, 1600, 2000, 2500, 3000]
        self.elements = {'огонь': 0, 'вода': 0, 'земля': 0, 'воздух': 0, 'магия': 0}
        self.element_levels = {'1': 2, '2': 4, '3': 7, '4': 10}
        self.weapon_mastery = {'рубящее': 0, "колющее": 0, "ударное": 0}
        self.directions_dict = {0: (0 - self.game.new_castle.rooms),
                               1: 1,
                               2: self.game.new_castle.rooms,
                               3: (0 - 1),
                               'наверх': (0 - self.game.new_castle.rooms),
                               'направо': 1,
                               'вправо': 1,
                               'налево': (0 - 1),
                               'лево': (0 - 1),
                               'влево': (0 - 1),
                               'вниз': self.game.new_castle.rooms,
                               'низ': self.game.new_castle.rooms,
                               'вверх': (0 - self.game.new_castle.rooms),
                               'верх': (0 - self.game.new_castle.rooms),
                               'право': 1}
        self.doors_dict = {'наверх': 0,
                          'направо': 1,
                          'вправо': 1,
                          'право': 1,
                          'налево': 3,
                          'влево': 3,
                          'лево': 3,
                          'вниз': 2,
                          'низ': 2,
                          'вверх': 0,
                          'верх': 0}
        self.command_dict = {'осмотреть': self.lookaround,
                            'идти': self.go,
                            'атаковать': self.fight,
                            'напасть': self.fight,
                            'взять': self.take,
                            'забрать': self.take,
                            'подобрать': self.take,
                            'обыскать': self.search,
                            'открыть': self.open,
                            'использовать': self.use,
                            'применить': self.use,
                            'читать': self.read,
                            'прочитать': self.read,
                            'убрать': self.remove,
                            'чинить': self.repair,
                            'починить': self.repair,
                            'отдохнуть': self.rest,
                            'отдыхать': self.rest,
                            'бросить': self.drop,
                            'выбросить': self.drop,
                            'сменить': self.change,
                            'поменять': self.change,
                            'улучшить': self.enchant}

    def __str__(self):
        return 'hero'

    def do(self, command):
        a = command.find(' ')
        full_command = []
        if a < 0:
            a = len(command)
        full_command.append(command[:a])
        full_command.append(command[a + 1:])
        if full_command[0] == '?':
            text = []
            text.append(f'{self.name} может:')
            for i in self.command_dict.keys():
                text.append(i)
            tprint(self.game, text)
            return True
        c = self.command_dict.get(full_command[0], False)
        if not c:
            tprint(self.game, f'Такого {self.name} не умеет!')
        elif len(full_command) == 1:
            c()
        else:
            c(full_command[1])

    def change(self, what=None):
        message = []
        if what == 'оружие':
            second_weapon = self.second_weapon()
            if not self.weapon.empty and not second_weapon.empty:
                message.append(f'{self.name} убирает {self.weapon.name1} в рюкзак и берет в руки {second_weapon.name1}.')
                if second_weapon.twohanded and not self.shield.empty:
                    self.removed_shield = self.shield
                    self.shield = self.game.no_shield
                    message.append(f'Из-за того, что {second_weapon.name1} - двуручное оружие, щит тоже приходится убрать.')
                elif not second_weapon.twohanded and not self.removed_shield.empty:
                    message.append(f'У {self.g(["героя", "героини"])} теперь одноручное оружие, поэтому {self.g(["он", "она"])} может достать щит из-за спины.')
                self.pockets.remove(second_weapon)
                self.pockets.append(self.weapon)
                self.weapon = second_weapon
            elif self.weapon.empty and not second_weapon.empty:
                message.append(f'{self.name} достает из рюкзака {second_weapon.name1} и берет в руку.')
                if second_weapon.twohanded and not self.shield.empty:
                    self.removed_shield = self.shield
                    self.shield = self.game.no_shield
                    message.append(f'Из-за того, что {second_weapon.name1} - двуручное оружие, щит приходится убрать за спину.')
                self.pockets.remove(second_weapon)
                self.weapon = second_weapon
            elif not self.weapon.empty and second_weapon.empty:
                message.append(f'{self.name} не может сменить оружие из-за того, что оно у него одно.')
            else:
                message.append(f'{self.name} не может сменить оружие. У {self.g(["него", "нее"])} и оружия-то нет.')
        else:
            message.append(f'{self.name} не знает, зачем нужно это менять.')
        tprint(self.game, message)
        return True
    
    def g(self, words_list):
        return words_list[self.gender]
    
    def drop(self, item=None):
        game = self.game
        room = game.new_castle.plan[self.current_position]
        if not item or item in ['все', 'всё']:
            tprint(game, f'{self.name} {self.g(["хотел", "хотела"])} бы бросить все и уйти в пекари, но в последний момент берет себя в руки и продолжает приключение.')
        elif item.isdigit():
            if int(item) - 1 < len(self.pockets):
                i = self.pockets[int(item) - 1]
                room.loot.append(i)
                self.pockets.remove(i)
                tprint(game, f'{self.name} бросает {i.name} на пол комнаты.')
                return True
            else:
                tprint(game, f'{self.name} не {self.g(["нашел", "нашла"])} такой вещи у себя в рюкзаке.')
                return False
        else:
            if not self.shield.empty and item.lower() in ['щит', self.shield.name.lower(), self.shield.name1.lower()]:
                room.loot.append(self.shield)
                tprint(game, f'{self.name} швыряет {self.shield.name} на пол комнаты.')
                self.shield = game.no_shield
                return True
            elif not self.removed_shield.empty and item.lower() in ['щит', self.removed_shield.name.lower(), self.removed_shield.name1.lower()]:
                room.loot.append(self.removed_shield)
                tprint(game, f'{self.name} достает {self.removed_shield.name} из-за спины и ставит его к стене.')
                self.removed_shield = game.no_shield
                return True
            elif not self.weapon.empty and item.lower() in ['оружие', self.weapon.name.lower(), self.weapon.name1.lower()]:
                room.loot.append(self.weapon)
                tprint(game, f'{self.name} бросает {self.shield.name} в угол комнаты.')
                self.weapon = game.no_weapon
                return True
            else:
                item_to_drop = None
                for i in self.pockets:
                    if item.lower() in [i.name.lower(), i.name1.lower()]:
                        item_to_drop = i
                if item_to_drop:
                    self.pockets.remove(item_to_drop)
                    tprint(game, f'{self.name} бросает {item_to_drop.name} на пол комнаты.')
                    return True
                else:
                    tprint(game, f'{self.name} роется в рюкзаке, но не находит ничего такого.')
                    return False
   
    def rest(self, what=None):
        game = self.game
        room = game.new_castle.plan[self.current_position]
        cant_rest, rest_place = room.can_rest()
        message = []
        shield = None
        if not rest_place or len(cant_rest) > 0:
            message.append('В этой комнате нельзя отдыхать.')
            message.append(randomitem(cant_rest))
            tprint(game, message)
            return False
        else:
            if room.get_ambush(self):
                return False
            if not self.shield.empty:
                shield = self.shield
            if not self.removed_shield.empty:
                shield = self.removed_shield
            if shield:
                need_money = shield.accumulated_damage * 10 // 1
                if need_money > 0 and self.money.how_much_money >= need_money:
                    shield.accumulated_damage = 0
                    self.money.how_much_money -= need_money
                    message.append(f'Пока отдыхает {self.name} успешно чинит {shield.name1}')
            dream_count = dice(1, s_nightmare_probability)
            steal_count = dice(1, s_steal_probability)
            if dream_count == 1:
                message.append(f'Провалившись в сон {self.name} видит ужасный кошмар. Так толком и не отдохнув {self.g(["герой", "героиня"])} просыпается с тревогой в душе.')
                self.fear = self.fear // 2
            else:
                message.append(f'{self.name} ложится спать и спит так сладко, что все страхи и тревоги уходят прочь.')
                self.fear = 0
            if steal_count == 1 and len(self.pockets) > 0:
                all_monsters = [monster for monster in game.all_monsters if (not monster.stink and monster.can_steal)]
                stealing_monster = randomitem(all_monsters)
                all_items = [item for item in self.pockets if (not isinstance(item, Key))]
                if len(all_items) > 0:
                    item = randomitem(all_items)
                    self.pockets.remove(item)
                    stealing_monster.give(item)
                    message.append(f'Проснувшись {self.name} лезет в свой рюкзак и обнаруживает, что кто-то украл {item.name1}.')
            tprint(game, message)
            return True
    
    def remove(self, what=None):
        message = []
        item = None
        if not self.shield.empty and what.lower() in ['щит', self.shield.name.lower(), self.shield.name1.lower()]:
            item = self.shield
        if not what:
            message.append(f'{self.name} оглядывается по сторонам, находит какой-то мусор и закидывает его в самый темный угол комнаты.')
        elif not item:
            message.append(f'{self.name} не понимает, как это можно убрать.')
        else:
            if isinstance(item, Shield):
                shield = self.shield
                self.removed_shield = shield
                self.shield = self.game.no_shield
                message.append(f'{self.name} убирает {shield.realname()[1]} за спину.')
        tprint(self.game, message)
        return True
        
    def repair(self, what=None):
        message = []
        if not self.shield.empty and what.lower() in ['щит', self.shield.name.lower(), self.shield.name1.lower()]:
                item = self.shield
        elif not self.removed_shield.empty and what.lower() in ['щит', self.removed_shield.name.lower(), self.removed_shield.name1.lower()]:
                item = self.removed_shield
        else:
            item = None
        if not what:
            message.append(f'{self.name} не может чинить что-нибудь. Нужно понимать, какую вещь ремонтировать.')
        elif not item:
            message.append(f'{self.name} не умеет чинить такие штуки.')
        else:
            need_money = item.accumulated_damage * 10 // 1
            if need_money == 0:
                message.append(f'{item.name1} не нужно ремонтировать.')
            elif self.money.hhow_much_money >= need_money:
                item.accumulated_damage = 0
                self.money.how_much_money -= need_money
                message.append(f'{self.name} успешно чинит {item.name1}')
            else:
                message.append(f'{self.name} и {self.g(["рад", "рада"])} бы починить {item.name1}, но {self.g(["ему", "ей"])} не хватает денег на запчасти.')
        tprint(self.game, message)
        return True

    def inpockets(self, item_type):
        """Функция возвращает список всех предметов определенного типа в рюкзаке героя

        Args:
            item_type (class): Класс предмета, который нужно найти (Например - Potion)

        Returns:
            list: Список всех найденных предметов
        """
        item_list = []
        for item in self.pockets:
            if isinstance(item, item_type):
                item_list.append(item)
        return item_list

    def action(self):
        """Функция возвращает случайное действие, которое герой может сделать оружием, которое держит в руках

        Returns:
            string: Строка действия. Например - "бьет".
        """
        return randomitem(self.weapon.actions)

    def second_weapon(self):
        """Функция ищет в рюкзаке героя оружие. 
        Если оружие найдено, функция возвращает его. Если оружие не найдено, возвращается объект "Пустое оружие".

        Returns:
            Weapon object: Объект класса Weapon
        """
        for i in self.pockets:
            if isinstance(i, Weapon):
                return i
        return self.game.no_weapon

    def run_away(self, target):
        """Функция "Убежать". Запускается когда герой сбегает из боя.

        Args:
            target (object Monster): Монстр, от которого убегает герой

        Returns:
            boolean: Возвращает False если по какой-то причине герой не смог сбежать
        """
        game = self.game
        room = game.new_castle.plan[self.current_position]
        if room.light:
            if target.frightening:
                tprint(game, f'{self.name} в ужасе сбегает с поля боя.')
                self.fear += 1
            else:
                tprint(game, f'{self.name} сбегает с поля боя.')
        else:
            if target.frightening:
                tprint(game, f'{self.name} в кромешной тьме закрыв глаза от ужаса пытается убежать хоть куда-нибудь.')
                self.fear += 1
            else:
                tprint(game, f'{self.name} в кромешной тьме пытается убежать хоть куда-нибудь.')
        a = dice(1, 2)
        if a == 1 and not self.weapon.empty:
            tprint(game, f'Убегая {self.name} роняет из рук {self.weapon.name1}')
            if target.weapon.empty and target.carryweapon:
                target.weapon = self.weapon
            else:
                room.loot.pile.append(self.weapon)
            self.weapon = self.game.no_weapon
        elif a == 2 and self.shield.empty:
            tprint(game, f'Убегая {self.name} теряет {self.shield.name1}')
            if target.shield == '' and target.carryshield:
                target.shield = self.shield
            else:
                room.loot.pile.append(self.shield)
            self.shield = self.game.no_shield
        a = dice(0, len(self.pockets))
        if a > 0:
            first_line = f'{self.name} бежит настолько быстро, что не замечает, как теряет:'
            text = [first_line]
            for i in range(a):
                b = dice(0, len(self.pockets) - 1)
                text.append(self.pockets[b].name1)
                room.loot.pile.append(self.pockets[b])
                self.pockets.pop(b)
            tprint(game, text)
        available_directions = []
        for i in range(4):
            if room.doors[i] == 1:
                available_directions.append(i)
        if room.light:
            direction = available_directions[dice(0, len(available_directions) - 1)]
        else:
            direction = dice(0, 3)
            if direction not in available_directions:
                return False
        self.current_position += self.directions_dict[direction]
        room = game.new_castle.plan[self.current_position]
        room.visited = '+'
        game.state = 0
        self.lookaround()
        if isinstance(room.center, Monster) and room.center.agressive and room.light:
                self.fight(room.center, True)
                return False
        return f'{self.name} еле стоит на ногах.'

    def attack(self, target, action):
        game = self.game
        room = game.new_castle.plan[self.current_position]
        if room.light:
            target_name = target.name
            target_name1 = target.name1
            if self.rage > 1:
                rage = dice(2, self.rage)
            else:
                rage = 1
            mele_attack = dice(1, self.stren) * rage
        else:
            target_name = 'Неизвестная тварь из темноты'
            target_name1 = 'черт знает кого'
            rage = 1
            mele_attack = dice(1, self.stren) // dice(1, 3)
        self.run = False
        can_use = []
        for i in self.pockets:
            if i.can_use_in_fight:
                can_use.append(i)
        if action == '' or action == 'у' or action == 'ударить':
            tprint(game, showsides(self, target, game.new_castle))
            self.rage = 0
            self.hide = False
            if not self.weapon.empty:
                weapon_attack = self.weapon.attack(target)
                critical_probability = self.weapon_mastery[self.weapon.type] * 5
                damage_text = ' урона. '
                if dice(1, 100) <= critical_probability:
                    weapon_attack = weapon_attack * 2
                    damage_text = ' критического урона. '
                string1 = f'{self.name} {self.action()} {target_name1} используя {self.weapon.name} и наносит' \
                          f' {str(mele_attack)}+{howmany(weapon_attack, "единицу,единицы,единиц")} {damage_text}'
            else:
                weapon_attack = 0
                string1 = f'{self.name} бьет {target_name1} не используя оружие и ' \
                          f'наносит {howmany(mele_attack, "единицу,единицы,единиц")} урона. '
            target_defence = target.defence(self)
            total_attack = weapon_attack + mele_attack
            if (total_attack - target_defence) > 0:
                total_damage = weapon_attack + mele_attack - target_defence
            else:
                total_damage = 0
            if total_damage == 0:
                string2 = f'{self.name} не {self.g(["смог", "смогла"])} пробить защиту {target_name1}.'
            elif target_defence == 0:
                string2 = f'{target_name} не имеет защиты и теряет {howmany(total_damage, "жизнь,жизни,жизней")}.'
            else:
                string2 = f'{target_name} защищается и теряет {howmany(total_damage, "жизнь,жизни,жизней")}.'
            if target.shield != '':
                shield = target.shield
                rand = dice(1, 100)
                dam = total_attack * target.shield.accumulated_damage
                if rand < dam:
                    string1 += f' {self.name} наносит настолько сокрушительный удар, что ломает щит соперника.'
                    game.all_shields.remove(shield)
                    target.shield = ''
            target.health -= total_damage
            return string1 + string2
        elif action in ['з', 'защититься', 'защита']:
            result = self.use_shield(target)
            if result:
                return result
        elif action in ['б', 'бежать', 'убежать']:
            self.rage = 0
            self.hide = False
            result = self.run_away(target)
            if not result:
                return f'{self.name} с разбега врезается в стену и отлетает в сторону. Схватка продолжается.'
            else:
                return result
        elif action in ['и', 'использовать'] and len(can_use) > 0:
            tprint(game, f'Во время боя {self.name} может использовать:')
            for i in self.pockets:
                if i.can_use_in_fight:
                    tprint(game, i.name)
            while True:
                a = input('Что нужно использовать?')
                if a == 'ничего' or a == '':
                    break
                else:
                    item_used = False
                    for i in can_use:
                        if i.name == a or i.name1 == a:
                            if i.use(self, inaction=True) and isinstance(i, Potion):
                                self.pockets.remove(i)
                            item_used = True
                            break
                    if item_used:
                        break
                    tprint(game, 'Что-то не выходит')
        elif action in ['с', 'сменить оружие', 'сменить']:
            weapon = self.weapon
            spare_weapon = False
            for item in self.pockets:
                if isinstance(item, Weapon):
                    spare_weapon = item
            self.weapon = spare_weapon
            self.pockets.remove(spare_weapon)
            self.pockets.append(weapon)
            message = [f'{self.name} меняет {weapon.name1} на {spare_weapon.name1}.']
            tprint(game, message)
        return True

    def use_shield(self, target):
        game = self.game
        if self.shield == '':
            return False
        else:
            tprint(game, showsides(self, target, game.new_castle))
            self.hide = True
            self.rage += 1
            return f'{self.name} уходит в глухую защиту, терпит удары и накапливает ярость.'

    def show(self):
        """Функция генерирует и выводит на экран описание персонажа
        """
        message = []
        if self.money.how_much_money > 1:
            money_text = f'В кошельке звенят {howmany(self.money.how_much_money, "монета,монеты,монет")}.'
        elif self.money.how_much_money == 1:
            money_text = f'Одна-единственная монета оттягивает карман героя.'
        else:
            money_text = f'{self.g(["Герой беден", "Героиня бедна"])}, как церковная мышь.'
        message.append(f'{self.name} - это {self.g(["смелый герой", "смелая героиня"])} {str(self.level)} уровня. {self.g(["Его", "Ее"])} сила - {str(self.stren)} и сейчас'
                       f' у {self.g(["него", "нее"])} {howmany(self.health, "единица,единицы,единиц")} здоровья, что составляет '
                       f'{str(self.health * 100 // self.start_health)} % от максимально возможного. {money_text}')
        if not self.weapon.empty:
            weapon_text = f'{self.weapon.real_name()[0]} в руке {self.g(["героя", "героини"])} добавляет к {self.g(["его", "ее"])} силе ' \
                          f'{str(self.weapon.damage)}+{str(self.weapon.perm_damage())}.'
        else:
            weapon_text = f'{self.name} предпочитает сражаться голыми руками.'
        message.append(weapon_text)
        if not self.shield.empty or not self.armor.empty:
            protection_text = f'{self.g(["Героя", "Героиню"])} '
            if not self.shield.empty and not self.armor.empty:
                protect = 'защищают '
                and_text = ' и '
            else:
                protect = 'защищает '
                and_text = ''
            if not self.shield.empty:
                shield_text = f'{self.shield.real_name()[0]} ' \
                              f'({str(self.shield.protection)}+{str(self.shield.perm_protection())})'
            else:
                shield_text = ''
            if not self.armor.empty:
                armor_text = f'{self.armor.real_name()[0]} ' \
                             f'({str(self.armor.protection)}+{str(self.armor.perm_protection())})'
            else:
                armor_text = ''
            protection_text += protect + shield_text + and_text + armor_text
        else:
            protection_text = f'У {self.g(["героя", "героини"])} нет ни щита, ни доспехов.'
        message.append(protection_text)
        mastery_text = None
        for mastery in self.weapon_mastery:
            if self.weapon_mastery[mastery] > 0:
                if not mastery_text:
                    mastery_text = f'{mastery} ({self.weapon_mastery[mastery]})'
                else:
                    mastery_text += f' {mastery} ({self.weapon_mastery[mastery]})'
        if mastery_text:
            text = f'{self.g(["Герой", "Героиня"])} обладает знаниями про {normal_count(mastery_text, "(")} оружие.'
            message.append(text)
        tprint(self.game, message)

    def defence(self, attacker):
        """Функция рассчитывает сумму защиты героя против атаки монстра

        Args:
            attacker (object, class Monster, обязательный): Объект атакующего монстра

        Returns:
            integer: Значение защиты с учетом доспехов и щита.
        """
        result = 0
        if not self.shield.empty:
            result += self.shield.protect(attacker)
            if self.hide:
                dice_result = dice(50, 75) / 100
                self.shield.accumulated_damage += dice_result
            else:
                dice_result = dice(10, 25) / 100
                self.shield.accumulated_damage += dice_result
        if not self.armor.empty:
            result += self.armor.protect(attacker)
        return result

    def lose(self, winner=None):
        """Функция сбрасывает состояние героя при его проигрыше в бою

        Args:
            winner (object, class Monster, optional): Объект атакующего монстра. Defaults to None.
        """
        self.health = self.start_health
        self.stren = self.start_stren
        self.dext = self.start_dext
        self.intel = self.start_intel
        self.current_position = 0

    def win(self, loser):
        self.health = self.start_health
        self.stren = self.start_stren
        self.dext = self.start_dext
        self.intel = self.start_intel
        self.wins += 1
        tprint(self.game, f'{self.name} получает {howmany(loser.exp, "единицу,единицы,единиц")} опыта!')
        self.exp += loser.exp
        if self.exp > self.levels[self.level]:
            self.levelup()

    def levelup(self):
        """Функция вызывается если герой получает новый уровень.
        Функция переводит игру в режим прокачки и выводит на экран инструкцию по прокачке.
        """
        self.game.state = 3
        level_up_message = []
        level_up_message.append(f'{self.name} получает новый уровень!')
        level_up_message.append('Что необходимо прокачать: здоровье, силу, ловкость или интеллект?')
        tprint(self.game, level_up_message, 'levelup')
        self.level += 1
        return True

    def game_over(self, goal_type, goal=None):
        """Функция производит проверку на выполнение условия окончания игры.

        Args:
            goal_type (string): Тип завершения игры. Сейчас поддерживаются следующие типы:
                                - 'killall': игра завершается если в замке убиты все монстры\n
            goal (string, optional): Вспомогательный параметр для типа завершения игры. Defaults to None.

        Returns:
            boolean:    True - если условие завершения игры выполнено
                        False - если условие завершение игры не выполнено
        """
        if goal_type == 'killall':
            if self.game.new_castle.monsters() == 0:
                tprint(self.game, f'{self.name} {self.g(["убил", "убила"])} всех монстров в замке и {self.g(["выиграл", "выиграла"])} в этой игре!')
                return True
            else:
                return False
        return False

    def lookaround(self, what=None):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        furniture_list = room.furniture
        if not what:
            room.show(game.player)
            room.map()
            return True
        elif what == 'себя':
            self.show()
            return True
        elif what == 'рюкзак':
            text = []
            if len(self.pockets) == 0 and self.money.how_much_money == 0:
                text.append(f'{self.name} осматривает свой рюкзак и обнаруживает, что тот абсолютно пуст.')
            else:
                text.append(f'{self.name} осматривает свой рюкзак и обнаруживает в нем:')
                for i in range(len(self.pockets)):
                    description = f'{str(i + 1)}: {self.pockets[i].show()}'
                    if isinstance(self.pockets[i], Weapon):
                        weapon = self.pockets[i]
                        if self.weapon_mastery[weapon.type] > 0:
                            description += f', мастерство - {self.weapon_mastery[weapon.type]}'
                    text.append(description)
                text.append(self.money.show())
            if not self.removed_shield.empty:
                text.append(f'За спиной у {self.g(["героя", "героини"])} висит {self.removed_shield.realname()[0]}')
            tprint(game, text)
            return True
        elif what in self.directions_dict.keys():
            if room.doors[self.doors_dict[what]] == 0:
                tprint(game, f'{self.name} осматривает стену и не находит ничего заслуживающего внимания.')
                return True
            else:
                if self.fear >=s_fear_limit:
                    message = f'{self.name} не может заставить себя заглянуть в замочную скважину. Слишком страшно.'
                else:
                    what_position = room.position + self.directions_dict[what]
                    message = new_castle.plan[what_position].show_through_key_hole(self)
                tprint(game, message)
                return True
        if not room.center.empty and what in [room.center.name, room.center.name1, room.center.name[0]] and room.monster():
            tprint(game, showsides(self, room.center, new_castle))
            return True
        if not self.weapon.empty and what in [self.weapon.name, self.weapon.name1, 'оружие']:
            tprint(game, self.weapon.show())
            return True
        if not self.shield.empty and what in [self.shield.name, self.shield.name1, 'защиту']:
            tprint(game, self.shield.show())
            return True
        if len(furniture_list) > 0:
            text = []
            for i in furniture_list:
                if i.name1 == what:
                    text.extend(i.show())
            if len(text) > 0:
                tprint(game, text)
        if len(self.pockets) > 0:
            text = []
            for i in self.pockets:
                if what in [i.name, i.name1]:
                    text.append(i.show())
            tprint(game, text)
        return True

    def go(self, direction):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        if direction not in self.directions_dict.keys():
            tprint(game, f'{self.name} не знает такого направления!')
            return False
        elif room.doors[self.doors_dict[direction]] == 0:
            if room.light:
                message = [f'Там нет двери. {self.name} не может туда пройти!']
            else:
                message = [f'В темноте {self.name} врезается во что-то носом.']
            tprint(game, message)
            return False
        elif room.doors[self.doors_dict[direction]] == 2:
            if room.light:
                message = [f'Эта дверь заперта. {self.name} не может туда пройти, нужен ключ!']
            else:
                message = [f'В темноте {self.name} врезается во что-то носом.']
            tprint(game, message)
            return False
        else:
            self.current_position += self.directions_dict[direction]
            room = new_castle.plan[self.current_position]
            room.visited = '+'
            room.show(self)
            room.map()
            if room.monster():
                if room.center.agressive and room.light:
                    self.fight(room.center.name, True)
            return True

    def fight(self, enemy, agressive=False):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        who_is_fighting = room.monster()
        if not who_is_fighting:
            tprint(game, 'Не нужно кипятиться. Тут некого атаковать')
            return False
        if not enemy in [who_is_fighting.name, who_is_fighting.name1, who_is_fighting.name[0]] and enemy != '':
            tprint(game, f'{self.name} не может атаковать. В комнате нет такого существа.')
            return False
        game.state = 1
        if agressive:
            who_first = 2
        else:
            who_first = dice(1, 2)
        if who_first == 1:
            tprint(game, f'{game.player.name} начинает схватку!', 'fight')
            self.attack(who_is_fighting, 'атаковать')
        else:
            if room.light:
                message = [f'{who_is_fighting.name} начинает схватку!']
            else:
                message = ['Что-то жуткое и непонятное нападает первым из темноты.']
            tprint(game, message, 'fight')
            tprint(game, who_is_fighting.attack(self))
            return True

    def search(self, item=False):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        message = []
        enemy_in_room = False
        if isinstance(room.center, Monster):
            enemy_in_room = room.center
        if not room.light:
            message.append('В комнате настолько темно, что невозможно что-то отыскать.')
            tprint(game, message)
            return True
        if enemy_in_room:
            message.append(f'{enemy_in_room.name} мешает толком осмотреть комнату.')
            tprint(game, message)
            return True
        if not item:
            if room.get_ambush(self):
                return False
            for furniture in room.furniture:
                message.append(furniture.where + ' ' + furniture.state + ' ' + furniture.name)
            if not room.loot.empty and len(room.loot.pile) > 0:
                message.append('В комнате есть:')
                for i in room.loot.pile:
                    message.append(i.name)
            else:
                message.append('В комнате нет ничего интересного.')
            tprint(game, message)
            return True
        else:
            if self.fear >= s_fear_limit:
                message = f'{self.name} не хочет заглядывать в неизвестные места. Страх сковал {self.g(["его", "ее"])} по рукам и ногам.'
                tprint(game, message)
                return True
            if room.secret_word.lower() == item.lower():
                if len(room.secret_loot.pile) == 0:
                    message.append(f'{self.name} осматривает {item} и ничего не находит.')
                    tprint(game, message)
                    return True
                else:
                    message.append(f'{self.name} осматривает {item} и находит:')
                    for i in room.secret_loot.pile:
                        message.append(i.name)
                        room.loot.pile.append(i)
                        message.append('Все, что было спрятано, теперь лежит на виду.')
                    tprint(game, message)
                    return True
            what_to_search = False
            for i in room.furniture:
                if item.lower() in [i.name.lower(), i.name1.lower()]:
                    what_to_search = i
            if not what_to_search:
                message.append('В комнате нет такой вещи.')
            elif what_to_search.locked:
                message.append(f'Нельзя обыскать {what_to_search.name1}. Там заперто.')
                tprint(game, message)
                return False
            elif what_to_search.get_ambush(self):
                return False
            elif len(what_to_search.loot.pile) > 0:
                message.append(f'{self.name} осматривает {what_to_search.name1} и находит:')
                for i in what_to_search.loot.pile:
                    message.append(i.name)
                    room.loot.pile.append(i)
                if len(what_to_search.loot.pile) > 0:
                    message.append('Все, что было спрятано, теперь лежит на виду.')
            elif len(what_to_search.loot.pile) == 0:
                message.append(what_to_search.name + ' ' + what_to_search.empty_text)
            tprint(game, message)
            return True

    def can_take(self, obj):
        classes = [Weapon, Shield, Armor]
        for i in classes:
            if isinstance(obj, i):
                return False
        return True

    def take(self, item='все'):
        game = self.game
        castle = self.game.new_castle
        current_loot = castle.plan[self.current_position].loot
        if current_loot.empty:
            tprint(game, 'Здесь нечего брать.')
            return False
        elif item in ['все', 'всё', '']:
            items_to_remove = []
            for item in current_loot.pile:
                if self.can_take(item):
                    item.take(self)
                    items_to_remove.append(item)
            for item in items_to_remove:
                current_loot.pile.remove(item)
            return True
        else:
            for i in current_loot.pile:
                if item in [i.name.lower(), i.name1.lower()]:
                    i.take(self)
                    current_loot.pile.remove(i)
                    return True
        tprint(game, 'Такой вещи здесь нет.')
        return False

    def open(self, item=''):
        game = self.game
        new_castle = self.game.new_castle
        room = new_castle.plan[self.current_position]
        key = False
        if self.fear >= s_fear_limit:
            message = [f'{self.name} Не может ничего сделать из-за того, что руки дрожат от страха.']
            tprint(game, message)
            return False
        for i in self.pockets:
            if isinstance(i, Key):
                key = i
        if not key:
            message = ['Чтобы что-то открыть нужен хотя бы один ключ.']
            tprint(game, message)
            return False
        what_is_in_room = []
        if len(room.furniture) > 0:
            for furniture in room.furniture:
                if furniture.locked:
                    what_is_in_room.append(furniture)
        if item == '' or (not self.doors_dict.get(item, False) and self.doors_dict.get(item, True) != 0):
            if len(what_is_in_room) == 0:
                if room.light:
                    message = ['В комнате нет вещей, которые можно открыть.']
                else:
                    message = [f'{self.name} шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return False
            elif item == '' and len(what_is_in_room) > 1:
                if room.light:
                    message = [f'В комнате слишком много запертых '
                               f'вещей. {self.name} не понимает, что {self.g(["ему", "ей"])} нужно открыть.']
                else:
                    message = [f'{self.name} шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return False
            elif item != '':
                if room.light:
                    for furniture in what_is_in_room:
                        if item.lower() in [furniture.name.lower(), furniture.name1.lower()]:
                            self.pockets.remove(key)
                            furniture.locked = False
                            message = [f'{self.name} отпирает {furniture.name1} ключом.']
                            tprint(game, message)
                            return True
                    message = [f'{self.name} не находит в комнате такой вещи. Отпирать нечего.']
                    tprint(game, message)
                else:
                    message = [f'{self.name} шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return True
            else:
                if room.light:
                    self.pockets.remove(key)
                    what_is_in_room[0].locked = False
                    message = [f'{self.name} отпирает {what_is_in_room[0].name1} ключом.']
                else:
                    message = [f'{self.name} шарит в темноте руками, но не нащупывает ничего интересного']
                tprint(game, message)
                return True
        else:
            if not room.light:
                message = [f'{self.name} ничего не видит и не может нащупать замочную скважину.']
                tprint(game, message)
                return False
            if not self.doors_dict.get(item, False) and self.doors_dict.get(item, True) != 0:
                tprint(game, f'{self.name} не может это открыть.')
                return False
            elif new_castle.plan[self.current_position].doors[self.doors_dict[item]] != 2:
                tprint(game, 'В той стороне нечего открывать.')
                return False
            else:
                self.pockets.remove(key)
                room.doors[self.doors_dict[item]] = 1
                j = self.doors_dict[item] + 2 if (self.doors_dict[item] + 2) < 4 else self.doors_dict[item] - 2
                new_castle.plan[self.current_position + self.directions_dict[item]].doors[j] = 1
                tprint(game, f'{self.name} открывает дверь.')

    def use(self, item=None, infight=False):
        game = self.game
        if not item:
            tprint(game, f'{self.name} не понимает, что {self.g(["ему", "ей"])} надо использовать.')
        elif item.isdigit():
            if int(item) - 1 < len(self.pockets):
                i = self.pockets[int(item) - 1]
                if isinstance(i, Potion) and i.use(self, False):
                    self.pockets.remove(i)
                elif not isinstance(i, Potion):
                    i.use(self, False)
                return True
            else:
                tprint(game, f'{self.name} не {self.g(["нашел", "нашла"])} такой вещи у себя в рюкзаке.')
                return False
        else:
            if not self.removed_shield.empty and item.lower() in [self.removed_shield.name.lower(), self.removed_shield.name1.lower(), 'щит']:
                if not self.weapon.empty and self.weapon.twohanded:
                    message = [f'{self.name} воюет двуручным оружием, поэтому не может взять щит.']
                    tprint(game, message)
                    return True
                shield = self.removed_shield
                self.shield = shield
                self.removed_shield = self.game.no_shield
                message = [f'{self.name} достает {shield.realname()[0]} из-за спины и берет его в руку.']
                tprint(game, message)
                return True
            for i in self.pockets:
                if item.lower() in [i.name.lower(), i.name1.lower()]:
                    if isinstance(i, Potion) and i.use(self, in_action=False):
                        self.pockets.remove(i)
                    else:
                        i.use(self, in_action=False)
                    return True
            tprint(game, f'{self.name} не {self.g(["нашел", "нашла"])} такой вещи у себя в карманах.')

    def enchant(self, item=''):
        """Функция улучшения вещей рунами.

        Args:
            item (str, optional): Наименование предмета, который нужно улучшить.\n
            Поддерживаются следующие значения: \n
            - 'оружие'\n
            - 'щит'\n
            - 'доспех' или 'доспехи'
        """
        game = self.game
        rune_list = self.inpockets(Rune)
        game.selected_item = game.empty_thing
        if len(rune_list) == 0:
            tprint(game, f'{self.name} не может ничего улучшать. В рюкзаке не нашлось ни одной руны.')
            return False
        if item == '':
            tprint(game, f'{self.name} не понимает, что {self.g(["ему", "ей"])} надо улучшить.')
            return False
        if self.fear >= s_fear_limit:
            tprint(game, f'{self.name} дрожащими от страха руками пытается достать из рюкзака руну, но ничего не получается.')
            return False
        elif item == 'оружие' and not self.weapon.empty:
            game.selected_item = self.weapon
        elif item == 'щит':
            if not self.shield.empty:
                game.selected_item = self.shield
            elif not self.removed_shield.empty:
                game.selected_item = self.removed_shield
        elif item in ['дооспех', 'доспехи'] and not self.armor.empty:
            game.selected_item = self.armor
        elif item.isdigit() and int(item) - 1 <= len(self.pockets):
            game.selected_item = self.pockets[int(item) - 1]
        else:
            for i in self.pockets:
                if item.lower() in [i.name.lower(), i.name1.lower()]:
                    game.selected_item = i
                else:
                    tprint(game, f'{self.name} не {self.g(["нашел", "нашла"])} такой вещи у себя в рюкзаке.')
                    return False
        if isinstance(game.selected_item, Weapon) or isinstance(game.selected_item, Shield) or isinstance(game.selected_item, Armor):
            text = []
            text.append(f'{self.name} может использовать следующие руны:')
            for rune in rune_list:
                text.append(f'{str(rune_list.index(rune) + 1)}: {str(rune)}')
            text.append('Выберите номер руны или скажите "отмена" для прекращения улучшения')
            # Здесь нужна доработка т.к. управление переходит на работу с рунами
            game.state = 2
            tprint(game, text, 'enchant')
        else:
            tprint(game, f'{self.name} не может улучшить эту вещь.')
            return False

    def read(self, what):
        if self.fear >= s_fear_limit:
            message = f'{self.name} не может читать - от страха буквы плывут перед глазами.'
            tprint(self.game, message)
            return False
        books = []
        message = []
        for i in self.pockets:
            if isinstance(i, Book):
                books.append(i)
        if len(books) > 0:
            book = None
            if not what or what == 'книгу':
                book = randomitem(books, False)
                message.append(f'{self.name} роется в рюкзаке и находит первую попавшуюся книгу.')
            else:
                for i in books:
                    if what.lower() in [i.name.lower(), i.name1.lower()]:
                        book = i
                        message.append(f'{self.name} читает {book.name1}.')
                if not book:
                    message.append('В рюкзаке нет такой книги.')
            if book:
                message.append(book.text)
                message += book.print_mastery(self)
                message.append(f'{self.g(["Он", "Она"])} решает больше не носить книгу с собой и оставляет ее в незаметном месте.')
                self.weapon_mastery[book.weapon_type] += 1
                self.pockets.remove(book)
        else:
            message.append('В рюкзаке нет ни одной книги. Грустно, когда нечего почитать.')
        tprint(self.game, message)
        return True
