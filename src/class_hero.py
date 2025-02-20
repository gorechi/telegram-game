from src.class_items import Map
from src.class_rune import Rune
from src.class_basic import Money
from src.class_monsters import Monster, Vampire
from src.class_protection import Shield
from src.class_room import Room
from src.class_weapon import Weapon
from src.class_backpack import Backpack
from src.class_fight import Fight
from src.class_dice import Dice
from src.functions.functions import howmany, normal_count, randomitem, tprint, roll, split_actions
from src.controllers.controller_actions import ActionController
from src.enums import state_enum, move_enum

from random import randint


class Hero:
    """Класс героя игры"""
    
    _nightmare_probability = Dice([3])
    """
    Вероятность того, что герой увидит кошмар во время отдыха. 
    Рассчитывается как 1/n, где n - это значение параметра.

    """

    _nightmare_divider = 2
    """Коэффициент, на который делится страх если приснился кошмар."""

    _steal_probability = Dice([2]) 
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
    
    
    def __init__(self, game):
        self.game = game
        self.current_position = None
        self.action_controller = ActionController(game=self.game, hero=self)
        self.poisoned = False
        self.trader = None
        self.weapon = self.game.no_weapon
        self.armor = self.game.no_armor
        self.shield = self.game.no_shield
        self.removed_shield = self.game.no_shield
        self.get_backpack()
        self.money = Money(self.game, 0)
        self.current_fight = None
        self.state = state_enum.NO_STATE
        self.game_is_over = False
        self.can_use_in_fight = []
        self.rune_list = []
        self.restless = 0
        self.wins = 0
        self.hide = False
        self.run = False
        self.exp = 0
        self.fear = 0
        self.drunk = 0
        self.floor = self.game.castle_floors[0]
        self.save_room = self.floor.plan[0]
        self.wounds = {}
        self.last_move = move_enum.DOWN
        self.command_dict = {
            'использовать': self.use,
            'применить': self.use,
            'test': self.test,
            'тест': self.test,
            'обезвредить': self.disarm,
            'торговать': self.trade,
            'улучшить': self.enchant
            }
        self.hero_actions = {
            "отдохнуть": {
                "method": "rest",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 10
                },
            "отдыхать": {
                "method": "rest",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 10
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "name_for_examine",
                "duration": 1
                },
            "лечиться": {
                "method": "heal",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "name_for_examine",
                "duration": 3
                },
            "лечить": {
                "method": "heal",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "name_for_examine",
                "duration": 3
                },
            "вылечиться": {
                "method": "heal",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "name_for_examine",
                "duration": 3
                },
            "вылечить": {
                "method": "heal",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "name_for_examine",
                "duration": 3
                },
            }
        
        
    def heal(self, who, in_action:bool=False) -> str:
        if in_action:
            potion = self.backpack.get_random_item_by_class('HealPotion')
        else:
            potion = self.backpack.get_random_item_by_class('Antidote')
        if not potion:
            return f'{self:nom} не может поправить здоровье так как у {self.g('него','нее')} нет подходящих зелий.'
        return potion.use(self, in_action)
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        names_list = ['себя', 'себе', 'героя', 'героиню']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def name_for_examine(self, who) -> str:
        return f'Себя {self.g('самого', 'саму')}'
    
    
    def examine(self, who, in_action:bool=False) -> list[str]:
        if not self.check_light():
            return 'В комнате совершенно неподходящая обстановка чтобы что-то осматривать. Сперва надо зажечь свет.'
        return self.show(return_message=True)   
    
    
    def on_create(self):
        self.start_stren = self.stren.copy()
        self.start_dext = self.dext.copy()
        self.start_intel = self.intel.copy()
        self.start_rage = self.rage.copy()
        self.start_health = self.health
        self.action_controller.add_actions(self)
        return None
    
    
    def __format__(self, format:str) -> str:
        if format == 'pronoun':
            if self.gender == 0:
                return 'он'
            return 'она'
        return self.lexemes.get(format, '')
         
    
    def __str__(self):
        return f'<Hero: name = {self.name}>'

    
    def get_backpack(self):
        new_backpack = Backpack(self.game)
        self.action_controller.add_actions(new_backpack)
        self.backpack = new_backpack
    
    
    def is_hero(self) -> bool:
        return True
    
    
    def generate_initiative(self) -> int:
        return self.initiative.roll() + self.dext.roll()
        
    
    def test(self, commands:list=None):
        self.game.test(self)
        tprint(self.game, 'Тестирование началось')
        
    
    def check_stren(self, against:int=None, add:list[int]=[], subtract:list[int]=[], multiplier:int=1) -> bool:
        if self.check_light():
            multiplier += self.rage.roll()
        subtract.append(self.wounds.get('stren', 0))
        subtract.append(self.stren.base_die() // 2)
        result = self.stren.roll(
                subtract = subtract,
                multiplier = multiplier,
                add = add
            )
        if against:
            return result > against
        return result
    
    
    def check_dext(self, against:int=None, add:list[int]=[], subtract:list[int]=[], multiplier:int=1) -> bool:
        subtract.append(self.wounds.get('dext', 0))
        result = self.dext.roll(
                subtract = subtract,
                multiplier = multiplier,
                add = add
            )
        if against:
            return result > against
        return result
    
    
    def check_intel(self, against:int=None, add:list[int]=[], subtract:list[int]=[], multiplier:int=1) -> bool:
        subtract.append(self.wounds.get('intel', 0))
        subtract.append(self.rage.base_die() - 1)
        result = self.intel.roll(
                subtract = subtract,
                multiplier = multiplier,
                add = add
            )
        if against:
            return result > against
        return result
    
    
    def check_if_sneak_past_monster(self, monster: Monster) -> bool:
        return self.check_dext(against=monster.size.roll())
    
    
    def place(self, room):
        self.current_position = room
        room.visited = True
        self.last_move = move_enum.START
    
    
    def check_if_sneak_past_furniture(self) -> bool:
        return self.check_dext(against=3, add=[2])
    
    
    def increase_monster_knowledge(self, monster_type) -> bool:
        knowledge = self.monster_knowledge.get(monster_type, 0)
        self.monster_knowledge[monster_type] = knowledge + 1
        return f'{self.name} больше узнает про {Monster._types[monster_type]["accus"]}'
    
    
    # def go_down(self, what:str) -> bool:
    #     if not self.check_light():
    #         return self.go_down_with_light_off()
    #     return self.go_down_with_light_on()
    
    
    def go_down_with_light_off(self) -> str:
        room = self.current_position
        if not room.ladder_down or room.ladder_down.locked:
            return f'{self:nom} шарит в темноте ногой по полу, но не находит, куда можно было бы спуститься.'
        return self.descend(room)


    def descend(self, room) -> bool:
        room_to_go = room.ladder_down.room_down
        self.last_move = move_enum.DOWNSTAIRS
        return self.move(room_to_go)
    
    
    def go_down_with_light_on(self) -> str:
        room = self.current_position
        if not room.ladder_down:
            return f'{self:nom} в недоумении смотрит на абсолютно ровный пол. Как только {self.g("ему", "ей")} могла прийти в голову такая идея?'
        if room.ladder_down.locked:
           return 'Крышка люка в полу не открывается. Похоже, она заперта.'
        return self.descend(room)
    
    
    # def go_up(self, what:str) -> bool:
    #     if not self.check_light():
    #         return self.go_up_with_light_off()
    #     return self.go_up_with_light_on()
    
    
    def go_up_with_light_off(self) -> bool:
        room = self.current_position
        if not room.ladder_up or room.ladder_up.locked:
            return f'{self:nom} ничего не может разглядеть в такой темноте.'
        return self.ascend(room)


    def ascend(self, room):
        room_to_go = room.ladder_up.room_up
        self.last_move = move_enum.UPSTAIRS
        return self.move(room_to_go)
    
    
    def go_up_with_light_on(self) -> bool:
        room = self.current_position
        if not room.ladder_up:
            return f'{self:nom} и {self.g("хотел", "хотела")} бы забраться повыше, но в этой комнате нет такой возможности.'
        if room.ladder_up.locked:
           return f'{self:nom} пытается поднять крышку люка, ведущего наверх, но она не поддается. Похоже, она заперта.'
        return self.ascend(room)

         
    def action(self, command:str, message:str):
        
        """Метод обработки комманд от игрока."""
        # command in self.command_dict.keys() and
        message = message.lower()
        if self.state == state_enum.NO_STATE:
            if not self.game.check_endgame():
                self.do(message)
            return True
        actions = {
            state_enum.ENCHANT: self.rune_actions,
            state_enum.TRADE: self.trade_actions,
            state_enum.USE_IN_FIGHT: self.in_fight_actions,
            state_enum.FIGHT: self.fight_actions,
            state_enum.ACTION: self.free_action
        }
        if command in Hero._level_up_commands and self.state == state_enum.LEVEL_UP:
            self.levelup(command)
            return True
        action = actions.get(self.state, None)
        if action:
            return action(message)
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
        game = self.game
        self.state = state_enum.NO_STATE
        if message == 'отмена':
            tprint(game, f'{self.name} передумывает что-то улучшать и решает просто жить дальше.', 'direction')
            self.state = state_enum.NO_STATE
            return False
        if not message.isdigit():
            tprint(game, f'Чтобы все заработало {self:dat} нужно просто выбрать руну по ее номеру. Проще говоря, просто ткнуть в нее пальцем', 'enchant')
            return False
        message = int(message) - 1
        if not message < len(rune_list):
            tprint(game, f'{self.name} не находит такую руну у себя в рюкзаке.', 'enchant')
            return False
        if not self.selected_item:
            tprint(game, f'{self.name} вертит руну в руках, но не может вспомнить, куда {self.g("он хотел", "она хотела")} ее поместить.', 'direction')
            self.state = state_enum.NO_STATE
            return False
        chosen_rune = rune_list[message]
        rune_is_placed = self.selected_item.enchant(chosen_rune)
        if not rune_is_placed:
            tprint(game, f'Похоже, что {self.name} не может вставить руну в {self.selected_item:accus}.', 'direction')
            self.state = state_enum.NO_STATE
            return False
        tprint(game, f'{self.name} улучшает {self.selected_item:accus} новой руной.', 'direction')
        self.backpack.remove(chosen_rune)
        self.rune_list = self.backpack.get_items_by_class('Rune')
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
            tprint(self.game, f'{self.name} продолжает бой.', 'fight')
            self.state = state_enum.FIGHT
            return False
        if not message.isdigit():
            tprint(self.game, f'Чтобы все заработало {self:dat} нужно просто выбрать вещь по ее номеру. Проще говоря, просто ткнуть в нее пальцем', 'fight')
            return False
        items = self.can_use_in_fight
        message = int(message) - 1
        if not message < len(items):
            tprint(self.game, f'{self.name} не находит такую вещь у себя в карманах.', 'fight')
            return False
        item = items[message]
        item_is_used = item.use(who_using=self, in_action=True)
        if not item_is_used:
            tprint(self.game, f'Похоже, что {self.name} не может использовать {item:accus}.', 'fight')
            self.state = state_enum.FIGHT
            return False    
        self.state = state_enum.FIGHT
        return True
    
    
    def fight_actions(self, message:str) -> bool:
        
        """
        Метод обрабатывает команды игрока когда он дерется с монстром.
                
        """

        fight = self.current_fight
        action, enemy_text = split_actions(message)
        enemy = self.select_enemy(enemy_text)
        message = self.attack(enemy, action)
        fight.continue_after_hero()
        return True
    
    
    def select_enemy(self, enemy_text:str):
        enemies = self.current_fight.get_targets(self)
        if str(enemy_text).isdigit():
            try:
                enemy = enemies[int(enemy_text)-1]
            except Exception:
                tprint(self.game, 'В схватке нет такого врага.')
                return False
            if enemy == self:
                tprint(self.game, 'Герой не может атаковать сам себя.')
                return False
            return enemy
        if not enemy_text:
            return randomitem(enemies)
        for enemy in enemies:
            if enemy.check_name(enemy_text.lower()):
                return enemy
        
    
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
        """
        self.trap_mastery += 1    


    def get_disarm_trap_chance(self) -> int:
        """
        Рассчитывает и возвращает шанс героя на успешное обезвреживание ловушки.
        """
        return self.check_dext(add=[self.trap_mastery])
   
    
    def intel_wound(self) -> str:
        """
        Наносит персонажу ранение, влияющее на интеллект, увеличивая счетчик таких ранений на 1.
        """
        wound = self.wounds.get('intel', 0)
        self.wounds['intel'] = wound + 1
        return f'{self.name} получает удар по голове, что отрицательно сказывается на {self.g("его", "ее")} способности к здравым рассуждениям.'
    
    
    def stren_wound(self) -> str:
        """
        Наносит персонажу ранение, влияющее на силу, увеличивая счетчик таких ранений на 1.
        """
        wound = self.wounds.get('stren', 0)
        self.wounds['stren'] = wound + 1
        return f'{self.name} получает ранение и теряет много крови. Из-за раны {self:pronoun} сильно слабеет.'
    
    
    def dex_wound(self) -> str:
        """
        Наносит персонажу ранение, влияющее на ловкость, увеличивая счетчик таких ранений на 1.
        """
        wound = self.wounds.get('dex', 0)
        self.wounds['dex'] = wound + 1
        return f'{self.name} получает ранение в ногу и теперь двигается как-то неуклюже и гораздо медленнее.'
        
            
    def get_weakness(self, weapon:Weapon) -> float:
        element = str(weapon.element())
        weakness = self.weakness.get(element, None)
        return weakness if weakness else 0
    
    
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
        Метод обрабатывает команды, переданные герою и передает управление соответствующей команде функции.
        """
        parts = command.split(' ', maxsplit=1)
        action, item = parts if len(parts) == 2 else (parts[0], None)
        if action == '?':
            text = []
            text.append(f'{self.name} может:')
            for i in self.command_dict.keys():
                text.append(i)
            tprint(self.game, text)
            return True
        method = self.command_dict.get(action, False)
        if method:
            if not item:
                method()
            else:
                method(item)
            return True
        self.do_from_dictionary(action, item)
    
    
    def check_fight(self) -> bool:
        if self.current_fight:
            return True
        return False
            
        
    def get_items_for_action(self, action:str, item:str=None, in_darkness:bool=False, in_combat:bool=False, bulk:bool=False) -> list:
        hero_items_list = self.action_controller.get_items_by_action_and_name(
            action = action, 
            name = item, 
            in_darkness = in_darkness, 
            in_combat = in_combat
            ) 
        room_items_list = self.current_position.action_controller.get_items_by_action_and_name(
            action = action, 
            name = item, 
            in_darkness = in_darkness, 
            in_combat = in_combat
            )
        return hero_items_list + room_items_list
    
    
    def do_from_dictionary(self, action:str, item:str=None):
        in_darkness = not self.check_light()
        in_combat = self.check_fight()
        items = self.get_items_for_action(action, item, in_darkness, in_combat)
        if not items:
            if in_darkness:
                tprint(self.game, 'В комнате слишком темно чтобы делать что-то такое.') 
            else:
                tprint(self.game, f'{self.name} не видит смысла сейчас делать подобные глупости!')
            return False
        first_item = items[0]
        if len(items) == 1 and (item or first_item.item == self or first_item.item == self.current_position):
            return self.do_single_action(first_item)
        items = self.bulk_actions(items)
        if not items:
            tprint(self.game, 'У героя закончились варианты как сделать что-то подобное.') 
            return True
        message = []
        message.append(f'Действие "{action}" доступно для следующих штук или достопочтенных особ:')
        for item in items:
            if not item.presentation:
                message.append(f'{items.index(item) + 1}: {item.name.capitalize()}')
            else:
                message.append(f'{items.index(item) + 1}: {item.presentation(self)}')
        message.append(f'{self.g('Герой должен', 'Героиня должна')} назвать номер вещи или крикнуть "отмена" во всю силу своих легких, чтобы ничего не делать')
        self.to_do_list = items
        self.state = state_enum.ACTION
        tprint(self.game, message, 'read')
        return True
    
    
    def bulk_actions(self, items:list) -> list:
        items_for_bulk_actions = [item for item in items if item.bulk]
        total_duration = 0
        for item in items_for_bulk_actions:
            tprint(self.game, item.action(self))
            total_duration += item.duration
            items.remove(item)
        self.game.events_controller.execute_all_events(total_duration)
        return items
            

    def free_action(self, message:str):
        if message == 'отмена':
            tprint(self.game, f'{self.name} неожиданно решает, что не хочет ничего делать.', 'direction')
            self.state = state_enum.NO_STATE
            return False
        if not message.isdigit():
            tprint(self.game, f'Чтобы что-то сделать {self:dat} нужно выбрать вещь по ее номеру.', 'read')
            return False
        message = int(message) - 1
        if not message < len(self.to_do_list):
            tprint(self.game, f'У {self:gen} нет столько подходящих вещей.', 'read')
            return False
        item = self.to_do_list[message]
        self.do_single_action(item)
        self.state = state_enum.NO_STATE
        
    
    def do_single_action(self, item) -> bool:
        action = item.action
        tprint(self.game, action(self), 'direction')
        self.decrease_restless(2)
        if item.post_process:
            item.post_process(self)
        self.game.events_controller.execute_all_events(item.duration)
        return True
    
    
    def get_poison_protection(self) -> int:
        protection = self.poison_protection.roll()
        if self.armor.is_poisoned() or self.shield.is_poisoned():
            protection += 2
        return protection
    
        
    def poison_enemy(self, target:Monster) -> str|None:
        """
        Метод проводит проверку, отравил герой противника при атаке, или нет.
        
        Входящие параметры:
        - target - монстр, которого атакует герой

        """
        
        if target.poisoned or target.poison_level.base_die() > 0:
            return None
        self_poison_level = self.poison_level.roll()
        weapon_poison_level = self.weapon.get_poison_level()
        protection = target.get_poison_protection()
        if self_poison_level + weapon_poison_level > protection:
            target.poisoned = True
            return f'{target.name} получает отравление, {target:pronoun} теперь неважно себя чувствует.'
        return None
    
    
    def get_hit_chance(self) -> int:
        """Метод рассчитывает и возвращает значение шанса попадания героем по монстру."""
        
        mastery = self.mastery.get(self.weapon.weapon_type, None)
        mastery_level = mastery['level'] if mastery else 0
        weapon_hit_chance = self.weapon.get_hit_chance()
        return self.check_dext(add=[mastery_level]) + weapon_hit_chance
    
    
    def parry_chance(self) -> int:
        """Метод рассчитывает и возвращает значение шанса парирования атаки."""
        
        mastery = self.mastery.get(self.weapon.weapon_type, None)
        mastery_level = mastery['level'] if mastery else 0
        parry_chance = self.check_dext(add=[mastery_level])
        if self.poisoned:
            parry_chance -= self.dext.base_die() // 2
        return max(parry_chance, 0)
        
    
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
    
    
    def rest(self, who, in_action:bool=False) -> list[str]:
        """
        Метод обрабатывает команду "отдохнуть". 
        """
        room = self.current_position
        rest_not_posible = self.check_rest_possibility(room=room)
        if rest_not_posible:
            return rest_not_posible
        monster_in_ambush = self.check_monster_in_ambush(place=room)
        if monster_in_ambush:
            return monster_in_ambush
        self.poisoned = False
        self.health = self.start_health
        self.save_room = room
        self.restless = 10
        return self.sleep_while_rest()
    
    
    def sleep_while_rest(self) -> list[str]:
        """
        Метод моделирует сон героя во время отдыха.
        """
        message = list()
        dream_count = Hero._nightmare_probability.roll()
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
        return message
        
    
    def get_robbed_while_sleep(self) -> str:
        """
        Метод моделирует то, что героя ограбили во время сна.
        Метод возвращает строку текста, которая добавляется к сообщению о сне.
        """
        steal_count = Hero._steal_probability.roll()
        if steal_count == 1 and not self.backpack.is_empty():
            all_monsters = [monster for monster in self.floor.all_monsters if (not monster.stink and monster.can_steal)]
            stealing_monster = randomitem(all_monsters)
            all_items = self.backpack.get_items_except_class('Key')
            if all_items:
                item = randomitem(all_items)
                item_is_taken = stealing_monster.take(item)
                if item_is_taken:
                    self.backpack.remove(item, stealing_monster)
                    return f'Проснувшись {self.name} лезет в свой рюкзак и обнаруживает, что кто-то украл {item:accus}.'
        return None
    
    
    def check_monster_in_ambush(self, place) -> list[str]:
        """
        Метод проверки, выскочил ли из засады монстр.        
        """    
        monster = place.monster_in_ambush()
        message = list()
        if monster:
            monster.hiding_place = None
            message.append(f'Неожиданно из засады выскакивает {monster.name} и нападает на {self:accus}.')
            if monster.frightening:
                message.append(f'{monster.name} очень {monster.g("страшный", "страшная")} и {self.name} пугается до икоты.')
                self.fear += 1
        return message
    
    
    def check_rest_possibility(self, room:Room) -> list[str]:
        """
        Метод проверки, может ли герой отдыхать в комнате.
        """
        cant_rest, rest_place = room.can_rest()
        message = list()
        if self.restless > 0:
            cant_rest.append(f'У {self.g("героя", "героини")} столько нерастраченной энергии, что {self.g("ему", "ей")} не сидится на месте')
        if not rest_place or len(cant_rest) > 0:
            message.append('В этой комнате нельзя этого делать.')
            message.append(randomitem(cant_rest))
        return message
       
    
    def get_second_weapon(self) -> Weapon:
        """
        Метод ищет в рюкзаке героя оружие. 
        Если оружие найдено, возвращает его. 
        Если оружие не найдено, возвращается объект "Пустое оружие".
        
        """       
        item = self.backpack.get_first_item_by_class('Weapon')
        if item:
            return item
        return self.game.no_weapon

    
    def generate_in_fight_description(self, index:int) -> str:
        line = f'{index}: {self.name}: сила - {self.stren.text()}'
        line += self.generate_weapon_text()
        line += self.generate_protection_text()
        line += f', жизней - {str(self.health)}. '
        return line
    
    
    def generate_weapon_text(self) -> str:
        if not self.weapon.empty:
            return f'{self.weapon.damage.text()}'
        return ''
    
    
    def generate_protection_text(self) -> str:
        if not self.shield.empty and self.armor.empty:
            return f', защита - {self.shield.protection.text()}'
        elif self.shield.empty and not self.armor.empty:
            return f', защита - {self.armor.protection.text()}'
        elif not self.shield.empty and not self.armor.empty:
            return f', защита - {self.armor.protection.text()} + {self.shield.protection.text()}'
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
        a = randint(1, 2)
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
        """        
        room = self.current_position
        available_directions = room.get_available_directions()
        self.rage.reset()
        self.hide = False
        message = [
            self.generate_run_away_text(target=target),
            self.lose_weapon_or_shield(target=target)
        ]
        message += self.lose_random_items()        
        if self.check_light():
            direction = randomitem(available_directions)
        else:
            direction = randint(0, 3)
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
            

    def generate_mele_attack(self) -> int:
        """Метод генерирует значение атаки голыми руками."""
        
        return self.check_stren()
                
    
    def generate_weapon_attack(self, target:Monster) -> int:
        """Метод генерирует значение дополнительной атаки оружием."""
        
        if self.weapon.empty:
            return 0
        if isinstance(target, Vampire) and self.weapon.element() == 4:
            return target.health
        weapon_attack = self.weapon.attack(target)
        mastery = self.mastery[self.weapon.type]['level']
        critical_probability = mastery * Hero._critical_step
        if randint(1, 100) <= critical_probability and not self.poisoned:
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
        mastery = self.mastery['щиты']
        if not shield.empty and shield.check_if_broken(total_attack, mastery):
            return f' {self.name} наносит настолько сокрушительный удар, что ломает щит соперника.'
        return None    
    
        
    def increase_mastery(self) -> str:
        """Метод увеличивает мастерство владения определенным типом оружия по итогу схватки."""
        
        if self.weapon.empty:
            return None
        weapon_type = self.weapon.type
        mastery = self.mastery.get(weapon_type)
        mastery['counter'] += randint(1, 10)/100
        if mastery['counter'] > mastery['level']:
            mastery['counter'] = 0
            mastery['level'] += 1
            return f' {self.g("Герой", "Героиня")} теперь немного лучше знает, как использовать {weapon_type} оружие.'
        return None
       
    
    def hit_enemy(self, target:Monster) -> None:
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
            hit_string = f'{self.name} бьет {target_name_accusative} не используя оружие и наносит {howmany(total_attack, ["единицу", "единицы", "единиц"])} урона. '
        message.append(hit_string)
        total_damage, target_defence = self.generate_total_damage(target=target, total_attack=total_attack)
        if target_defence < 0:
            message.append(f' {target.name} {target.g("смог", "смогла")} увернуться от атаки и не потерять ни одной жизни.')
        elif total_damage == 0:
            message.append(f'{self.name} не {self.g("смог", "смогла")} пробить защиту {target_name_accusative}.')
        elif total_damage > 0:
            damage_string = f'{target_name} не имеет защиты и теряет {howmany(total_damage, ["жизнь", "жизни", "жизней"])}.'
            message += [
                damage_string,
                self.break_enemy_shield(target=target, total_attack=total_attack),
                self.poison_enemy(target=target),
                self.increase_mastery()
            ] 
        target.health -= total_damage
        self.rage.reset()
        tprint(game, message)
        
    
    
    def attack(self, target:Monster, action:str) -> bool:
        """Метод обрабатывает команду "атаковать". """
        
        self.run = False
        if action == '' or action == 'у' or action == 'ударить':
            self.hit_enemy(target=target)
            return
        if action in ['з', 'защититься', 'защита']:
            self.use_shield(target)
            return
        if action in ['б', 'бежать', 'убежать']:
            self.run_away(target)
            return
        if action in ['и', 'использовать']:
            self.use_in_fight()
            return
        if action in ['с', 'сменить оружие', 'сменить']:
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
            tprint(game, f'У {self.g("героя", "героини")} нет щита, так что защищаться {self:pronoun} не может.')
        else:
            self.hide = True
            self.rage.increase_base_die(self.mastery['щиты'] + 1)
            tprint(game, f'{self.name} уходит в глухую защиту, терпит удары и накапливает ярость.')

    
    def show(self, return_message:bool=False):
        """
        Метод генерирует и выводит на экран описание персонажа
        
        """
        message = []
        money_text = self.show_me_money()
        message.append(f'{self.name} - это {self.g("смелый герой", "смелая героиня")} {str(self.level)} уровня. ' 
                       f'{self.g("Его", "Ее")} сила - {self.stren.text()}, ловкость - {self.dext.text()}, интеллект - {self.intel.text()} и сейчас'
                       f' у {self.g("него", "нее")} {howmany(self.health, ["единица", "единицы", "единиц"])} здоровья, что составляет '
                       f'{str(self.health * 100 // self.start_health)} % от максимально возможного. {money_text}')
        message.append(self.show_weapon())
        message.append(self.show_protection())
        message.append(self.show_mastery())
        if return_message:
            return message
        tprint(self.game, message)

    
    def show_mastery(self) -> str:
        """Метод генерирует описание мастерства персонажа."""
        
        mastery_text = ''
        for mastery in self.mastery:
            if self.mastery[mastery]['level'] > 0:
                mastery_text += f' {mastery} ({self.mastery[mastery]["level"]})'
        if mastery_text:
            mastery_text = mastery_text[1::]
            text = f'{self.g("Герой", "Героиня")} обладает знаниями про {normal_count(mastery_text, "(")}.'
            return text
        return ''
    
    
    def show_me_money(self) -> str:
        """Метод генерирует описание денег персонажа."""
        
        if self.money >= 2:
            money_text = f'В кошельке звенят {howmany(self.money.how_much_money, ["монета", "монеты", "монет"])}.'
        elif self.money == 1:
            money_text = 'Одна-единственная монета оттягивает карман героя.'
        else:
            money_text = f'{self.name} {self.g("беден", "бедна")}, как церковная мышь.'
        return money_text
    
    
    def show_weapon(self) -> str:
        """Метод генерирует описание оружия персонажа."""
        
        if not self.weapon.empty:
            weapon_text = f'{self.weapon.get_full_names("nom")} в руке {self.g("героя", "героини")} добавляет к {self.g("его", "ее")} силе ' \
                          f'{self.weapon.damage.text()}.'
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
        parry_chance = self.parry_chance()
        hit_chance = attacker.hit_chance.roll() + weapon.hit_chance.roll()
        if parry_chance > hit_chance:
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
            result += self.armor.protect(attacker, self.mastery['доспехи'])
        if self.try_to_parry(attacker=attacker):
            result = -1
        return result

    
    def reset_dice(self):
        self.stren = self.start_stren.copy()
        self.dext = self.start_dext.copy()
        self.intel = self.start_intel.copy()
        self.rage = self.start_rage.copy()
        self.health = self.start_health
    
    
    def lose(self, fight:Fight) -> list[str]:
        """
        Метод сбрасывает состояние героя при его проигрыше в бою

        Входящие параметры:
        - winner - атакующий монстр (пока не используется).
        
        """
        self.reset_dice()
        self.current_position = self.save_room
        self.restless = 0
        self.last_move = move_enum.START
        return [f'{self.name} терпит сокрушительное поражение. Каким-то чудом {self:gender} приходит в себя на последнем месте отдыха.']
    
    
    def win(self, loser):
        """Метод обрабатыват событие победы в схватке."""
        
        self.reset_dice()
        self.wins += 1
        tprint(self.game, f'{self.name} получает {howmany(loser.exp, ["единицу", "единицы", "единиц"])} опыта!')
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
        actions = {
            'здоровье': self.increase_health,
            'силу': self.increase_strength,
            'ловкость': self.increase_dexterity,
            'интеллект': self.increase_intelligence
        }
        action = actions.get(message, False)
        if not action:
            return False
        action()
        self.state = state_enum.NO_STATE
        return True

    
    def increase_health(self, amount:int=3) -> bool:
        self.health += amount
        self.start_health += amount
        tprint(self.game, f'{self.name} получает {howmany(amount, ['единица', 'единицы', 'единиц'])} здоровья.', 'direction')
        return True
    
    
    def increase_strength(self, amount:int=1) -> bool:
        self.stren.increase_base_die(amount)
        self.start_stren.increase_base_die(amount)
        tprint(self.game, f'{self.name} увеличивает свою силу на {amount}.', 'direction')
    
    
    def increase_dexterity(self, amount:int=1) -> bool:
        self.dext.increase_base_die(amount)
        self.start_dext.increase_base_die(amount)
        tprint(self.game, f'{self.name} увеличивает свою ловкость на {amount}.', 'direction')
    
    
    def increase_intelligence(self, amount:int=1) -> bool:
        self.intel.increase_base_die(amount)
        self.start_intel.increase_base_die(amount)
        tprint(self.game, f'{self.name} увеличивает свой интеллект на {amount}.', 'direction')
    
    
    def detect_trap(self, trap) -> bool:
        """
        Пытается обнаружить ловушку, основываясь на интеллекте героя, его мастерстве обнаружения ловушек и ранениях.
        
        :param trap: Объект ловушки, который необходимо обнаружить.
        :return: Возвращает True, если ловушка обнаружена, иначе False.
        """
        if trap.seen:
            self.current_position.last_seen_trap = trap
            return True
        detection = self.check_intel() + self.trap_mastery
        if detection > trap.difficulty:
            trap.seen = True
            self.current_position.last_seen_trap = trap
        return trap.seen

    
    def check_monster_and_figth(self):
        """
        Метод проверяет, есть ли в комнате монстр, 
         и, если этот монстр агрессивен, начинает схватку.
         
         """
        
        room = self.current_position
        monster = room.monsters('first')
        if monster:
            if monster.aggressive and self.check_light():
                self.fight(monster)
    
    
    def check_disturbed_monsters (self, who) -> None:
        room = self.current_position
        for monster in room.monsters():
            if monster.disturbed:
                self.fight(monster, True)
                return True
        return False
    
    
    def go_with_light_on(self, direction:int) -> bool:
        door = self.current_position.doors[direction]
        if door.empty:
            return f'Там нет двери. {self.name} не может туда пройти!'
        if door.locked:
            return f'Эта дверь заперта. {self.name} не может туда пройти, нужен ключ!'
        new_position = door.get_another_room(self.current_position)
        self.last_move = move_enum.get_move_by_number(direction)
        self.move(new_position)
        return ''
    
    
    def go_with_light_off(self, direction:int) -> str:
        door = self.current_position.doors[direction]
        going_back = self.check_if_going_back(direction)
        if not going_back:
            sneak, sneak_text = self.sneak_through_dark_room()
            if not sneak:
                return sneak_text
        if door.empty or door.locked:
            if self.check_noise():
                self.current_position.noise(3)
            return f'В темноте {self.name} врезается во что-то носом.'
        new_position = door.get_another_room(self.current_position)
        self.last_move = move_enum.get_move_by_number(direction)
        self.move(new_position)
        return ''
    

    def check_noise(self) -> bool:
        if self.weapon.noisy or self.shield.noisy or self.armor.noisy:
            return True
        return False
    
    
    def sneak_through_dark_room(self) -> bool:
        room = self.current_position
        if room.has_a_monster():
            for monster in room.monsters():
                if not self.check_if_sneak_past_monster(monster):
                    monster.disturbed = True
                    return False, f'{self.name} в темноте задевает что-то живое плечом и это что-то нападает.'
        if room.ladder_down:
            stayed = self.try_not_to_fall_down()
            if not stayed:
                self.descend(self.current_position)
                return False, f'{self.name} медленно пробирается через темноту, но в какой-то момент перестает чувствовать пол под ногами и кубарем скатывается по лестнице вниз.'
        if room.has_furniture() and not self.check_if_sneak_past_furniture():
            self.generate_noise(2)
            return False, f'{self.name} в темноте врезается в какую-то мебель. Раздается оглушительный грохот.'
        return True, ''
    
    
    def try_not_to_fall_down(self) -> bool:
        check_target = self.dext.base_die() // 2
        if not self.dext_check(against=check_target):
            return False
        return True
    
    
    def check_if_going_back(self, direction:int) -> bool:
        return direction == self.last_move.countermove
       
    
    def move(self, new_position:Room) -> str:
        self.game.trigger_on_movement()
        self.current_position = new_position
        self.current_position.visited = True
        self.current_position.show(self)
        self.current_position.map()
        self.decrease_restless(1)
        self.check_monster_and_figth()
        return ''
    
    
    def fight(self, enemy=None, enemy_started:bool=False):
        """Метод обрабатывает команду "атаковать". """
        if enemy_started:
            who_started = enemy
        else:
            who_started = self
        monsters_to_fight = [self, enemy]
        new_fight = Fight(
            game=self.game, 
            hero=self, 
            who_started=who_started, 
            fighters=monsters_to_fight
            )
        new_fight.start()
        return True
        

    def put_in_backpack(self, item) -> bool:
        if self.current_position.loot.is_item_in_loot(item):
            self.current_position.loot.remove(item)
        self.backpack.append(item)
        item.owner = self
        self.action_controller.add_actions(item)
        self.current_position.action_controller.delete_actions_by_item(item)
        return True
    
    
    def check_fear(self) -> str|bool:
        """
        Метод проверки того, что герой испытывает страх.
        Если страх выше лимита, то на экран выводится сообщение, что ничего не получилось.
        Если в метод передан print_message=False, то сообщение не выводится.
        
        """
        
        if self.fear >= Hero._fear_limit:
            return f'{self.name} не может ничего сделать из-за того, что руки дрожат от страха.'
        return False
    
    
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
        maps = self.backpack.get_items_by_class('Map')
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
        rune_list = self.backpack.get_items_by_class('Rune')
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
        self.rune_list = self.backpack.get_items_by_class('Rune')
        message = []
        self.selected_item = self.chose_what_to_enchant(item)
        message.append(f'{self.name} может использовать следующие руны:')
        for rune in self.rune_list:
            message.append(f'{str(self.rune_list.index(rune) + 1)}: {str(rune)}')
        message.append('Выберите номер руны или скажите "отмена" для прекращения улучшения')
        self.state = state_enum.ENCHANT
        tprint(game, message, 'enchant')

    
    def check_if_can_read(self) -> bool:
        """Метод проверки, может ли герой сейчас читать."""
        
        if self.fear >= Hero._fear_limit:
            return False, f'{self.name} смотрит на буквы, но от страха они не складываются в слова.'
        if not self.check_light():
            return False, f'{self.name} решает, что читать в такой темноте вредно для зрения.'
        return True, []
    
        
    def check_light(self) -> bool:
        """Метод проверки, есть ли в комнате свет."""
        
        room = self.current_position
        if room.light or room.torch.burning:
            return True
        if self.weapon.element() in Rune._glowing_elements:
            return True
        if self.shield.element() in Rune._glowing_elements:
            return True
        if self.armor.element() in Rune._glowing_elements:
            return True
        return False
    
    
    def decrease_restless(self, number:int) -> bool:
        """Метод уменьшает значение непоседливости героя. Герой не может отдыхать когда непоседливость больше 0."""
        
        if self.restless >= number:
            self.restless -= number
        return True
