from class_items import Key, Money, Rune, Map
from class_book import Book
from class_monsters import Monster, Vampire
from class_protection import Armor, Shield
from class_room import Furniture, Room, Ladder
from class_weapon import Weapon
from class_backpack import Backpack
from class_fight import Fight
from functions import howmany, normal_count, randomitem, tprint, roll, split_actions
from enums import state_enum, move_enum


class Hero:
    """Класс героя игры"""
    
    _nightmare_probability = 3
    """
    Вероятность того, что герой увидит кошмар во время отдыха. 
    Рассчитывается как 1/n, где n - это значение параметра.

    """

    _nightmare_divider = 2
    """Коэффициент, на который делится страх если приснился кошмар."""

    _steal_probability = 2 
    """
    Вероятность того, что героя обворуют во время отдыха. 
    Рассчитывается как 1/n, где n - это значение параметра.

    """
    
    _fear_limit = 5
    """Значение уровня страха героя, при котором он начинает отказываться делать определенные вещи."""
    
    _critical_step = 5
    """На сколько увеличивается вероятность критического удара оружием при увеличении мастерства на 1."""

    _critical_multiplier = 2
    """Коэффициент увеличения урона при критическом ударе."""
    
    _dark_damage_divider_die = 3
    """Кубик, который кидается, чтобы выяснить, во сколько раз уменьшится урон от атаки в темноте."""
    
    _doors_dict = {'наверх': 0,
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
    """Словарь направлений, в которых может пойти герой."""
    
    _poison_base_protection_die = 5
    """Кубик, который кидается чтобы определить базовую защиту от отравления."""

    _poison_additional_protection_die = 5
    """
    Кубик, который кидается чтобы определить дополнительную защиту от яда
    когда у героя или монстра ядовитые доспехи или щит.

    """
    
    _level_up_commands = ('здоровье',
                            '?',
                            'силу',
                            'ловкость',
                            'интеллект')
    """Список дополнительных комманд при прокачке уровня персонажа."""

    _fight_commands = ('ударить',
                        '?',
                        'защититься',
                        'бежать',
                        'сменить оружие',
                        'сменить',
                        'поменять',
                        'использовать')
    """Список комманд во время схватки."""
    
    _initiative_die = 20
    """Кубик инициативы"""
    
    def __init__(self,
                 game,
                 name:str = None,
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
        self.gender = gender
        self.poisoned = False
        self.stren = stren
        self.start_stren = self.stren
        self.dext = dext
        self.start_dext = self.dext
        self.intel = intel
        self.start_intel = self.intel
        self.health = health
        self.trap_mastery = 0
        self.trader = None
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
        self.state = state_enum.NO_STATE
        self.game_is_over = False
        self.start_health = self.health
        self.weakness = {}
        self.monster_knowledge = {}
        self.can_use_in_fight = []
        self.rune_list = []
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
        self.wounds = {}
        self.last_move = None
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
                            'подняться': self.go_up,
                            'подниматься': self.go_up,
                            'спуститься': self.go_down,
                            'спускаться': self.go_down,
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
                            'обезвредить': self.disarm,
                            'торговать': self.trade,
                            'изучить': self.examine,
                            'изучать': self.examine,
                            'улучшить': self.enchant}    
    
    
    def on_create(self):
        return None
    
    
    def __format__(self, format:str) -> str:
        if format == 'pronoun':
            if self.gender == 0:
                return 'он'
            return 'она'
        return self.lexemes.get(format, '')
         
    
    def __str__(self):
        return f'<Hero: name = {self.name}>'

    
    def is_hero(self) -> bool:
        return True
    
    
    def generate_initiative(self) -> int:
        return roll([Hero._initiative_die]) + self.dext
        
    
    def test(self, commands:list):
        self.game.test(self)
        tprint(self.game, 'Тестирование началось')
        
    
    def check_if_sneak_past_monster(self, monster: Monster) -> bool:
        die = [8 + roll([self.dext]) - monster.size]
        return roll(die) > 5
    
    
    def check_if_sneak_past_furniture(self) -> bool:
        return roll([3 + self.dext]) > 2
    
    
    def examine(self, what:str) -> bool:
        if not self.check_light():
            tprint(self.game, f'В этой комнате так темно, что {self.g("герой", "героиня")} не может изучить даже собственную ладонь.')
            return False
        items_list = self.find_what_to_examine()
        if not items_list:
            tprint(self.game, f'В этой комнате нечего изучать. Это довольно скучная комната.')
            return False
        if what:
            items_list = [item for item in items_list if item.check_name(what)]
            if not items_list:
                tprint(self.game, f'Эту штуку нельзя изучить.')
                return False
        for item in items_list:
            item.get_examined(self)
        return True 
    
    
    def increase_monster_knowledge(self, monster_type) -> bool:
        knowledge = self.monster_knowledge.get(monster_type, '0')
        self.monster_knowledge[monster_type] = knowledge + 1
        tprint(self.game, f'{self.name} больше узнает про {Monster._types[monster_type]["accus"]}')
        return True       
                   
    
    def find_what_to_examine(self) -> list:
        items = []
        if self.current_position.has_a_corpse():
            items.extend(self.current_position.morgue)
        return [item for item in items if not item.examined]
    
    
    def go_down(self, what:str) -> bool:
        if not self.check_light():
            return self.go_down_with_light_off()
        return self.go_down_with_light_on()
    
    
    def go_down_with_light_off(self) -> bool:
        room = self.current_position
        if not room.ladder_down or room.ladder_down.locked:
            tprint (self.game, f'{self:nom} шарит в темноте ногой по полу, но не находит, куда можно было бы спуститься.')
            return False
        return self.descend(room)


    def descend(self, room) -> bool:
        room_to_go = room.ladder_down.room_down
        self.last_move = move_enum.DOWNSTAIRS
        return self.move(room_to_go)
    
    
    def go_down_with_light_on(self) -> bool:
        room = self.current_position
        if not room.ladder_down:
            tprint (self.game, f'{self:nom} в недоумении смотрит на абсолютно ровный пол.' 
                    f'Как только {self.g("ему", "ей")} могла прийти в голову такая идея?')
            return False
        if room.ladder_down.locked:
           tprint (self.game, f'Крышка люка в полу не открывается. Похоже, она заперта.')
           return False
        return self.descend(room)
    
    
    def go_up(self, what:str) -> bool:
        if not self.check_light():
            return self.go_up_with_light_off()
        return self.go_up_with_light_on()
    
    
    def go_up_with_light_off(self) -> bool:
        room = self.current_position
        if not room.ladder_up or room.ladder_up.locked:
            tprint (self.game, f'{self:nom} ничего не может разглядеть в такой темноте.')
            return False
        return self.ascend(room)


    def ascend(self, room):
        room_to_go = room.ladder_up.room_up
        self.last_move = move_enum.UPSTAIRS
        return self.move(room_to_go)
    
    
    def go_up_with_light_on(self) -> bool:
        room = self.current_position
        if not room.ladder_up:
            tprint (self.game, f'{self:nom} и {self.g("хотел", "хотела")} бы забраться повыше, но в этой комнате нет такой возможности.')
            return False
        if room.ladder_up.locked:
           tprint (self.game, f'{self:nom} пытается поднять крышку люка, ведущего наверх, но она не поддается. Похоже, она заперта.')
           return False
        return self.ascend(room)

         
    def action(self, command:str, message:str):
        
        """Метод обработки комманд от игрока."""
        
        message = message.lower()
        if command in self.command_dict.keys() and self.state == state_enum.NO_STATE:
            if not self.game_over('killall'):
                self.do(message)
            return True
        actions = {
            state_enum.ENCHANT: self.rune_actions,
            state_enum.TRADE: self.trade_actions,
            state_enum.USE_IN_FIGHT: self.in_fight_actions,
            state_enum.FIGHT: self.fight_actions
        }
        if command in Hero._level_up_commands and self.state == state_enum.LEVEL_UP:
            self.levelup(command)
            return True
        action = actions.get(self.state, None)
        if action:
            return action(message)
        """ elif command in Hero._fight_commands and self.state == state_enum.FIGHT:
            return self.fight_actions(answer=answer) """
        tprint (self.game, f'{self.name} такого не умеет.', 'direction')
        return False


    def rune_actions(self, message:str) -> bool:
        
        """
        Метод обрабатывает команды игрока когда он улучшает предметы при помощи рун.
        
        Возвращает:
        - True - если удалось улучшить предмет
        - False - если предмет по любой причине не улучшился
        
        """
        
        rune_list = self.rune_list
        self.state = state_enum.NO_STATE
        if message == 'отмена':
            self.state = state_enum.NO_STATE
            return False
        if not message.isdigit():
            tprint(self, f'Чтобы все заработало {self:dat} нужно просто выбрать руну по ее номеру. Проще говоря, просто ткнуть в нее пальцем', 'fight')
            return False
        message = int(message) - 1
        if not message < len(rune_list):
            tprint(self, f'{self.name} не находит такую руну у себя в карманах.', 'direction')
            return False
        if not self.selected_item:
            tprint(self, f'{self.name} вертит руну в руках, но не может вспомнить, куда {self.g("он хотел", "она хотела")} ее поместить.', 'direction')
            self.state = state_enum.NO_STATE
            return False
        chosen_rune = rune_list[message]
        rune_is_placed = self.selected_item.enchant(chosen_rune)
        if not rune_is_placed:
            tprint(self, f'Похоже, что {self.name} не может вставить руну в {self.selected_item:occus}.', 'direction')
            self.state = state_enum.NO_STATE
            return False
        tprint(self, f'{self.name} улучшает {self.selected_item:occus} новой руной.', 'direction')
        self.backpack.remove(chosen_rune)
        self.rune_list = self.backpack.get_items_by_class(Rune)
        self.state = state_enum.NO_STATE
        return True
    
    
    def in_fight_actions(self, message:str) -> bool:
        
        """
        Метод обрабатывает команды игрока когда он что-то использует во время боя.
        
        Возвращает:
        - True - если удалось использовать предмет
        - False - если предмет по любой причине не был использован
        
        """
        if message == 'отмена':
            tprint(self, f'{self.name} продолжает бой.', 'fight')
            self.state = state_enum.FIGHT
            return False
        if not message.isdigit():
            tprint(self, f'Чтобы все заработало {self:dat} нужно просто выбрать вещь по ее номеру. Проще говоря, просто ткнуть в нее пальцем', 'fight')
            return False
        items = self.can_use_in_fight
        message = int(message) - 1
        if not message < len(items):
            tprint(self, f'{self.name} не находит такую вещь у себя в карманах.', 'fight')
            return False
        item = items[message]
        item_is_used = item.use(who_using=self, in_action=True)
        if not item_is_used:
            tprint(self, f'Похоже, что {self.name} не может использовать {item:occus}.', 'fight')
            self.state = state_enum.FIGHT
            return False    
        self.state = state_enum.FIGHT
        return True
    
    
    def fight_actions(self, message:str) -> bool:
        
        """
        Метод обрабатывает команды игрока когда он дерется с монстром.
                
        """

        enemy = self.current_position.monsters('first')
        tprint(self.game, self.attack(enemy, message))
        if self.run:
            self.run = False
            self.look()
            self.state = state_enum.NO_STATE
        elif enemy.run:
            self.state = state_enum.NO_STATE
        elif enemy.health > 0 and self.state == state_enum.FIGHT:
            enemy.attack(self)
        elif self.state == state_enum.FIGHT:
            tprint(self.game, f'{self.name} побеждает в бою!', 'off')
            self.state = state_enum.NO_STATE
            enemy.lose(self)
            self.win(enemy)
        return True
    
    
    def trade_actions(self, message:str) -> bool:
        action, target = split_actions(message)
        if not self.trader:
            tprint(self.game, 'Похоже, торговец отказывается общаться и торговля сейчас невозможна.')
            self.state = state_enum.NO_STATE
            return False
        if action in ['закончить', 'отмена', 'уйти']:
            return self.leave_shop()
        if action in ['купить', 'покупать'] and target:
            return self.buy_item(target)
        if action in ['продать', 'продавать'] and target:
            return self.sell_item(target)
        tprint(self.game, 'Герой сейчас находится в лавке торговца, а здесь такие выкрутасы недопустимы.')
        return False
    
    
    def leave_shop(self):
        self.state = state_enum.NO_STATE
        tprint(self.game, f'{self.name} покидает лавку {self.trader:gen}.')
        self.trader = None
        return True
    
    
    def buy_item(self, target:str) -> bool:
        result = self.trader.sell(target, self)
        if result:
            tprint(self.game, self.trader.get_prices(self.backpack))
    
    
    def sell_item(self, target:str) -> bool:
        result = self.trader.buy(target, self)
        if result:
            tprint(self.game, self.trader.get_prices(self.backpack))
            
            
    def trade(self, what:str=None) -> bool:
        """
        Метод обрабатывает команду "торговать".        
        """
        game = self.game
        room = self.current_position
        trader = room.trader
        if not trader:
            tprint(game, 'В этой комнате не с кем торговать')
            return False
        message = [f'{self.name} подходит к {trader:dat} и начинат изучать товары.']
        message.extend(trader.get_prices(self.backpack))
        tprint(game, message)
        self.state = state_enum.TRADE
        self.trader = trader
        return True
    
    
    def disarm(self, what:str) -> bool:
        """
        Пытается обезвредить указанный объект. В текущей реализации поддерживается обезвреживание ловушек.
        
        :param what: Строка, указывающая, что нужно обезвредить. Поддерживаются значения 'ловушку', 'ловушка', и пустая строка для обезвреживания ловушки.
        :return: Возвращает True, если удалось обезвредить объект, иначе False.
        """
        if what in ['ловушку', 'ловушка', '']:
            return self.disarm_trap()
    
    
    def disarm_trap(self) -> bool:
        """
        Пытается обезвредить ловушку в текущем помещении.

        Метод проверяет наличие ловушки в текущем помещении (`current_position`). Если ловушка отсутствует,
        выводит сообщение о том, что герой не видит ловушек, и возвращает `False`. В случае обнаружения ловушки
        формирует сообщение о попытке обезвреживания и вызывает метод `try_to_disarm_trap()` для попытки обезвреживания.
        Результат работы `try_to_disarm_trap()` добавляется к сообщению, которое затем выводится.

        :return: Возвращает `True`, если ловушка успешно обезврежена, иначе `False`.
        """
        trap = self.current_position.get_trap()
        if not trap:
            tprint(self.game, f'{self.name} не видит в этом помещении никаких ловушек.')
            return False
        message = [f'{self.name} пытается обезвредить ловушку, прикрепленную к {trap.where:dat}.']
        message.extend(self.try_to_disarm_trap(trap))
        tprint(self.game, message)
    
    
    def try_to_disarm_trap(self, trap) -> list[str]:
        """
        Пытается обезвредить ловушку, с которой столкнулся герой.

        Этот метод сначала рассчитывает шанс героя на успешное обезвреживание ловушки, 
        затем сравнивает его со сложностью ловушки. Если шанс обезвреживания меньше сложности ловушки, 
        ловушка срабатывает, вызывая соответствующий метод. В противном случае ловушка считается успешно обезвреженной, 
        и герой получает опыт в обезвреживании ловушек.

        Параметры:
            - trap: Объект ловушки, которую необходимо обезвредить.

        Возвращает:
            Список строк, описывающих результат попытки обезвреживания ловушки.
        """
        disarm_chance = self.get_disarm_trap_chance()
        trap_difficulty = trap.get_difficulty()
        if disarm_chance < trap_difficulty:
            return trap.trigger(self)
        message = trap.disarm()
        message.append(f'{self.name} теперь лучше понимает, какую опасность представляют ловушки, и как с ними правильно обращаться.')
        self.increase_trap_mastery()
        return message
    
    
    def increase_trap_mastery(self):
        """
        Увеличивает мастерство героя в обезвреживании ловушек на 1.
        
        Этот метод увеличивает значение атрибута `trap_mastery` на единицу, что отражает улучшение навыков героя в обнаружении и обезвреживании ловушек.
        """
        self.trap_mastery += 1    


    def get_disarm_trap_chance(self) -> int:
        """
        Рассчитывает и возвращает шанс героя на успешное обезвреживание ловушки.
        
        Шанс обезвреживания ловушки зависит от ловкости (`dext`) героя и его мастерства обезвреживания ловушек (`trap_mastery`).
        Значение шанса определяется путем броска кубика с параметрами, зависящими от указанных атрибутов.
        
        :return: Целое число, представляющее шанс на успешное обезвреживание ловушки.
        """
        return roll([self.dext, self.trap_mastery])
                
        
    def generate_map_text(self, in_action: bool = False) -> list[bool, str]:
        if not in_action:
            if self.fear >= Hero._fear_limit:
                return False, f'{self.name} от страха не может сосредоточиться и что-то разобрать на карте.'
            elif not self.current_position.light:
                return False, f'В комнате слишком темно чтобы разглядывать карту'
            else:
                return True, f'{self.name} смотрит на карту этажа замка.'
        else:
            return False, 'Во время боя это совершенно неуместно!'
    
    
    def intel_wound(self) -> str:
        """
        Наносит персонажу ранение, влияющее на интеллект, увеличивая счетчик таких ранений на 1.
        Возвращает строку, описывающую получение ранения персонажем.
        
        :return: Строка с описанием получения ранения.
        """
        wound = self.wounds.get('intel', 0)
        self.wounds['intel'] = wound + 1
        return f'{self.name} получает удар по голове, что отрицательно сказывается на {self.g("его", "ее")} способности к здравым рассуждениям.'
    
    
    def stren_wound(self) -> str:
        """
        Наносит персонажу ранение, влияющее на силу, увеличивая счетчик таких ранений на 1.
        Возвращает строку, описывающую получение ранения персонажем.
        
        :return: Строка с описанием получения ранения.
        """
        wound = self.wounds.get('stren', 0)
        self.wounds['stren'] = wound + 1
        return f'{self.name} получает ранение и теряет много крови. Из-за раны {self:pronoun} сильно слабеет.'
    
    
    def dex_wound(self) -> str:
        """
        Наносит персонажу ранение, влияющее на ловкость, увеличивая счетчик таких ранений на 1.
        Возвращает строку, описывающую получение ранения персонажем.
        
        :return: Строка с описанием получения ранения.
        """
        wound = self.wounds.get('dex', 0)
        self.wounds['dex'] = wound + 1
        return f'{self.name} получает ранение в ногу и теперь двигается как-то неуклюже и гораздо медленнее.'
            
#TODO       
    def get_weakness(self, weapon:Weapon) -> float:
        return 1
    
    
    def get_shield(self) -> Shield|None:
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

    
    def poison_enemy(self, target:Monster) -> str|None:
        """
        Метод проводит проверку, отравил герой противника при атаке, или нет.
        
        Входящие параметры:
        - target - монстр, которого атакует герой

        """
        
        if target.poisoned or target.venomous:
            return None
        if self.weapon.is_poisoned():
            poison_die = roll([Weapon._poison_level])
        else:
            poison_die = 0
        base_protection_die = roll([Hero._poison_base_protection_die])
        additional_protection_die = 0
        if target.armor.is_poisoned() or target.shield.is_poisoned():
            additional_protection_die = roll([Hero._poison_additional_protection_die])
        protection = base_protection_die + additional_protection_die
        if poison_die > protection:
            target.poisoned = True
            return f'{target.name} получает отравление, {target:pronoun} теперь неважно себя чувствует.'
        return None
    
    
    def hit_chance(self) -> int:
        """Метод рассчитывает и возвращает значение шанса попадания героем по монстру."""
        
        dext_wound = self.wounds.get('dext', 0)
        wound_modifier = roll([dext_wound])
        return self.dext + self.weapon_mastery[self.weapon.type]['level'] - wound_modifier
    
    
    def parry_chance(self) -> int:
        """Метод рассчитывает и возвращает значение шанса парирования атаки."""
        
        dext_wound = self.wounds.get('dext', 0)
        wound_modifier = roll([dext_wound])
        chance = self.dext + self.weapon_mastery[self.weapon.type]['level'] - wound_modifier
        if self.poisoned:
            chance -= self.dext // 2
        if chance < 0:
            chance = 0
        return chance
    
    
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
            tprint(self.game, f'{self.name} не может сменить оружие из-за того, что оно у {self.g("него", "нее")} одно.')
        else:
            tprint(self.game, f'{self.name} не может сменить оружие. У {self.g("него", "нее")} и оружия-то нет.')
    
       
    def change_weapon(self):
        """Метод вызывается если герой может сменить оружие и меняет его."""
        
        message = []
        second_weapon = self.get_second_weapon()
        message.append(f'{self.name} убирает {self.weapon:occus} в рюкзак и берет в руки {second_weapon:occus}.')
        if second_weapon.twohanded and not self.shield.empty:
            self.removed_shield = self.shield
            self.shield = self.game.no_shield
            message.append(f'Из-за того, что {second_weapon:nom} - двуручное оружие, щит тоже приходится убрать.')
        elif not second_weapon.twohanded and not self.removed_shield.empty:
            message.append(f'У {self.g("героя", "героини")} теперь одноручное оружие, поэтому {self:pronoun} может достать щит из-за спины.')
        self.backpack.remove(second_weapon, self)
        self.backpack.append(self.weapon)
        self.weapon = second_weapon
        tprint(self.game, message)
        
    
    def take_out_weapon(self):
        """Метод вызывается если герой был без оружие и достает его из рюкзака."""
        
        message = []
        second_weapon = self.get_second_weapon()
        message.append(f'{self.name} достает из рюкзака {second_weapon:occus} и берет в руку.')
        if second_weapon.twohanded and not self.shield.empty:
            self.removed_shield = self.shield
            self.shield = self.game.no_shield
            message.append(f'Из-за того, что {second_weapon:nom} - двуручное оружие, щит приходится убрать за спину.')
        self.backpack.remove(second_weapon, self)
        self.weapon = second_weapon
        tprint(self.game, message)
        
    
    def g(self, he_word:str, she_word:str) -> str:
        """
        Метод получает на вход два слова и
        выбирает нужное слово в зависимости от пола игрока. 
        Первым должно идти слово, соответствующее мужскому полу, 
        а вторым - соответствующее женскому.
        
        """
        if self.gender == 0:
            return he_word
        return she_word
    
    
    def drop(self, item:str=None) -> bool:
        """Метод обрабатывает команду "бросить". """
        
        game = self.game
        item = item.lower()
        shield_in_hand = not self.shield.empty
        shield_removed = not self.removed_shield.empty
        if not item or item in ['все', 'всё']:
            tprint(game, f'{self.name} {self.g("хотел", "хотела")} бы бросить все и уйти в пекари, но в последний момент берет себя в руки и продолжает приключение.')
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
            tprint(game, f'{self.name} не {self.g("нашел", "нашла")} такой вещи у себя в рюкзаке.')
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
        dream_count = roll([Hero._nightmare_probability])
        if dream_count == 1:
            message.append(f'Провалившись в сон {self.name} видит ужасный кошмар. \
                           Так толком и не отдохнув {self.g("герой", "героиня")} просыпается с тревогой в душе.')
            self.fear = self.fear // Hero._nightmare_divider
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
        
        steal_count = roll([Hero._steal_probability])
        if steal_count == 1 and not self.backpack.is_empty():
            all_monsters = [monster for monster in self.floor.all_monsters if (not monster.stink and monster.can_steal)]
            stealing_monster = randomitem(all_monsters)
            all_items = self.backpack.get_items_except_class(Key)
            if all_items:
                item = randomitem(all_items)
                self.backpack.remove(item, stealing_monster)
                stealing_monster.take(item)
                return f'Проснувшись {self.name} лезет в свой рюкзак и обнаруживает, что кто-то украл {item:occus}.'
        return None
    
    
    def repair_shield_while_rest(self):
        """Метод починки щита во время отдыха."""
        
        shield = self.get_shield()
        if shield:
            repair_price = shield.get_repair_price()
            if repair_price > 0 and self.money >= repair_price:
                shield.repair()
                self.money -= repair_price
                tprint(self.game, f'Пока отдыхает {self.name} успешно чинит {shield.get_full_names("occus")}')
    
    
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
            message.append(f'Неожиданно из засады выскакивает {monster.name} и нападает на {self:occus}.')
            if monster.frightening:
                message.append(f'{monster.name} очень {monster.g("страшный", "страшная")} и {self.name} пугается до икоты.')
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
            cant_rest.append(f'У {self.g("героя", "героини")} столько нерастраченной энергии, что {self.g("ему", "ей")} не сидится на месте')
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
        if self.shield.check_name(what):
            return self.remove_shield()
        else:
            tprint(self.game, f'{self.name} не понимает, как это можно убрать.')
            return False
    
    
    def remove_shield(self) -> bool:
        """Метод убирания щита за спину."""
        
        if not self.shield.empty:
            self.shield, self.removed_shield = self.removed_shield, self.shield
            tprint(self.game, f'{self.name} убирает {self.removed_shield.get_full_names("occus")} за спину.') 
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
            tprint(game, f'У {self.g("героя", "героини")} нет щита, так что и ремонтировать нечего.')
            return False
        repair_price = shield.get_repair_price()
        if repair_price == 0:
            tprint(game, f'{shield:accus} не нужно ремонтировать.')
            return False
        if self.money >= repair_price:
            shield.repair()
            self.money.how_much_money -= repair_price
            tprint(game, f'{self.name} успешно чинит {shield:accus}')
            self.decrease_restless(1)
            return True
        else:
            tprint(game, f'{self.name} и {self.g("рад", "рада")} бы починить {shield:accus}, но {self.g("ему", "ей")} не хватает денег на запчасти.')
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

    
    def generate_in_fight_description(self, index:int) -> str:
        line = f'{index}: {self.name}: сила - d{str(self.stren)}'
        line += self.generate_weapon_text()
        line += self.generate_protection_text()
        line += f', жизней - {str(self.health)}. '
        return line
    
    
    def generate_weapon_text(self) -> str:
        if not self.weapon.empty:
            return f'+d{str(self.weapon.damage)}+{str(self.weapon.perm_damage())}'
        return ''
    
    
    def generate_protection_text(self) -> str:
        if not self.shield.empty and self.armor.empty:
            return f', защита - d{str(self.shield.protection)}+{str(self.shield.perm_protection())}'
        elif self.shield.empty and not self.armor.empty:
            line += f', защита - d{str(self.armor.protection)}+{str(self.armor.perm_protection())}'
        elif not self.shield.empty and not self.armor.empty:
            line += f', защита - d{str(self.armor.protection)}+{str(self.armor.perm_protection())} + d{str(self.shield.protection)}+{str(self.shield.perm_protection())}'
        return ''
     
        
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
        a = roll([2])
        if a == 1 and not self.weapon.empty:
            if target.weapon.empty and target.carryweapon:
                target.weapon = self.weapon
            else:
                room.loot.add(self.weapon)
            self.weapon = self.game.no_weapon
            return f'Убегая {self.name} роняет из рук {self.weapon:accus}.'
        elif a == 2 and not self.shield.empty:
            if target.shield.empty and target.carryshield:
                target.shield = self.shield
            else:
                room.loot.add(self.shield)
            self.shield = self.game.no_shield
            return f'Убегая {self.name} теряет {self.shield:accus}.'
        return None
    
    
    def lose_random_items(self) -> list[str]:
        """
        Метод моделирует потерю героем вещей из рюкзака 
        когда он сбегает из схватки.
        Метод возвращает список потерянных вещей.
        
        """
        
        room = self.current_position
        items_list = []
        items_quantity = self.backpack.count_items()
        a = roll([items_quantity + 1])
        if a < items_quantity:
            items_list.append(f'{self.name} бежит настолько быстро, что не замечает, как теряет:')
            for _ in range(a):
                item = self.backpack.get_random_item()
                items_list.append(item.lexemes["accus"])
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
            direction = roll([4]) - 1
            if direction not in available_directions:
                message.append(f'{self.name} с разбега врезается в стену и отлетает в сторону. Схватка продолжается.')
                tprint(self.game, message)
                return
        new_position = self.current_position.position + self.floor.directions_dict[direction]
        self.current_position = self.floor.plan[new_position]
        self.current_position.visited = True
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
            return target.name, target.get_name("accus")
        else:
            return 'Неизвестная тварь из темноты', 'черт знает кого'
            
    
    def generate_rage(self) -> int:
        """Метод генерирует значение ярости героя."""
        
        if self.check_light():
            return roll([self.rage])
        return 1
    
    
    def generate_poison_effect(self) -> int:
        """Метод генерирует значение силы отравления, которое испытывает герой."""
        
        if self.poisoned:
            return roll([self.stren // 2])
        return 0
    
    
    def get_real_strength(self) -> int:
        strength_wound = self.wounds.get('stren', 0)
        wound_modifier = roll([strength_wound])
        poison_effect = self.generate_poison_effect()
        return self.stren - wound_modifier - poison_effect
        
    
    def generate_mele_attack(self) -> int:
        """Метод генерирует значение атаки голыми руками."""
        
        rage = self.generate_rage()
        strength = self.get_real_strength()
        strength_die = roll([strength])
        if self.check_light():
            return strength_die * rage
        return strength_die // roll([Hero._dark_damage_divider_die])
                
    
    def generate_weapon_attack(self, target:Monster) -> int:
        """Метод генерирует значение дополнительной атаки оружием."""
        if self.weapon.empty:
            return 0
        if isinstance(target, Vampire) and self.weapon.element() == 4:
            return target.health
        weapon_attack = self.weapon.attack(target)
        weapon_mastery = self.weapon_mastery[self.weapon.type]['level']
        critical_probability = weapon_mastery * Hero._critical_step
        if roll([100]) <= critical_probability and not self.poisoned:
            weapon_attack = weapon_attack * Hero._critical_multiplier
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
        
        shield = target.shield
        if not shield.empty and shield.check_if_broken(total_attack):
            return f' {self.name} наносит настолько сокрушительный удар, что ломает щит соперника.'
        return None    
    
        
    def increase_weapon_mastery(self) -> str:
        """Метод увеличивает мастерство владения определенным типом оружия по итогу схватки."""
        
        if self.weapon.empty:
            return None
        weapon_type = self.weapon.type
        mastery = self.weapon_mastery.get(weapon_type)
        mastery['counter'] += roll([10])/100
        if mastery['counter'] > mastery['level']:
            mastery['counter'] = 0
            mastery['level'] += 1
            return f' {self.g("Герой", "Героиня")} теперь немного лучше знает, как использовать {weapon_type} оружие.'
        return None
       
    
    def hit_enemy(self, target:Monster) -> int:
        """Метод моделирует удар героя по врагу во время схватки."""
        
        message = []
        game = self.game
        target_name, target_name_accusative = self.get_target_name(target=target)
        self.hide = False
        total_attack = self.generate_total_attack(target=target)
        if not self.weapon.empty:
            action = randomitem(self.weapon.actions)
            hit_string = f'{self.name} {action} {target_name_accusative} используя {self.weapon:accus} и наносит {total_attack}+{howmany(total_attack, ["единицу", "единицы", "единиц"])} урона.'
        else:
            hit_string = f'{self.name} бьет {target_name_accusative} не используя оружие и наносит {howmany(total_attack, "единицу,единицы,единиц")} урона. '
        message.append(hit_string)
        total_damage, target_defence = self.generate_total_damage(target=target, total_attack=total_attack)
        if target_defence < 0:
            message.append(f' {target.name} {target.g("смог", "смогла")} увернуться от атаки и не потерять ни одной жизни.')
        elif total_damage == 0:
            message.append(f'{self.name} не {self.g("смог", "смогла")} пробить защиту {target_name_accusative}.')
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
        self.can_use_in_fight = self.backpack.get_items_for_fight()
        if not self.can_use_in_fight:
            tprint(game, f'{self.name} не может ничего использовать. В рюкзаке нет вещей, которые были бы полезны в бою.')
            return
        message = []
        message.append(f'{self.name} может использовать следующие предметы:')
        for item in self.can_use_in_fight:
            message.append(f'{str(self.can_use_in_fight.index(item) + 1)}: {item:accus}')
        message.append('Выберите номер предмета или скажите "отмена" для прекращения.')
        self.state = state_enum.USE_IN_FIGHT
        tprint(game, message, 'use_in_fight')
    
    
    def use_shield(self, target):
        """Метод использования щита."""
        
        game = self.game
        if self.shield.empty:
            tprint(self.game, f'У {self.g("героя", "героини")} нет щита, так что защищаться {self:pronoun} не может.')
        else:
            self.hide = True
            self.rage += 1
            tprint(self.game, f'{self.name} уходит в глухую защиту, терпит удары и накапливает ярость.')

    
    def show(self):
        """
        Метод генерирует и выводит на экран описание персонажа
        
        """
        message = []
        money_text = self.show_me_money()
        message.append(f'{self.name} - это {self.g("смелый герой", "смелая героиня")} {str(self.level)} уровня. ' 
                       f'{self.g("Его", "Ее")} сила - {str(self.stren)}, ловкость - {str(self.dext)}, интеллект - {str(self.intel)} и сейчас'
                       f' у {self.g("него", "нее")} {howmany(self.health, ["единица", "единицы", "единиц"])} здоровья, что составляет '
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
            text = f'{self.g("Герой", "Героиня")} обладает знаниями про {normal_count(mastery_text, "(")} оружие.'
            return text
        return ''
    
    
    def show_me_money(self) -> str:
        """Метод генерирует описание денег персонажа."""
        
        if self.money >= 2:
            money_text = f'В кошельке звенят {howmany(self.money.how_much_money, ["монета", "монеты", "монет"])}.'
        elif self.money == 1:
            money_text = f'Одна-единственная монета оттягивает карман героя.'
        else:
            money_text = f'{self.name} {self.g("беден", "бедна")}, как церковная мышь.'
        return money_text
    
    
    def show_weapon(self) -> str:
        """Метод генерирует описание оружия персонажа."""
        
        if not self.weapon.empty:
            weapon_text = f'{self.weapon.get_full_names("nom")} в руке {self.g("героя", "героини")} добавляет к {self.g("его", "ее")} силе ' \
                          f'{str(self.weapon.damage)}+{str(self.weapon.perm_damage())}.'
        else:
            weapon_text = f'{self.name} предпочитает сражаться голыми руками.'
        return weapon_text
    
    
    def show_protection(self) -> str:
        """Метод генерирует описание защиты персонажа."""
        
        shield_text = self.shield.show()
        armor_text = self.armor.show()
        protection_text = f'{self.g("Героя", "Героиню")} '
        if not self.shield.empty and not self.armor.empty:
            protection_text += f'защищают {shield_text} и {armor_text}.'
        elif not self.shield.empty and self.armor.empty:
            protection_text += f'защищает {shield_text}.'
        elif self.shield.empty and not self.armor.empty:
            protection_text += f'защищает {armor_text}.'
        else:
            protection_text = f'У {self.g("героя", "героини")} нет ни щита, ни доспехов.'
        return protection_text
    
    
    def damage_shield(self):
        """Метод моделирует урон, который наносится щиту персонажа во время схватки."""
        
        self.shield.take_damage(self.hide)
            
    
    def try_to_parry(self, attacker:Monster) -> bool:
        """Метод проверки, удалось ли персонажу увернуться от удара врага."""
        
        weapon = attacker.weapon
        chance = [self.parry_chance()]
        parry_die = roll(chance)
        hit_die = roll([attacker.hit_chance + weapon.hit_chance])
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
        tprint(self.game, f'{self.name} получает {howmany(loser.exp, ["единицу", "единицы", "единиц"])} опыта!')
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
                tprint(self.game, f'{self.name} {self.g("убил", "убила")} всех монстров в замке и {self.g("выиграл", "выиграла")} в этой игре!')
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
                message.append(f'За спиной у {self.g("героя", "героини")} висит {self.removed_shield.get_full_names("nom")}')
        tprint(self.game, message)
        return True
    
    
    def key_hole(self, direction):
        """Метод генерирует текст сообщения когда герой смотрит через замочную скважину."""
        
        room = self.current_position
        door = room.doors[Hero._doors_dict[direction]]
        if door.empty:
            message = f'{self.name} осматривает стену и не находит ничего заслуживающего внимания.'
        elif self.fear >= Hero._fear_limit:
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
            if i.lexemes["accus"].find(what) != -1:
                message += (i.show())
                message.append(self.get_trap_text(i))
        return message
    
    
    def get_trap_text(self, item) -> str|None:
        trap = item.trap
        if trap.activated and self.detect_trap(trap):
            return trap.get_detection_text()
        return None
    
    
    def detect_trap(self, trap) -> bool:
        """
        Пытается обнаружить ловушку, основываясь на интеллекте героя, его мастерстве обнаружения ловушек и ранениях.
        
        :param trap: Объект ловушки, который необходимо обнаружить.
        :return: Возвращает True, если ловушка обнаружена, иначе False.
        """
        if trap.seen:
            self.current_position.last_seen_trap = trap
            return True
        detection = roll([self.intel]) - roll([self.wounds['intel']]) + self.trap_mastery
        if detection > trap.difficulty:
            trap.seen = True
            self.current_position.last_seen_trap = trap
        return trap.seen
    
    
    def look(self, what:str=None):
        """Метод обрабатывает команду "осмотреть". """
        
        game = self.game
        room = self.current_position
        monster = room.monsters(mode='first')
        if what:
            what = what.lower()
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
        if self.weapon.check_name(what):
            tprint(game, self.look_at_weapon())
        if self.shield.check_name(what):
            tprint(game, self.look_at_shield())
        if self.armor.check_name(what):
            tprint(game, self.look_at_armor())
        if [f for f in room.furniture if f.lexemes["accus"].find(what) != -1]:
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
        
        direction_number = Hero._doors_dict.get(direction, False)
        if not direction_number:
            tprint(self.game, f'{self.name} не знает такого направления!')
            return False
        if self.check_light():
            return self.go_with_light_on(direction_number)
        return self.go_with_light_off(direction_number)
    
    
    def go_with_light_on(self, direction:int) -> bool:
        door = self.current_position.doors[direction]
        if door.empty:
            tprint(self.game, f'Там нет двери. {self.name} не может туда пройти!')
            return False
        if door.locked:
            tprint(self.game, f'Эта дверь заперта. {self.name} не может туда пройти, нужен ключ!')
            return False
        new_room_number = self.current_position.position + self.floor.directions_dict[direction]
        new_position = self.floor.plan[new_room_number]
        self.last_move = move_enum.get_move_by_number(direction)
        return self.move(new_position)
    
    
    def go_with_light_off(self, direction:int) -> bool:
        door = self.current_position.doors[direction]
        going_back = self.check_if_going_back(direction)
        if not going_back:
            sneak = self.sneak_through_dark_room()
            if not sneak:
                return False
        if door.empty or door.locked:
            tprint(self.game, f'В темноте {self.name} врезается во что-то носом.')
            return False
        new_room_number = self.current_position.position + self.floor.directions_dict[direction]
        new_position = self.floor.plan[new_room_number]
        self.last_move = move_enum.get_move_by_number(direction)
        return self.move(new_position)
    
    
    def sneak_through_dark_room(self) -> bool:
        room = self.current_position
        if room.has_a_monster():
            for monster in room.monsters():
                if not self.check_if_sneak_past_monster(monster):
                    tprint(self.game, f'{self.name} в темноте задевает что-то живое плечом и это что-то нападает.')
                    self.fight(monster.name, True)
                    return False
        if room.ladder_down:
            stayed = self.try_not_to_fall_down()
            if not stayed:
                return False
        if room.has_furniture() and not self.check_if_sneak_past_furniture():
            self.generate_noise(2)
            tprint(self.game, f'{self.name} в темноте врезается в какую-то мебель. Раздается оглушительный грохот.')
        return True
    
    
    def try_not_to_fall_down(self) -> bool:
        if not roll([3 + self.dext]) > 2:
            tprint(self.game, f'{self.name} медленно пробирается через темноту, но в какой-то момент перестает чувствовать пол под ногами и кубарем скатывается по лестнице вниз.')
            self.descend(self.current_position)
            return False
        return True
    
    
    def generate_noise(self, noise_level:int) -> None:
        return
    
    
    def check_if_going_back(self, direction:int) -> bool:
        return direction == self.last_move.countermove
       
    
    def move(self, new_position:Room) -> bool:
        self.game.trigger_on_movement()
        self.current_position = new_position
        self.current_position.visited = True
        self.current_position.show(self)
        self.current_position.map()
        self.decrease_restless(1)
        self.check_monster_and_figth()
        return True
    
    
    def fight(self, enemy:None):
        """Метод обрабатывает команду "атаковать". """
        
        room = self.current_position
        monsters_in_room = room.monsters(mode='first')
        if not monsters_in_room:
            tprint(self.game, 'Не нужно кипятиться. Тут некого атаковать')
            return False
        monsters_to_fight = []
        if enemy:
            for monster in monsters_in_room:
                if monster.check_name(enemy):
                    monsters_to_fight.append(monster)
        if not monsters_to_fight:
            tprint(self.game, f'{self.name} не может атаковать. В комнате нет такого существа.')
            return False
        if not enemy:
            monsters_to_fight = monsters_in_room
        monsters_to_fight.append(self)
        new_fight = Fight(
            game=self.game, 
            hero=self, 
            who_started=self, 
            fighters=monsters_to_fight
            )
        new_fight.start()
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
        if self.fear >= Hero._fear_limit:
            tprint(game, f'{self.name} не хочет заглядывать в неизвестные места. \
                Страх сковал {self.g("его", "ее")} по рукам и ногам.')
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
        for furniture in room.furniture:
            if furniture.check_name(item):
                what_to_search = furniture
        if not what_to_search:
            tprint(game, 'В комнате нет такой вещи.')
            return False
        if what_to_search.locked:
            tprint(game, f'Нельзя обыскать {what_to_search:accus}. Там заперто.')
            return False
        if what_to_search.check_trap():
            tprint(game, f'К несчастью в {what_to_search:prep} кто-то установил ловушку.')
            what_to_search.trap.trigger(self)
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
        message = [f'{self.name} осматривает {what:accus} и находит:']
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
        tprint(self.game, f'У {self.g("героя", "героини")} нет рюкзака, поэтому {self:pronoun} может взять только то, что может нести в руках')
        return False
    
    
    def take_item_by_name(self, name):
        current_loot = self.current_position.loot
        item = current_loot.get_first_item_by_name(name)
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
        current_loot.get_empty()
        return True
    
    
    def check_fear(self, print_message:bool=True) -> bool:
        """
        Метод проверки того, что герой испытывает страх.
        Если страх выше лимита, то на экран выводится сообщение, что ничего не получилось.
        Если в метод передан print_message=False, то сообщение не выводится.
        
        """
        
        if self.fear >= Hero._fear_limit:
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
                if furniture.locked and furniture.check_name(what):
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
            tprint(game, f'В комнате слишком много запертых вещей. {self.name} не понимает, что {self.g("ему", "ей")} нужно открыть.')
            return False
        furniture = what_is_locked[0]
        if furniture.check_trap():
            tprint(game, f'К несчастью в {furniture:prep} кто-то установил ловушку.')
            furniture.trap.trigger(self)
            return False
        self.backpack.remove(key)
        furniture.locked = False
        tprint(game, f'{self.name} отпирает {furniture:accus} ключом.')
        return True
        
    
    def open_door(self, direction:str) -> bool:
        """Метод отпирания двери при помощи ключа."""
        
        game = self.game
        room = self.current_position
        key = self.backpack.get_first_item_by_class(Key)
        door = room.doors[Hero._doors_dict[direction]]
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
        if Hero._doors_dict.get(item, False):
            return self.open_door(direction=item)
        if item in ['люк', 'лестницу']:
            return self.open_ladder()
        return self.open_furniture(what=item)     
        
    
    def open_ladder(self) -> bool:
        ladder, direction_string = self.choose_ladder_to_open()
        key = self.backpack.get_first_item_by_class(Key)
        if not ladder:
            tprint(self.game, f'В этой комнате нет лестниц, которые нужно было бы отпирать.')
            return False
        self.backpack.remove(key)
        ladder.locked = False
        tprint(self.game, f'{self.name} отпирает {ladder:accus}, ведущую {direction_string}, ключом.')
        return True
        
        
    def choose_ladder_to_open(self) -> tuple[Ladder|None, str]:
        room = self.current_position
        if room.ladder_up and room.ladder_up.locked:
            return room.ladder_up, 'вверх'
        if room.ladder_down and room.ladder_down.locked:
            return room.ladder_down, 'вниз'
        return None, ''

    
    def take_out_shield(self) -> bool:
        """Метод доставания щита из-за спины."""
        
        if self.weapon.twohanded:
            tprint(self.game, f'{self.name} воюет двуручным оружием, поэтому не может взять щит.')
            return False
        self.shield, self.removed_shield = self.removed_shield, self.shield
        tprint(self.game, f'{self.name} достает {self.shield.get_full_names("accus")} из-за спины и берет его в руку.')
        return True
    
    
    def use_item_from_backpack(self, item_string:str) -> bool:
        """Метод использования штуки из рюкзака."""
        
        game = self.game
        if self.backpack.no_backpack:
            tprint(game, f'{self.name} где-то {self.g("потерял", "потеряла")} свой рюкзак и не может ничего использовать.')
            return False
        if item_string.isdigit():
            number = int(item_string)
            item = self.backpack.get_item_by_number(number)
        elif item_string in ['карту', 'карта', 'картой']:
            item = self.get_map()
        else:
            item = self.backpack.get_first_item_by_name(item_string)
        if item:
            item.use(self, in_action=False)
            return True
        tprint(game, f'{self.name} не {self.g("нашел", "нашла")} такой вещи у себя в рюкзаке.')
        return False
    
    
    def get_map(self) -> Map|None:
        maps = self.backpack.get_items_by_class(Map)
        return next((map for map in maps if map.floor == self.floor), None)
    
    
    def use(self, item:str=None) -> bool:
        """Метод обрабатывает команду "использовать". """
        
        game = self.game
        if not item:
            tprint(game, f'{self.name} не понимает, что {self.g("ему", "ей")} надо использовать.')
            return False
        if self.removed_shield.check_name(item):
            return self.take_out_shield()
        return self.use_item_from_backpack(item)

    
    def check_if_hero_can_enchant(self, item:str) -> bool:
        """Метод проверки, может ли герой что-то улучшать."""
        
        game = self.game
        rune_list = self.backpack.get_items_by_class(Rune)
        if item == '':
            tprint(game, f'{self.name} не понимает, что {self.g("ему", "ей")} надо улучшить.')
            return False
        if self.fear >= Hero._fear_limit:
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
        if item == 'оружие' and not self.weapon.empty:
            return self.weapon
        if item == 'щит':
            if not self.shield.empty:
                return self.shield
            elif not self.removed_shield.empty:
                return self.removed_shield
        if item in ['дооспех', 'доспехи'] and not self.armor.empty:
            return self.armor
        if item.isdigit():
            selected_item = self.backpack.get_item_by_number(int(item))
        else:
            selected_item = self.backpack.get_first_item_by_name(item)
        if isinstance(selected_item, Weapon):
                return selected_item
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
        self.rune_list = self.backpack.get_items_by_class(Rune)
        message = []
        self.selected_item = self.chose_what_to_enchant(item)
        message.append(f'{self.name} может использовать следующие руны:')
        for rune in self.rune_list:
            message.append(f'{str(self.rune_list.index(rune) + 1)}: {str(rune)}')
        message.append('Выберите номер руны или скажите "отмена" для прекращения улучшения')
        self.state = state_enum.ENCHANT
        tprint(game, message, 'enchant')

    
    def check_if_hero_can_read(self) -> bool:
        """Метод проверки, может ли герой сейчас читать."""
        
        game = self.game
        if self.fear >= Hero._fear_limit:
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
        if self.weapon.element() in Rune._glowing_elements:
            return True
        if self.shield.element() in Rune._glowing_elements:
            return True
        if self.armor.element() in Rune._glowing_elements:
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
            message = f'{self.name} читает {book:accus}.'
        if book:
            tprint(game, message)
            return book
        return None 
    
    
    def read(self, what:str) -> bool:
        """Метод обрабатывает команду "читать". """
        
        if not self.check_if_hero_can_read():
            return False
        book = self.get_book(item=what)
        if not book:
            tprint(self.game, 'В рюкзаке нет ни одной книги. Грустно, когда нечего почитать.')
            return False
        message = book.use(self)
        self.backpack.remove(book)           
        tprint(self.game, message)
        self.decrease_restless(2)
        return True
    
    
    def decrease_restless(self, number:int) -> bool:
        """Метод уменьшает значение непоседливости героя. Герой не может отдыхать когда непоседливость больше 0."""
        
        if self.restless >= number:
            self.restless -= number
        return True
