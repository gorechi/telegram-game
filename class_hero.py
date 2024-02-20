from random import randint as dice

from class_items import Book, Key, Money, Rune
from class_monsters import Monster, Vampire
from class_protection import Armor, Shield
from class_room import Furniture, Room
from class_weapon import Weapon
from class_backpack import Backpack
from functions import howmany, normal_count, randomitem, showsides, tprint
from settings import *


class Hero:
    """Класс героя игры"""
    
    def __init__(self,
                 game,
                 name:str = None,
                 name1:str = None,
                 gender:int = None,
                 stren:int = 10,
                 dext:int = 2,
                 intel:int = 0,
                 health:int = 20,
                 actions:list = None,
                 weapon=None,
                 shield=None,
                 backpack=None,
                 armor=None):
        if not actions:
            self.actions = ['бьет']
        else:
            self.actions = actions
        self.game = game
        self.name = name
        self.name1 = name1
        self.gender = gender
        self.poisoned = False
        self.stren = stren
        self.start_stren = self.stren
        self.dext = dext
        self.start_dext = self.dext
        self.intel = intel
        self.start_intel = self.intel
        self.health = health
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
        if backpack is None:
            self.backpack = Backpack(self.game)
        else:
            self.backpack = backpack
        self.money = Money(self.game, 0)
        self.current_position = None
        self.game_is_over = False
        self.start_health = self.health
        self.weakness = {}
        self.restless = 0
        self.wins = 0
        self.rage = 0
        self.hide = False
        self.run = False
        self.level = 1
        self.exp = 0
        self.fear = 0
        self.drunk = 0
        self.floor = self.game.castle_floors[0]
        self.save_room = self.floor.plan[0]
        self.levels = [0, 100, 200, 350, 500, 750, 1000, 1300, 1600, 2000, 2500, 3000]
        self.elements = {'огонь': 0, 'вода': 0, 'земля': 0, 'воздух': 0, 'магия': 0}
        self.element_levels = {'1': 2, '2': 4, '3': 7, '4': 10}
        self.weapon_mastery = {'рубящее': {
                                        'counter': 0,
                                        'level': 0
                                        }, 
                               "колющее": {
                                        'counter': 0,
                                        'level': 0
                                        }, 
                               "ударное": {
                                        'counter': 0,
                                        'level': 0
                                        }, 
                               "": {
                                        'counter': 0,
                                        'level': 0
                                        }
                               }
        self.command_dict = {'осмотреть': self.look,
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
                            'test': self.test,
                            'улучшить': self.enchant}

    
    def on_create(self):
        return None
    
    
    def __str__(self):
        return f'<Hero: name = {self.name}>'

    
    def test(self, commands:list):
        self.game.test(self)
        tprint(self.game, 'Тестирование началось')
        
    
    def get_weakness(self, weapon:Weapon) -> float:
        return 1
    
    
    def get_shield(self) -> Shield:
        """Метод возвращает щит героя."""
        
        if not self.shield.empty:
            return self.shield
        elif not self.removed_shield.empty:
            return self.removed_shield
        return None

    
    def check_backpack(self) -> bool:
        """Метод возвращает True если у героя есть рюкзак"""
        return not self.backpack.no_backpack
    
    
    def do(self, command:str):
        """
        Метод обрабатывает команды, переданные герою и 
        передает управление соответствующей команде функции.
        
        Входящие параметры:
        - command - команда от пользователя, полученная из чата игры
        
        """
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

    
    def poison_enemy(self, target:Monster) -> str:
        """
        Метод проводит проверку, отравил герой противника при атаке, или нет.
        
        Входящие параметры:
        - target - монстр, которого атакует герой

        """
        
        if target.poisoned or target.venomous:
            return None
        if self.weapon.is_poisoned():
            poison_die = dice(1, s_weapon_poison_level)
        else:
            poison_die = 0
        base_protection_die = dice(1, s_poison_base_protection_die)
        additional_protection_die = 0
        if target.armor.is_poisoned() or target.shield.is_poisoned():
            additional_protection_die = dice(1, s_poison_additional_protection_die)
        protection = base_protection_die + additional_protection_die
        if poison_die > protection:
            target.poisoned = True
            return f'{target.name} получает отравление, {target.g(["он", "она"])} теперь неважно себя чувствует.'
        return None
    
    
    def hit_chance(self):
        """Метод рассчитывает и возвращает значение шанса попадания героем по монстру."""
        
        return self.dext + self.weapon_mastery[self.weapon.type]['level']
    
    
    def change(self, what:str=None):
        """Метод обрабатывает команду "сменить". """
        
        if what not in ['оружие']:
            tprint(self.game, f'{self.name} не знает, зачем нужно это менять.')
        if what == 'оружие':
            self.change_weapon_actions()
    
    
    def change_weapon_actions(self):
        """Метод моделирует различные варианты смены оружия."""
        
        second_weapon = self.get_second_weapon()
        if not self.weapon.empty and not second_weapon.empty:
            self.change_weapon()
        elif self.weapon.empty and not second_weapon.empty:
            self.take_out_weapon()
        elif not self.weapon.empty and second_weapon.empty:
            tprint(self.game, f'{self.name} не может сменить оружие из-за того, что оно у {self.g(["него", "нее"])} одно.')
        else:
            tprint(self.game, f'{self.name} не может сменить оружие. У {self.g(["него", "нее"])} и оружия-то нет.')
    
       
    def change_weapon(self):
        """Метод вызывается если герой может сменить оружие и меняет его."""
        
        message = []
        second_weapon = self.get_second_weapon()
        message.append(f'{self.name} убирает {self.weapon.name1} в рюкзак и берет в руки {second_weapon.name1}.')
        if second_weapon.twohanded and not self.shield.empty:
            self.removed_shield = self.shield
            self.shield = self.game.no_shield
            message.append(f'Из-за того, что {second_weapon.name1} - двуручное оружие, щит тоже приходится убрать.')
        elif not second_weapon.twohanded and not self.removed_shield.empty:
            message.append(f'У {self.g(["героя", "героини"])} теперь одноручное оружие, поэтому {self.g(["он", "она"])} может достать щит из-за спины.')
        self.backpack.remove(second_weapon, self)
        self.backpack.append(self.weapon)
        self.weapon = second_weapon
        tprint(self.game, message)
        
    
    def take_out_weapon(self):
        """Метод вызывается если герой был без оружие и достает его из рюкзака."""
        
        message = []
        second_weapon = self.get_second_weapon()
        message.append(f'{self.name} достает из рюкзака {second_weapon.name1} и берет в руку.')
        if second_weapon.twohanded and not self.shield.empty:
            self.removed_shield = self.shield
            self.shield = self.game.no_shield
            message.append(f'Из-за того, что {second_weapon.name1} - двуручное оружие, щит приходится убрать за спину.')
        self.backpack.remove(second_weapon, self)
        self.weapon = second_weapon
        tprint(self.game, message)
        
    
    def g(self, words_list:list) -> str:
        """
        Метод получает на вход список из двух слов и
        выбирает нужное слово в зависимости от пола игрока. 
        В списке первым должно идти слово, соответствующее мужскому полу, 
        а вторым - соответствующее женскому.
        
        """
        
        return words_list[self.gender]
    
    
    def drop(self, item:str=None) -> bool:
        """Метод обрабатывает команду "бросить". """
        
        game = self.game
        item = item.lower()
        shield_in_hand = not self.shield.empty
        shield_removed = not self.removed_shield.empty
        if not item or item in ['все', 'всё']:
            tprint(game, f'{self.name} {self.g(["хотел", "хотела"])} бы бросить все и уйти в пекари, но в последний момент берет себя в руки и продолжает приключение.')
        elif item.isdigit():
            return self.drop_digit(item)
        else:
            if shield_in_hand and self.shield.check_name(item):
                return self.drop_shield()
            elif shield_removed and self.remove_shield.check_name(item):
                return self.drop_removed_shield()
            elif self.weapon.check_name(item):
                return self.drop_weapon()
            elif self.backpack.check_name(item):
                return self.drop_backpack()
            else:
                return self.drop_item(item=item)
   
    
    def drop_digit(self, number:str) -> bool:
        """
        Метод обрабатывает ситуацию, когда в команду "бросить" 
        в качестве аргумента передан порядковый номер предмета.
        
        """
        
        game = self.game
        room = self.current_position
        number = int(number)
        item = self.backpack.get_item_by_number(number)
        if item:
            room.loot.add(item)
            self.backpack.remove(item, room)
            tprint(game, f'{self.name} бросает {item.name} на пол комнаты.')
            return True
        else:
            tprint(game, f'{self.name} не {self.g(["нашел", "нашла"])} такой вещи у себя в рюкзаке.')
            return False
    
    
    def drop_backpack(self) -> bool:
        """Метод выбрасывания рюкзака."""
        
        if self.backpack.no_backpack:
            return False
        game = self.game
        room = self.current_position
        room.loot.add(self.backpack)
        tprint(game, f'{self.name} снимает рюкзак и кладет в угол комнаты.')
        self.backpack = game.no_backpack
        return True    
    
    
    def drop_shield(self) -> bool:
        """Метод выбрасывания щита."""
        
        if self.shield.empty:
            return False
        game = self.game
        room = self.current_position
        room.loot.add(self.shield)
        tprint(game, f'{self.name} швыряет {self.shield.name} на пол комнаты.')
        self.shield = game.no_shield
        return True
    
    
    def drop_removed_shield(self) -> bool:
        """Метод выбрасывания щита, который убран за спину."""
        
        if self.removed_shield.empty:
            return False
        game = self.game
        room = self.current_position
        room.loot.add(self.removed_shield)
        tprint(game, f'{self.name} достает {self.removed_shield.name} из-за спины и ставит его к стене.')
        self.removed_shield = game.no_shield
        return True
    
    
    def drop_weapon(self) -> bool:
        """Метод выбрасывания оружия."""
        
        if self.weapon.empty:
            return False
        game = self.game
        room = self.current_position
        room.loot.add(self.weapon)
        tprint(game, f'{self.name} бросает {self.weapon.name} в угол комнаты.')
        self.weapon = game.no_weapon
        return True
    
    
    def drop_item(self, item:str) -> bool:
        """Метод выбрасывания вещи из рюкзака."""
        
        game = self.game
        room = self.current_position
        item_to_drop = self.backpack.get_first_item_by_name(item)
        if item_to_drop:
            self.backpack.remove(item_to_drop, room)
            room.loot.add(item_to_drop)
            tprint(game, f'{self.name} бросает {item_to_drop.name} на пол комнаты.')
            return True
        else:
            tprint(game, f'{self.name} роется в рюкзаке, но не находит ничего такого.')
            return False
    
    
    def rest(self, what=None):
        """Метод обрабатывает команду "отдохнуть". """
        
        room = self.current_position
        if not self.check_rest_possibility(room=room):
            return False
        if self.check_monster_in_ambush(place=room):
            return False
        self.repair_shield_while_rest()
        self.sleep_while_rest()
        self.poisoned = False
        self.health = self.start_health
        self.save_room = room
        self.restless = 10
        return True
    
    
    def sleep_while_rest(self):
        """Метод моделирует сон героя во время отдыха."""
        
        message = []
        dream_count = dice(1, s_nightmare_probability)
        if dream_count == 1:
            message.append(f'Провалившись в сон {self.name} видит ужасный кошмар. \
                           Так толком и не отдохнув {self.g(["герой", "героиня"])} просыпается с тревогой в душе.')
            self.fear = self.fear // s_nightmare_divider
        else:
            message.append(f'{self.name} ложится спать и спит так сладко, что все страхи и тревоги уходят прочь.')
            self.fear = 0
        stolen_item = self.get_robbed_while_sleep()
        if stolen_item:
            message.append(stolen_item)
        tprint(self.game, message)
        
    
    def get_robbed_while_sleep(self) -> str:
        """
        Метод моделирует то, что героя ограбили во время сна.
        Метод возвращает строку текста, которая добавляется к сообщению о сне.
        
        """
        
        steal_count = dice(1, s_steal_probability)
        if steal_count == 1 and not self.backpack.is_empty():
            all_monsters = [monster for monster in self.floor.all_monsters if (not monster.stink and monster.can_steal)]
            stealing_monster = randomitem(all_monsters)
            all_items = self.backpack.get_items_except_class(Key)
            if all_items:
                item = randomitem(all_items)
                self.backpack.remove(item, stealing_monster)
                stealing_monster.take(item)
                return f'Проснувшись {self.name} лезет в свой рюкзак и обнаруживает, что кто-то украл {item.name1}.'
        return None
    
    
    def repair_shield_while_rest(self):
        """Метод починки щита во время отдыха."""
        
        shield = self.get_shield()
        if shield:
            need_money = shield.accumulated_damage * s_shield_repair_multiplier // 1
            if need_money > 0 and self.money >= need_money:
                shield.accumulated_damage = 0
                self.money -= need_money
                tprint(self.game, f'Пока отдыхает {self.name} успешно чинит {shield.name1}')
    
    
    def check_monster_in_ambush(self, place) -> bool:
        """
        Метод проверки, выскочил ли из засады монстр.
        
        Принимает на вход:
        - place - объект места, в котором может спрятаться монстр.
        Сейчас используются классы Room и Furniture.
        
        Если монстр выскакивает из засады, то сразу же начинается схватка.
        """
        
        monster = place.monster_in_ambush()
        message = []
        if monster:
            monster.hiding_place = None
            message.append(f'Неожиданно из засады выскакивает {monster.name} и нападает на {self.name1}.')
            if monster.frightening:
                message.append(f'{monster.name} очень {monster.g(["страшный", "страшная"])} и {self.name} пугается до икоты.')
                self.fear += 1
            tprint(self.game, message)
            self.fight(monster.name, True)
            return True
        return False
    
    
    def check_rest_possibility(self, room:Room) -> bool:
        """Метод проверки, может ли герой отдыхать в комнате."""
        
        cant_rest, rest_place = room.can_rest()
        message = []
        if self.restless > 0:
            cant_rest.append(f'У {self.g(["героя", "героини"])} столько нерастраченной энергии, что {self.g(["ему", "ей"])} не сидится на месте')
        if not rest_place or len(cant_rest) > 0:
            message.append('В этой комнате нельзя этого делать.')
            message.append(randomitem(cant_rest))
            tprint(self.game, message)
            return False
        return True
    
    
    def remove(self, what=None) -> bool:
        """Метод обрабатывает команду "убрать". """
        
        if not what:
            tprint(self.game, f'{self.name} оглядывается по сторонам, \
                находит какой-то мусор и закидывает его в самый темный угол комнаты.')
            return False
        if what.lower() in ['щит', self.shield.name.lower(), self.shield.name1.lower()]:
            return self.remove_shield()
        else:
            tprint(self.game, f'{self.name} не понимает, как это можно убрать.')
            return False
    
    
    def remove_shield(self) -> bool:
        """Метод убирания щита за спину."""
        
        if not self.shield.empty:
            self.shield, self.removed_shield = self.removed_shield, self.shield
            tprint(self.game, f'{self.name} убирает {self.removed_shield.real_name()[1]} за спину.') 
            return True
        return False
        
    
    def repair(self, what=None) -> bool:
        """Метод обрабатывает команду "чинить". """
        
        if not what:
            tprint(self.game, f'{self.name} не может чинить что-нибудь. Нужно понимать, какую вещь ремонтировать.')
            return False
        if self.shield.check_name(what) or self.removed_shield.check_name(what):
            return self.repair_shield()
        tprint(self.game, f'{self.name} не умеет чинить такие штуки.')
        return False

    
    def repair_shield(self) -> bool:
        """
        Метод починки щита.
        Щит чинится за деньги. Если у героя не хватает денег, 
        то щит починен не будет.
        
        """
        
        game = self.game
        shield = self.get_shield()
        if not shield:
            tprint(game, f'У {self.g(["героя", "героини"])} нет щита, так что и ремонтировать нечего.')
            return False
        needed_money = shield.accumulated_damage * s_shield_repair_multiplier // 1
        if needed_money == 0:
            tprint(game, f'{shield.name1} не нужно ремонтировать.')
            return False
        if self.money >= needed_money:
            shield.accumulated_damage = 0
            self.money.how_much_money -= needed_money
            tprint(game, f'{self.name} успешно чинит {shield.name1}')
            self.decrease_restless(1)
            return True
        else:
            tprint(game, f'{self.name} и {self.g(["рад", "рада"])} бы починить {shield.name1}, но {self.g(["ему", "ей"])} не хватает денег на запчасти.')
            return False
        
    
    def get_second_weapon(self) -> Weapon:
        """
        Метод ищет в рюкзаке героя оружие. 
        Если оружие найдено, возвращает его. 
        Если оружие не найдено, возвращается объект "Пустое оружие".
        
        """       
        item = self.backpack.get_first_item_by_class(Weapon)
        if item:
            return item
        return self.game.no_weapon

    
    def generate_run_away_text(self, target:Monster) -> str:
        """
        Метод генерирует текст, который выводится в чат если 
        герой убегает из схватки.
        
        """
        
        if target.frightening:
            fright_text = 'в ужасе '
        else:
            fright_text = ''
        if self.check_light():
            message_text = f'{self.name} {fright_text}сбегает с поля боя.'
        else:
            message_text = f'{self.name} в кромешной тьме {fright_text}пытается убежать хоть куда-нибудь.'
        return message_text
    
    
    def lose_weapon_or_shield(self, target:Monster) -> str:
        """
        Метод моделирует потерю героем экипировки 
        когда он сбегает из схватки.
        Герой может потерять оружие или щит.
        Метод возвращает описывающую ситуацию строку текста.
        
        """
        
        room = self.current_position
        a = dice(1, 2)
        if a == 1 and not self.weapon.empty:
            if target.weapon.empty and target.carryweapon:
                target.weapon = self.weapon
            else:
                room.loot.add(self.weapon)
            self.weapon = self.game.no_weapon
            return f'Убегая {self.name} роняет из рук {self.weapon.name1}.'
        elif a == 2 and not self.shield.empty:
            if target.shield.empty and target.carryshield:
                target.shield = self.shield
            else:
                room.loot.add(self.shield)
            self.shield = self.game.no_shield
            return f'Убегая {self.name} теряет {self.shield.name1}.'
        return None
    
    
    def lose_random_items(self) -> list[str]:
        """
        Метод моделирует потерю героем вещей из рюкзака 
        когда он сбегает из схватки.
        Метод возвращает список потерянных вещей.
        
        """
        
        room = self.current_position
        items_list = []
        a = dice(0, self.backpack.count_items())
        if a > 0:
            items_list.append(f'{self.name} бежит настолько быстро, что не замечает, как теряет:')
            for _ in range(a):
                item = self.backpack.get_random_item()
                items_list.append(item.name1)
                room.loot.add(item)
                self.backpack.remove(item, room)
        return items_list
      
    
    def run_away(self, target: Monster) -> list:
        """
        Метод обрабатывает команду "убежать". 
        Запускается когда герой сбегает из боя.

        Входящие параметры:
        - target - Монстр, от которого убегает герой

        Исходящие параметры:
        - Возвращает текст сообщения в виде массива строк
        
        """
        
        room = self.current_position
        available_directions = room.get_available_directions()
        self.rage = 0
        self.hide = False
        message = [
            self.generate_run_away_text(target=target),
            self.lose_weapon_or_shield(target=target)
        ]
        message += self.lose_random_items()        
        if self.check_light():
            direction = randomitem(available_directions)
        else:
            direction = dice(0, 3)
            if direction not in available_directions:
                message.append(f'{self.name} с разбега врезается в стену и отлетает в сторону. Схватка продолжается.')
                tprint(self.game, message)
                return
        new_position = self.current_position.position + self.floor.directions_dict[direction]
        self.current_position = self.floor.plan[new_position]
        self.current_position.visited = '+'
        self.run = True
        message.append('На этом схватка заканчивается.')
        self.restless = 0
        tprint (self.game, message)

    
    def get_target_name(self, target:Monster) ->str:
        """
        Метод возвращает два имени противника - 
        в именительном и винительном падежах.
        
        """
        
        if self.check_light():
            return target.name, target.get_name('accus')
        else:
            return 'Неизвестная тварь из темноты', 'черт знает кого'
            
    
    def generate_rage(self) -> int:
        """Метод генерирует значение ярости героя."""
        
        if self.check_light():
            if self.rage > 1:
                rage = dice(2, self.rage)
            else:
                rage = 1
        else:
            rage = 1
        return rage
    
    
    def generate_poison_strength(self) -> int:
        """Метод генерирует значение силы отравления, которое испытывает герой."""
        
        if self.poisoned:
            poison_strength = dice(1, self.stren // 2)
        else:
            poison_strength = 0
        return poison_strength
    
    
    def generate_mele_attack(self) -> int:
        """Метод генерирует значение атаки голыми руками."""
        
        rage = self.generate_rage()
        poison_strength = self.generate_poison_strength()
        if self.check_light():
            mele_attack = dice(1, self.stren - poison_strength) * rage
        else:
            mele_attack = dice(1, self.stren - poison_strength) // dice(1, s_dark_damage_divider_dice)
        return mele_attack
                
    
    def generate_weapon_attack(self, target:Monster) -> int:
        """Метод генерирует значение дополнительной атаки оружием."""
        if self.weapon.empty:
            return 0
        if isinstance(target, Vampire) and self.weapon.element() == 4:
            return target.health
        weapon_attack = self.weapon.attack(target)
        weapon_mastery = self.weapon_mastery[self.weapon.type]['level']
        critical_probability = weapon_mastery * s_critical_step
        if dice(1, 100) <= critical_probability and not self.poisoned:
            weapon_attack = weapon_attack * s_critical_multiplier
        return weapon_attack
    
    
    def generate_total_attack(self, target:Monster) -> int:
        """Метод генерирует общее значение атаки героя по противнику."""
        
        mele_attack = self.generate_mele_attack()
        weapon_attack = self.generate_weapon_attack(target=target)
        return mele_attack + weapon_attack
        
        
    def generate_total_damage(self, target:Monster, total_attack:int) ->int:
        """Метод генерирует значение урона, который наносит противнику атака героя."""
        
        target_defence = target.defence(self)
        if target_defence < 0 or total_attack < target_defence:
            return 0, target_defence
        else:
            return total_attack - target_defence, target_defence
        
    
    def break_enemy_shield(self, target:Monster, total_attack:int) -> str:
        """Метод проверяет, смог ли герой сломать вражеский щит."""
        
        if target.shield.empty:
            return None
        else:
            shield = target.shield
            r = dice(1, s_shield_crushed_upper_limit)
            damage_to_shield = total_attack * target.shield.accumulated_damage
            if r < damage_to_shield:
                self.game.all_shields.remove(shield)
                target.shield = self.game.no_shield
            return f' {self.name} наносит настолько сокрушительный удар, что ломает щит соперника.'    
    
        
    def increase_weapon_mastery(self) -> str:
        """Метод увеличивает мастерство владения определенным типом оружия по итогу схватки."""
        
        if self.weapon.empty:
            return None
        weapon_type = self.weapon.type
        mastery = self.weapon_mastery.get(weapon_type)
        mastery['counter'] += dice(1, 10)/100
        if mastery['counter'] > mastery['level']:
            mastery['counter'] = 0
            mastery['level'] += 1
            return f' {self.g(["Герой", "Героиня"])} теперь немного лучше знает, как использовать {weapon_type} оружие.'
        return None
       
    
    def hit_enemy(self, target:Monster) -> int:
        """Метод моделирует удар героя по врагу во время схватки."""
        
        message = []
        game = self.game
        target_name, target_name_accusative = self.get_target_name(target=target)
        tprint(game, showsides(self, target, self.floor))
        self.hide = False
        total_attack = self.generate_total_attack(target=target)
        if not self.weapon.empty:
            action = randomitem(self.weapon.actions)
            hit_string = f'{self.name} {action} {target_name_accusative} используя {self.weapon.name1} и наносит {total_attack}+{howmany(total_attack, "единицу,единицы,единиц")} урона.'
        else:
            hit_string = f'{self.name} бьет {target_name_accusative} не используя оружие и наносит {howmany(total_attack, "единицу,единицы,единиц")} урона. '
        message.append(hit_string)
        total_damage, target_defence = self.generate_total_damage(target=target, total_attack=total_attack)
        if target_defence < 0:
            message.append(f' {target.name} {target.g(["смог", "смогла"])} увернуться от атаки и не потерять ни одной жизни.')
        elif total_damage == 0:
            message.append(f'{self.name} не {self.g(["смог", "смогла"])} пробить защиту {target_name_accusative}.')
        elif total_damage > 0:
            damage_string = f'{target_name} не имеет защиты и теряет {howmany(total_damage, "жизнь,жизни,жизней")}.'
            message += [
                damage_string,
                self.break_enemy_shield(target=target, total_attack=total_attack),
                self.poison_enemy(target=target),
                self.increase_weapon_mastery()
            ] 
        target.health -= total_damage
        self.rage = 0
        tprint(game, message)
    
    
    def attack(self, target, action):
        """Метод обрабатывает команду "атаковать". """
        
        self.run = False
        if action == '' or action == 'у' or action == 'ударить':
            self.hit_enemy(target=target)
            return
        elif action in ['з', 'защититься', 'защита']:
            self.use_shield(target)
            return
        elif action in ['б', 'бежать', 'убежать']:
            self.run_away(target)
            return
        elif action in ['и', 'использовать']:
            self.use_in_fight()
            return
        elif action in ['с', 'сменить оружие', 'сменить']:
            self.change_weapon()
            tprint(self.game, f'\n{self.name} продолжает бой.')
            return
        return True

    
    def use_in_fight(self):
        """
        Метод использования вещей в бою.

        Входящие параметры:
        - item - наименование предмета, который нужно использовать.
        
        """
        
        game = self.game
        can_use = self.backpack.get_items_for_fight()
        if len(can_use) == 0:
            tprint(game, f'{self.name} не может ничего использовать. В рюкзаке нет вещей, которые были бы полезны в бою.')
            return
        message = []
        message.append(f'{self.name} может использовать следующие предметы:')
        for item in can_use:
            message.append(f'{str(can_use.index(item) + 1)}: {item.name1}')
        message.append('Выберите номер предмета или скажите "отмена" для прекращения.')
        game.selected_item = can_use
        game.state = 4
        tprint(game, message, 'use_in_fight')
    
    
    def use_shield(self, target):
        """Метод использования щита."""
        
        game = self.game
        if self.shield.empty:
            tprint(self.game, 'У {self.g(["героя", "героини"])} нет щита, так что защищаться {self.g(["он", "она"])} не может.')
        else:
            tprint(game, showsides(self, target, self.floor))
            self.hide = True
            self.rage += 1
            tprint(self.game, f'{self.name} уходит в глухую защиту, терпит удары и накапливает ярость.')

    
    def show(self):
        """
        Метод генерирует и выводит на экран описание персонажа
        
        """
        message = []
        money_text = self.show_me_money()
        message.append(f'{self.name} - это {self.g(["смелый герой", "смелая героиня"])} {str(self.level)} уровня. ' 
                       f'{self.g(["Его", "Ее"])} сила - {str(self.stren)}, ловкость - {str(self.dext)}, интеллект - {str(self.intel)} и сейчас'
                       f' у {self.g(["него", "нее"])} {howmany(self.health, "единица,единицы,единиц")} здоровья, что составляет '
                       f'{str(self.health * 100 // self.start_health)} % от максимально возможного. {money_text}')
        message.append(self.show_weapon())
        message.append(self.show_protection())
        message.append(self.show_mastery())
        tprint(self.game, message)

    
    def show_mastery(self) -> str:
        """Метод генерирует описание мастерства персонажа."""
        
        mastery_text = ''
        for mastery in self.weapon_mastery:
            if self.weapon_mastery[mastery]['level'] > 0:
                mastery_text += f' {mastery} ({self.weapon_mastery[mastery]["level"]})'
        if mastery_text:
            mastery_text = mastery_text[1::]
            text = f'{self.g(["Герой", "Героиня"])} обладает знаниями про {normal_count(mastery_text, "(")} оружие.'
            return text
        return ''
    
    
    def show_me_money(self) -> str:
        """Метод генерирует описание денег персонажа."""
        
        if self.money >= 2:
            money_text = f'В кошельке звенят {howmany(self.money.how_much_money, "монета,монеты,монет")}.'
        elif self.money == 1:
            money_text = f'Одна-единственная монета оттягивает карман героя.'
        else:
            money_text = f'{self.name} {self.g(["беден", "бедна"])}, как церковная мышь.'
        return money_text
    
    
    def show_weapon(self) -> str:
        """Метод генерирует описание оружия персонажа."""
        
        if not self.weapon.empty:
            weapon_text = f'{self.weapon.real_name()[0]} в руке {self.g(["героя", "героини"])} добавляет к {self.g(["его", "ее"])} силе ' \
                          f'{str(self.weapon.damage)}+{str(self.weapon.perm_damage())}.'
        else:
            weapon_text = f'{self.name} предпочитает сражаться голыми руками.'
        return weapon_text
    
    
    def show_protection(self) -> str:
        """Метод генерирует описание защиты персонажа."""
        
        shield_text = self.shield.show()
        armor_text = self.armor.show()
        protection_text = f'{self.g(["Героя", "Героиню"])} '
        if not self.shield.empty and not self.armor.empty:
            protection_text += f'защищают {shield_text} и {armor_text}.'
        elif not self.shield.empty and self.armor.empty:
            protection_text += f'защищает {shield_text}.'
        elif self.shield.empty and not self.armor.empty:
            protection_text += f'защищает {armor_text}.'
        else:
            protection_text = f'У {self.g(["героя", "героини"])} нет ни щита, ни доспехов.'
        return protection_text
    
    
    def damage_shield(self):
        """Метод моделирует урон, который наносится щиту персонажа во время схватки."""
        
        if self.hide:
            dice_result = dice(s_shield_damage_when_hiding_min, s_shield_damage_when_hiding_max) / 100
            self.shield.accumulated_damage += dice_result
        else:
            dice_result = dice(s_shield_damage_min, s_shield_damage_max) / 100
            self.shield.accumulated_damage += dice_result
            
    
    def try_to_parry(self, attacker:Monster) -> bool:
        """Метод проверки, удалось ли персонажу увернуться от удара врага."""
        
        weapon = attacker.weapon
        parry_chance = self.dext + self.weapon_mastery[weapon.type]['level']
        if self.poisoned:
            parry_chance -= self.dext // 2
        parry_die = dice(1, parry_chance)
        hit_die = dice(1, (attacker.hit_chance + weapon.hit_chance))
        if parry_die > hit_die:
            return True
        return False
    
    
    def defence(self, attacker: Monster) -> int:
        """
        Метод рассчитывает сумму защиты героя против атаки монстра.

        Входящие параметры:
        - attacker - атакующий монстр

        Исходящие параметры:
        - Значение защиты с учетом доспехов и щита.
        
        """
        result = 0
        if not self.shield.empty:
            result += self.shield.protect(attacker)
            self.damage_shield()
        if not self.armor.empty:
            result += self.armor.protect(attacker)
        if self.try_to_parry(attacker=attacker):
            result = -1
        return result

    
    def lose(self, winner:Monster=None):
        """
        Метод сбрасывает состояние героя при его проигрыше в бою

        Входящие параметры:
        - winner - атакующий монстр (пока не используется).
        
        """
        self.health = self.start_health
        self.stren = self.start_stren
        self.dext = self.start_dext
        self.intel = self.start_intel
        self.current_position = self.save_room
        self.restless = 0
    
    
    def win(self, loser):
        """Метод обрабатыват событие победы в схватке."""
        
        self.health = self.start_health
        self.stren = self.start_stren
        self.dext = self.start_dext
        self.intel = self.start_intel
        self.wins += 1
        tprint(self.game, f'{self.name} получает {howmany(loser.exp, "единицу,единицы,единиц")} опыта!')
        self.gain_experience(exp=loser.exp)
        self.restless = 0

    
    def gain_experience (self, exp:int):
        """Метод увеличения опыта героя после схватки."""
        
        self.exp += exp
        if self.exp > self.levels[self.level]:
            self.game.state = 3
            level_up_message = [f'{self.name} получает новый уровень!']
            level_up_message.append('Что необходимо прокачать: здоровье, силу, ловкость или интеллект?')
            tprint(self.game, level_up_message, 'levelup')
            self.level += 1
    
    
    def levelup(self, message:str):
        """
        Метод обрабатывает команды, приходящие от игрока во время увеличения уровня героя.
        
        """
        if message == 'здоровье':
            self.health += 3
            self.start_health += 3
            tprint(self, f'{self.name} получает 3 единицы здоровья.', 'direction')
        elif message == 'силу':
            self.stren += 1
            self.start_stren += 1
            tprint(self.game, f'{self.name} увеличивает свою силу на 1.', 'direction')
        elif message == 'ловкость':
            self.dext += 1
            self.start_dext += 1
            tprint(self.game, f'{self.name} увеличивает свою ловкость на 1.', 'direction')
        elif message == 'интеллект':
            self.intel += 1
            self.start_intel += 1
            tprint(self.game, f'{self.name} увеличивает свой интеллект на 1.', 'direction')
        self.game.state = 0
        return True

    
    def game_over(self, goal_type, goal=None):
        """Метод проверяет, не произошло ли событие окончания игры."""
        
        if goal_type == 'killall':
            if self.game.monsters() == 0:
                tprint(self.game, f'{self.name} {self.g(["убил", "убила"])} всех монстров в замке и {self.g(["выиграл", "выиграла"])} в этой игре!')
                return True
            else:
                return False
        return False

    
    def show_backpack(self):
        """Метод генерирует описание рюкзака героя."""
        
        message = []
        if not self.check_light():
            message.append(f'В комнате слишком темно чтобы рыться в рюкзаке')
        else:
            message += self.backpack.show(self)
            message.append(self.money.show())
            if not self.removed_shield.empty:
                message.append(f'За спиной у {self.g(["героя", "героини"])} висит {self.removed_shield.real_name()[0]}')
        tprint(self.game, message)
        return True
    
    
    def key_hole(self, direction):
        """Метод генерирует текст сообщения когда герой смотрит через замочную скважину."""
        
        room = self.current_position
        door = room.doors[s_hero_doors_dict[direction]]
        if door.empty:
            message = f'{self.name} осматривает стену и не находит ничего заслуживающего внимания.'
        elif self.fear >= s_fear_limit:
            message = f'{self.name} не может заставить себя заглянуть в замочную скважину. Слишком страшно.'
        else:
            what_position = room.position + self.floor.directions_dict[direction]
            room_behind_the_door = self.floor.plan[what_position]
            message = room_behind_the_door.show_through_key_hole(self)
        tprint(self.game, message)
        return True
       
    def look_at_shield(self) -> str:
        """Метод генерирует текст осмотра своего щита."""
        
        if not self.check_light():
            return f'Из-за темноты нельзя осмотреть даже собственный щит.'
        else:
            return self.shield.show()
    
    def look_at_weapon(self) -> str:
        """Метод генерирует текст осмотра собственного оружия."""
        
        if not self.check_light():
            return f'В такой темноте оружие можно только ощупать, но это не даст полезной информации.'
        else:
            return self.weapon.show()
        
    def look_at_armor(self) -> str:
        """Метод генерирует текст осмотра своих доспехов."""
        
        if not self.check_light():
            return 'Так темно, что не видно, что на тебе надето.'
        else:
            return self.armor.show()

    
    def look_at_furniture(self, what:str) -> list[str]:
        """Метод генерирует текст осмотра мебели."""
        
        room = self.current_position
        message = []
        for i in room.furniture:
            if i.name1 == what:
                message += (i.show())
        return message
    
    
    def look(self, what:str=None):
        """Метод обрабатывает команду "осмотреть". """
        
        game = self.game
        room = self.current_position
        monster = room.monsters(mode='first')
        if not self.check_light():
            tprint(game, f'В комнате совершенно неподходящая обстановка чтобы что-то осматривать. Сперва надо зажечь свет.')
            return
        if not what:
            room.show(game.player)
            room.map()
        if what == 'себя':
            self.show()
        if what == 'рюкзак':
            self.show_backpack()
        if self.floor.directions_dict.get(what):
            self.key_hole(what)
        if monster and what: 
            if what.lower() in [monster.name.lower(),
                                monster.get_name('accus').lower(),
                                monster.name[0].lower(),
                                'монстр', 
                                'врага', 
                                'монстра', 
                                'враг', 
                                'противника', 
                                'противник']:
                tprint(game, showsides(self, monster, self.floor))
        if what in self.weapon.real_name(all=True, additional=['оружие']):
            tprint(game, self.look_at_weapon())
        if what in self.shield.real_name(all=True, additional=['щит']):
            tprint(game, self.look_at_shield())
        if what in self.armor.real_name(all=True, additional=['защиту', 'доспехи', 'доспех']):
            tprint(game, self.look_at_armor())
        if [f for f in room.furniture if f.name1 == what]:
            tprint(game, self.look_at_furniture(what=what))

    
    def check_monster_and_figth(self):
        """
        Метод проверяет, есть ли в комнате монстр, 
         и, если этот монстр агрессивен, начинает схватку.
         
         """
        
        room = self.current_position
        monster = room.monsters('first')
        if monster:
            if monster.agressive and self.check_light():
                self.fight(monster.name, True)
    
    
    def go(self, direction:str):
        """Метод обрабатывает команду "идти". """
        
        game = self.game
        door = self.current_position.doors[s_hero_doors_dict[direction]]
        if not self.floor.directions_dict.get(direction):
            tprint(game, f'{self.name} не знает такого направления!')
            return False
        elif door.empty:
            if self.check_light():
                tprint(game, f'Там нет двери. {self.name} не может туда пройти!')
            else:
                tprint(game, f'В темноте {self.name} врезается во что-то носом.')
            return False
        elif door.locked:
            if self.check_light():
                tprint(game, f'Эта дверь заперта. {self.name} не может туда пройти, нужен ключ!')
            else:
                tprint(game, f'В темноте {self.name} врезается во что-то носом.')
            return False
        else:
            self.game.trigger_on_movement()
            new_position = self.current_position.position + self.floor.directions_dict[direction]
            self.current_position = self.floor.plan[new_position]
            self.current_position.visited = '+'
            self.current_position.show(self)
            self.current_position.map()
            self.decrease_restless(1)
            self.check_monster_and_figth()
            return True

    
    def fight(self, enemy, agressive=False):
        """Метод обрабатывает команду "атаковать". """
        
        game = self.game
        room = self.current_position
        who_is_fighting = room.monsters(mode='first')
        if not who_is_fighting:
            tprint(game, 'Не нужно кипятиться. Тут некого атаковать')
            return False
        if not enemy in [who_is_fighting.name, who_is_fighting.get_name('accus'), who_is_fighting.name[0]] and enemy != '':
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
            if self.check_light():
                message = [f'{who_is_fighting.name} начинает схватку!']
            else:
                message = ['Что-то жуткое и непонятное нападает первым из темноты.']
            tprint(game, message, 'fight')
            who_is_fighting.attack(self)
            return True

    
    def search_room(self) -> bool:
        """Метод обыскивания комнаты."""
        
        room = self.current_position
        message = []
        if self.check_monster_in_ambush(place=room):
            return False
        for furniture in room.furniture:
            message.append(str(furniture))
        if not room.loot.empty and len(room.loot.pile) > 0:
            message.append('В комнате есть:')
            message += room.loot.show_sorted()
        else:
            message.append('В комнате нет ничего интересного.')
        if room.has_a_corpse():
            message + room.show_corpses()
        tprint(self.game, message)
        return True
    
    
    def check_if_hero_can_search(self) -> bool:
        """
        Метод проверяет, может ли герой обыскивать что-либо в комнате, 
        в которой он находится.
        
        """
        
        game = self.game
        room = self.current_position
        enemy_in_room = room.monsters('first')
        if not self.check_light():
            tprint(game, 'В комнате настолько темно, что невозможно что-то отыскать.')
            return False
        if enemy_in_room:
            tprint(game, f'{enemy_in_room.name} мешает толком осмотреть комнату.')
            return False
        if self.fear >= s_fear_limit:
            tprint(game, f'{self.name} не хочет заглядывать в неизвестные места. \
                Страх сковал {self.g(["его", "ее"])} по рукам и ногам.')
            return False
        return True
    
    
    def search_secret_place(self, item:str) -> bool:
        """Метод обыскивания секретного места комнаты."""
        
        game = self.game
        room = self.current_position
        if room.secret_word.lower() == item.lower():
            if not room.secret_loot.pile:
                tprint(game, f'{self.name} осматривает {item} и ничего не находит.')
            else:
                message = []
                message.append(f'{self.name} осматривает {item} и находит:')
                message += room.secret_loot.show_sorted()
                room.secret_loot.transfer(room.loot)
                message.append('Все, что было спрятано, теперь лежит на виду.')
                tprint(game, message)
            return True
        return False
     
     
    def search_corpse(self, item:str) -> bool:
        """Метод обыскивания трупа."""
        
        game = self.game
        room = self.current_position
        if not room.has_a_corpse():
            return False
        corpse = None
        if item.lower() == 'труп':
            corpse = room.morgue[0]
        else:
            for candidate in room.morgue:
                if item.lower() == candidate.name.lower():
                    corpse = candidate
        if not corpse:
            return False
        if not corpse.loot.pile:
            tprint(game, f'{self.name} осматривает {corpse.name} и ничего не находит.')
        else:
            message = []
            message.append(f'{self.name} осматривает {corpse.name} и находит:')
            message += corpse.loot.show_sorted()
            corpse.loot.transfer(room.loot)
            message.append('Все ценное, что было у трупа, теперь разбросано по полу комнаты.')
            tprint(game, message)
        return True
        
    
    def search_furniture(self, item:str) -> bool:
        """Метод обыскивания мебели."""
        
        room = self.current_position
        game = self.game
        what_to_search = None
        for i in room.furniture:
            if item.lower() in [i.name.lower(), i.name1.lower()]:
                what_to_search = i
        if not what_to_search:
            tprint(game, 'В комнате нет такой вещи.')
            return False
        if what_to_search.locked:
            tprint(game, f'Нельзя обыскать {what_to_search.name1}. Там заперто.')
            return False
        if self.check_monster_in_ambush(place=what_to_search):
            return False
        return self.get_loot_from_furniture(what=what_to_search)
        
    
    def get_loot_from_furniture(self, what:Furniture) -> bool:
        """Метод извлекает весь лут из обысканной мебели."""
        
        room = self.current_position
        if what.loot == 0:
            tprint(self.game, f'{what.name} {what.empty_text}'.capitalize())
            return False
        message = [f'{self.name} осматривает {what.name1} и находит:']
        message += what.loot.show_sorted()
        what.loot.transfer(room.loot)
        message.append('Все, что было спрятано, теперь лежит на виду.')
        tprint(self.game, message)
        return True
    
    
    def search(self, item:str=None) -> bool:
        """Метод обрабатывает команду "обыскать". """
        
        if not self.check_if_hero_can_search():
            return False
        if not item:
            return self.search_room()
        if self.search_secret_place(item=item):
            return True
        if self.search_corpse(item=item):
            return True
        return self.search_furniture(item=item)
        

    def can_take(self, obj) -> bool:
        """
        Метод проверяет, может ли герой взять объект себе.
        На вход передается любой объект из игры.
        
        """
        
        classes = [Weapon, Shield, Armor]
        for i in classes:
            if isinstance(obj, i):
                return False
        return True

    
    def take(self, item:str='все') -> bool:
        """Метод обрабатывает команду "взять". """
        
        game = self.game
        current_loot = self.current_position.loot
        if current_loot.empty:
            tprint(game, 'Здесь нечего брать.')
            return False
        if self.backpack.no_backpack:
            backpack_is_taken = self.try_to_take_backpack()
        if item in ['все', 'всё', '']:
            item_is_taken = self.take_all()
        else:
            item_is_taken = self.take_item_by_name(item)
        if not item_is_taken and not backpack_is_taken:
            tprint(game, 'Такой вещи здесь нет.')
        return item_is_taken or backpack_is_taken

    
    def try_to_take_backpack(self) -> bool:
        current_loot = self.current_position.loot        
        backpacks = current_loot.get_items_by_class(Backpack)
        if backpacks:
            backpacks[0].take(self)
            current_loot.remove(backpacks[0])
            return True
        tprint(self.game, f'У {self.g(["героя", "героини"])} нет рюкзака, поэтому {self.g(["он", "она"])} может взять только то, что может нести в руках')
        return False
    
    
    def take_item_by_name(self, name):
        current_loot = self.current_position.loot
        item = current_loot.get_first_item_by_name(item)
        if item:
            item.take(self)
            current_loot.remove(item)
            return True
        return False
    
    
    def take_all(self):
        current_loot = self.current_position.loot
        for item in current_loot.pile:
                if self.can_take(item):
                    item.take(self)
        return True
    
    
    def check_fear(self, print_message:bool=True) -> bool:
        """
        Метод проверки того, что герой испытывает страх.
        Если страх выше лимита, то на экран выводится сообщение, что ничего не получилось.
        Если в метод передан print_message=False, то сообщение не выводится.
        
        """
        
        if self.fear >= s_fear_limit:
            if print_message:
                tprint(self.game, f'{self.name} не может ничего сделать из-за того, что руки дрожат от страха.')
            return True
        return False
    
    
    def get_list_of_locked_objects(self, room:Room, what:str='') -> list:
        """
        Метод возвращает список всех запертых объектов в комнате.
        Пока работает только с мебелью, после доработки будут добавлены двери.
        
        """
        
        what_is_in_room = []
        for furniture in room.furniture:
            if what:
                if furniture.locked and what.lower() in [furniture.name.lower(), furniture.name1.lower()]:
                    what_is_in_room.append(furniture)
            else:
                if furniture.locked:
                    what_is_in_room.append(furniture)
        return what_is_in_room
    
    
    def check_if_hero_can_open(self) -> bool:
        """Метод проверяет, может ли герой что-то открывать."""
        
        game = self.game
        if self.check_fear():
            return False
        if not self.check_light():
            tprint(game, f'{self.name} шарит в темноте руками, но не нащупывает ничего интересного')
            return False
        key = self.backpack.get_first_item_by_class(Key)
        if not key:
            tprint(game, 'Чтобы что-то открыть нужен хотя бы один ключ.')
            return False
        return True
        
    def open_furniture(self, what:str) -> bool:
        """Метод отпирания мебели при помощи ключа."""
        
        game = self.game
        room = self.current_position
        what_is_locked = self.get_list_of_locked_objects(room=room, what=what)
        key = self.backpack.get_first_item_by_class(Key)
        if not what_is_locked:
            tprint(game, 'В комнате нет такой вещи, которую можно открыть.')
            return False
        if len(what_is_locked) > 1:
            tprint(game, f'В комнате слишком много запертых вещей. \
                {self.name} не понимает, что {self.g(["ему", "ей"])} нужно открыть.')
            return False
        furniture = what_is_locked[0]
        self.backpack.remove(key)
        furniture.locked = False
        tprint(game, f'{self.name} отпирает {furniture.name1} ключом.')
        return True
        
    
    def open_door(self, direction:str) -> bool:
        """Метод отпирания двери при помощи ключа."""
        
        game = self.game
        room = self.current_position
        key = self.backpack.get_first_item_by_class(Key)
        door = room.doors[s_hero_doors_dict[direction]]
        if  not door.locked:
            tprint(game, 'В той стороне нечего открывать.')
            return False
        else:
            self.backpack.remove(key)
            door.locked = False
            tprint(game, f'{self.name} открывает дверь.')
            return True
    
    
    def open(self, item:str='') -> bool:
        """Метод обрабатывает команду "открыть". """
        
        if not self.check_if_hero_can_open():
            return False
        if item == '' or not s_hero_doors_dict.get(item, False):
            return self.open_furniture(what=item)
        else:
            return self.open_door(direction=item)

    
    def take_out_shield(self) -> bool:
        """Метод доставания щита из-за спины."""
        
        if self.weapon.twohanded:
            tprint(self.game, f'{self.name} воюет двуручным оружием, поэтому не может взять щит.')
            return False
        self.shield, self.removed_shield = self.removed_shield, self.shield
        tprint(self.game, f'{self.name} достает {self.shield.real_name()[0]} из-за спины и берет его в руку.')
        return True
    
    
    def use_item_from_backpack(self, item_string:str) -> bool:
        """Метод использования штуки из рюкзака."""
        
        game = self.game
        if self.backpack.no_backpack:
            tprint(game, f'{self.name} где-то {self.g(["потерял", "потеряла"])} свой рюкзак и не может ничего использовать.')
            return False
        if item_string.isdigit():
            number = int(item_string)
            item = self.backpack.get_item_by_number(number)
        else:
            item = self.backpack.get_first_item_by_name(item_string)
        if item:
            item.use(self, in_action=False)
            return True
        tprint(game, f'{self.name} не {self.g(["нашел", "нашла"])} такой вещи у себя в рюкзаке.')
        return False
    
    
    def use(self, item:str=None) -> bool:
        """Метод обрабатывает команду "использовать". """
        
        game = self.game
        if not item:
            tprint(game, f'{self.name} не понимает, что {self.g(["ему", "ей"])} надо использовать.')
            return False
        if item.lower() in [self.removed_shield.name.lower(), self.removed_shield.name1.lower(), 'щит']:
            return self.take_out_shield()
        return self.use_item_from_backpack(item)

    
    def check_if_hero_can_enchant(self, item:str) -> bool:
        """Метод проверки, может ли герой что-то улучшать."""
        
        game = self.game
        rune_list = self.backpack.get_items_by_class(Rune)
        if item == '':
            tprint(game, f'{self.name} не понимает, что {self.g(["ему", "ей"])} надо улучшить.')
            return False
        if self.fear >= s_fear_limit:
            tprint(game, f'{self.name} дрожащими от страха руками пытается достать из рюкзака руну, \
                но ничего не получается.')
            return False
        if len(rune_list) == 0:
            tprint(game, f'{self.name} не может ничего улучшать. В рюкзаке не нашлось ни одной руны.')
            return False
        if not self.check_light():
            tprint(game, f'{self.name} не может ничего улучшать в такой темноте.')
            return False
        return True
    
    
    def chose_what_to_enchant(self, item:str) -> bool:
        """
        Метод возвращает вещь, которую герой будет улучшать.
        Принимает на вход строку из команды игрока, ищет эту строку 
        среди оружия, щитов и защиты, и возвращает найденную вещь.
        
        """
        
        game = self.game
        game.selected_item = game.empty_thing
        selected_item = None
        if item == 'оружие' and not self.weapon.empty:
            game.selected_item = self.weapon
            return True
        if item == 'щит':
            if not self.shield.empty:
                game.selected_item = self.shield
                return True
            elif not self.removed_shield.empty:
                game.selected_item = self.removed_shield
                return True
        if item in ['дооспех', 'доспехи'] and not self.armor.empty:
            game.selected_item = self.armor
            return True
        if item.isdigit():
            selected_item = self.backpack.get_item_by_number(int(item))
        else:
            selected_item = self.backpack.get_first_item_by_name(item)
        if isinstance(selected_item, Weapon):
                    game.selected_item = selected_item
                    return True
        tprint(game, f'{self.name} не умеет улучшать такую штуку.')
        return False
    
    
    def enchant(self, item='') -> bool:
        """
        Метод обрабатывает команду "улучшить".

        Входящие параметры:
        - item - наименование предмета, который нужно улучшить.
        Поддерживаются следующие значения:
            - 'оружие'
            - 'щит'
            - 'доспех' или 'доспехи'
        
        """
        game = self.game
        if not self.check_if_hero_can_enchant(item=item):
            return False
        if not self.chose_what_to_enchant(item=item):
            return False
        rune_list = self.backpack.get_items_by_class(Rune)
        text = []
        text.append(f'{self.name} может использовать следующие руны:')
        for rune in rune_list:
            text.append(f'{str(rune_list.index(rune) + 1)}: {str(rune)}')
        text.append('Выберите номер руны или скажите "отмена" для прекращения улучшения')
        game.state = 2
        tprint(game, text, 'enchant')

    
    def check_if_hero_can_read(self) -> bool:
        """Метод проверки, может ли герой сейчас читать."""
        
        game = self.game
        if self.fear >= s_fear_limit:
            tprint(game, f'{self.name} смотрит на буквы, но от страха они не складываются в слова.')
            return False
        if not self.check_light():
            tprint(game, f'{self.name} решает, что читать в такой темноте вредно для зрения.')
            return False
        return True
    
    
    def check_light(self) -> bool:
        """Метод проверки, есть ли в комнате свет."""
        
        room = self.current_position
        if room.light:
            return True
        if self.weapon.element() in s_glowing_elements:
            return True
        if self.shield.element() in s_glowing_elements:
            return True
        if self.armor.element() in s_glowing_elements:
            return True
        return False
        
    
    def get_book(self, item:str) -> Book|None:
        """
        Метод поиска книги в рюкзаке.
        Принимает на вход строку из команды игрока.
        Если передана пустая строка или просто "книга", 
        возвращает случайную книку.
        Если передана конкретная книга, возвращает ее.
        
        """
        
        game = self.game
        if not item or item == 'книгу':
            book = self.backpack.get_random_item_by_class(Book)
            message = f'{self.name} роется в рюкзаке и находит первую попавшуюся книгу.'
        else:
            book = self.backpack.get_first_item_by_name(item)
            message = f'{self.name} читает {book.name1}.'
        if book:
            tprint(game, message)
            return book
        return None 
    
    
    def read(self, what:str) -> bool:
        """Метод обрабатывает команду "читать". """
        
        if not self.check_if_hero_can_read():
            return False
        book = self.get_book(item=what)
        if book:
            message = [book.text]
            message.append(book.get_mastery_string(self))
            message.append(f'{self.g(["Он", "Она"])} решает больше не носить книгу с собой и оставляет ее в незаметном месте.')
            self.weapon_mastery[book.weapon_type]['level'] += 1
            self.backpack.remove(book)
        else:
            message = 'В рюкзаке нет ни одной книги. Грустно, когда нечего почитать.'
        tprint(self.game, message)
        self.decrease_restless(2)
        return True
    
    
    def decrease_restless(self, number:int) -> bool:
        """Метод уменьшает значение непоседливости героя. Герой не может отдыхать когда непоседливость больше 0."""
        
        if self.restless >= number:
            self.restless -= number
        return True
