from src.functions.functions import randomitem
from src.class_dice import Dice


class Weapon:
    
    _elements_dictionary = {1: 'огня',
                        2: 'пламени',
                        3: 'воздуха',
                        4: 'света',
                        6: 'ветра',
                        7: 'земли',
                        8: 'лавы',
                        10: 'пыли',
                        12: 'воды',
                        13: 'пара',
                        14: 'камня',
                        15: 'дождя',
                        19: 'грязи',
                        24: 'потопа'}
    """Словарь стихий."""
    
    _poison_level = Dice([10])
    """Кубик, который кидается при проверке отравления оружием."""
    
       
    def __init__(self, game):
        self.game = game
        self.runes = []
        self.empty = False
        self.hero_actions = {
            "использовать": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 0
                },
            "экипировать": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 0
                },
            "выбрать": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 0
                },
            "бросить": {
                "method": "drop",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 0
                },
            "выбросить": {
                "method": "drop",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 0
                },
            "оставить": {
                "method": "drop",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 0
                },
            "сменить": {
                "method": "change",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "name_for_change",
                "duration": 0
                },
            "поменять": {
                "method": "change",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "name_for_change",
                "duration": 0
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "show_for_examine_hero",
                "duration": 1
                },
            }
        self.room_actions = {
            "взять": {
                "method": "take",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "брать": {
                "method": "take",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "собрать": {
                "method": "take",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "show_for_examine_room",
                "duration": 1
                },
        }

    
    def examine(self, who, in_action:bool=False) -> str:
        return self.show()
    
    
    def show_for_examine_hero(self, who) -> str:
        return f'{self.name} (в руках у героя)'
    
    
    def show_for_examine_room(self, who) -> str:
        return f'{self.name} (лежит в комнате)'
    
    
    def name_for_change(self, who) -> str:
        second_weapon = who.get_second_weapon()
        if not second_weapon.empty:
            return f'{self.show()} (меняется на {second_weapon.show()})'
        return self.show()
    
    
    def can_be_changed(self, who) -> bool:
        second_weapon = who.get_second_weapon()
        if who.weapon == self and not second_weapon.empty:
            return True
        return False
    
    
    def change(self, who, in_action:bool=False) -> list[str]:
        """
        Метод смены оружия.
        """
        message = []
        second_weapon = who.get_second_weapon()
        if not self.weapon.empty and second_weapon.empty:
            return f'{who.name} не может сменить оружие из-за того, что оно у {who.g("него", "нее")} одно.'
        message.append(f'{who.name} убирает {self:accus} в рюкзак и берет в руки {second_weapon:accus}.')
        if second_weapon.twohanded and not who.shield.empty:
            who.removed_shield = who.shield
            who.shield = who.game.no_shield
            message.append(f'Из-за того, что {second_weapon:nom} - двуручное оружие, щит тоже приходится убрать.')
        elif not second_weapon.twohanded and not who.removed_shield.empty:
            message.append(f'У {who.g("героя", "героини")} теперь одноручное оружие, поэтому {who:pronoun} может достать щит из-за спины.')
        who.backpack.remove(second_weapon, who)
        self.place_into_backpack(who)
        who.weapon = second_weapon
        return message
    
    
    def place_into_backpack(self, who):
        who.backpack.append(self)
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
    def on_create(self) -> bool:
        return True

    
    def get_hit_chance(self) -> int:
        return self.hit_chance.roll()
    
    
    def __str__(self) -> str:
        return f'{self.name}{self.enchantment()} ({self.damage.text()})'
    
    
    def get_full_names(self, key:str=None) -> str|list:
        if self.element() != 0:
            return self.get_element_names(key)
        if key:
            return self.lexemes.get(key, '')
        return self.lexemes
    
    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания оружия.
        """
        room = who.current_position
        room.loot.add(self)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        who.weapon = self.game.no_weapon
        return f'{who.name} бросает {self.name} в угол комнаты.'
    
    
    def get_element_decorator(self) -> str|None:
        return Weapon._elements_dictionary.get(self.element(), None)
        
        
    def get_element_names(self, key:str=None) -> str|dict|None:
        names = {}
        element_decorator = self.get_element_decorator()
        if not element_decorator:
            return None
        for lexeme in self.lexemes:
            names[lexeme] = f'{self.lexemes[lexeme]} {element_decorator}'
        if key:
            return names.get(key, '')
        return names
    
    
    def check_name(self, message:str) -> bool:
        if self.empty:
            return False
        names_list = self.get_names_list(['nom', "accus"])
        return bool([name for name in names_list if message.lower() in name.lower()])

    
    def get_names_list(self, cases:list=None, room=None) -> list:
        names_list = ['оружие']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
            element_name = self.get_element_names(case)
            if element_name:
                names_list.append(element_name.lower())
        return names_list
    
    
    def element(self):
        element_sum = 0
        for rune in self.runes:
            element_sum += rune.element
        return element_sum

    
    def get_poison_level(self):
        poison_level = 0
        for rune in self.runes:
            if rune.poison:
                poison_level += 1
        return poison_level
    
    
    def can_be_enchanted(self) -> bool:
        if len(self.runes) > 1 or self.empty or not self.enchatable:
            return False
        return True
    
    
    def enchant(self, rune):
        if self.can_be_enchanted():
            self.runes.append(rune)
            self.damage.increase_modifier(rune.damage)
            return True
        return False
    

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
            return ' ' + Weapon._elements_dictionary[element]

    
    def attack(self, who=None):
        """Функция рассчитывает урон, который наносит оружие конкретному монстру

        Args:
            who (object Monster, optional): Монстр, которого атакуют оружием. Defaults to None.

        Returns:
            integer: Значение нанесенного урона
        """
        target_weakness = who.get_weakness(self)
        if target_weakness < 0:
            return self.damage.roll(subtract=[target_weakness*-1])
        elif target_weakness > 0: 
            return self.damage.roll(add=[target_weakness])
        return self.damage.roll()

    
    def take(self, who, in_action=False) -> list[str]:
        message = [f'{who.name} берет {self:accus}.']
        second_weapon = who.get_second_weapon()
        if who.weapon.empty:
            who.weapon = self
            message.append(f'{who.name} теперь использует {self:accus} в качестве оружия.')
            if who.weapon.twohanded and not who.shield.empty:
                who.shield.take_away(who)
                message.append(f'Из-за того, что {who.g("герой взял", "героиня взяла")} двуручное оружие, '
                               f'{who.g("ему", "ей")} пришлось убрать {who.removed_shield.get_full_names("accus")} за спину.')
        else:
            if not second_weapon.empty:
                message.append(f'В рюкзаке для нового оружия нет места, поэтому приходится бросить {who.weapon.name}.')
                who.weapon.drop(who)
                who.weapon = self
            else:
                message.append('В рюкзаке находится место для второго оружия. Во время схватки можно "Сменить" оружие.')
                self.place_into_backpack(who)
        who.action_controller.add_actions(self)
        who.current_position.action_controller.delete_actions_by_item(self)
        return message

    
    def show(self):
        damage_string = self.damage.text()
        if self.twohanded:
            name = self.twohanded_dict[self.gender] + ' ' + self.name + self.enchantment()
        else:
            name = self.name + self.enchantment()
        return f'{name} ({damage_string}), {self.type}'.capitalize()

    
    def use(self, who, in_action=False) -> list[str]:
        if not who.weapon.empty:
            if who.weapon == self:
                return [f'{who.name} уже использует {self:accus} в качестве оружия.']
            who.backpack.append(who.weapon)
            who.backpack.remove(self, who)
        who.weapon = self
        message = [f'{who.name} теперь использует {self:accus} в качестве оружия.']
        if not who.shield.empty and self.twohanded:
            shield = who.shield
            who.removed_shield = shield
            who.shield = self.game.no_shield
            message.append('Из-за того, что новое оружие двуручное, щит пришлось убрать за спину.')
        if not who.removed_shield.empty and not self.twohanded:
            shield = who.removed_shield
            who.shield = shield
            who.removed_shield = self.game.no_shield
            message.append(f'Из-за того, что новое оружие одноручное, {who.g("герой", "героиня")} теперь держит во второй руке {shield.get_full_name("accus")}.')
        return message

    
    def place(self, floor, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(floor.plan)
        monster = room.monsters('random')
        if monster:
            if monster.carry_weapon:
                monster.take(self)
                return True
        elif len(room.furniture) > 0:
            furniture = randomitem(room.furniture)
            if furniture.can_contain_weapon:
                furniture.put(self)
                return True
        room.action_controller.add_actions(self)
        room.loot.add(self)
        

class Torch(Weapon):
    
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "поджечь": {
                "method": "fire",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "show_for_examine_hero",
                "condition": "is_not_burning",
                "duration": 1
                },
            "зажечь": {
                "method": "fire",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "show_for_examine_hero",
                "condition": "is_not_burning",
                "duration": 1
                },
            "потушить": {
                "method": "extinguish",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "show_for_examine_hero",
                "condition": "is_burning",
                "duration": 1
                },
        }
        self.room_actions |= {
            "поджечь": {
                "method": "fire_in_room",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "show_for_examine_room",
                "condition": "is_not_burning",
                "duration": 1
                },
            "зажечь": {
                "method": "fire_in_room",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "show_for_examine_room",
                "condition": "is_not_burning",
                "duration": 1
                },
            "потушить": {
                "method": "extinguish_in_room",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "presentation": "show_for_examine_room",
                "condition": "is_burning",
                "duration": 1
                },
        }
        self.burning = False


    def extinguish(self, who, in_action:bool=False) -> str:
        self.burning = False
        if who.check_light():
            return f'{who.name} тушит факел, который держит руке.'
        return f'{who.name} тушит факел, который держит руке. Комната погружается во тьму.'
    
    
    def extinguish_in_room(self, who, in_action:bool=False) -> str:
        self.burning = False
        if who.check_light():
            return f'{who.name} тушит факел, который освещает комнату.'
        return f'{who.name} тушит факел, который освещает комнату. Комната погружается во тьму'
    
    
    def fire(self, who, in_action:bool=False) -> str:
        matches_in_backpack = who.backpack.get_first_item_by_class('Matches')
        if matches_in_backpack and matches_in_backpack.quantity > 0:
            matches_in_backpack.use_one()
            self.burning = True
            return f'{who.name} поджигает {self:nom} спичками.'
        return f'{who.name} не может поджечь {self:nom}, так как у него нет спичек.'
    
    
    def fire_in_room(self, who, in_action:bool=False) -> str:
        matches_in_backpack = who.backpack.get_first_item_by_class('Matches')
        if matches_in_backpack and matches_in_backpack.quantity > 0:
            matches_in_backpack.use_one()
            self.burning = True
            who.current_position.light = True
            return f'{who.name} поджигает {self:nom} спичками и комната озаряется светом.'
        return f'{who.name} не может поджечь {self:nom}, так как у него нет спичек.'            
    
    
    def is_not_burning(self, room=None) -> bool:
        return not self.burning
    
    
    def is_burning(self, room=None) -> bool:
        return self.burning
    
    
    def place_into_backpack(self, who):
        who.backpack.append(self)
        self.burning = False
        

    def show_for_examine_hero(self, who) -> str:
        if self.burning:
            return f'горящий {self:nom} в руках у {who:gen}'
        return f'потухший {self:nom}, принадлежащий {who:dat}'
    
    
    def show_for_examine_room(self, who) -> str:
        if self.burning:
            return f'горящий {self:nom}, находящийся в комнате'
        return f'потухший {self:nom}, находящийся в комнате'
    
    
    def light(self):
        self.burning = True
        
    
    def element(self):
        if self.burning:
            return 2
        return 0
    
    
    def show(self):
        damage_string = self.damage.text()
        if self.burning:
            name = 'Горящий факел'
        else:
            name = 'Потухший факел'
        return f'{name} ({damage_string}), {self.type}'.capitalize()
    
    
    def place(self, floor, room_to_place = None) -> bool:
        if room_to_place:
            room = room_to_place
        else:
            rooms_without_torches = [room for room in floor.plan if not room.torch]
            room = randomitem(rooms_without_torches)
        if not room:
            return False
        room.torch = self
        room.light = True
        room.action_controller.add_actions(self)
        return True
