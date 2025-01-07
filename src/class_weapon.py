from src.functions.functions import randomitem, tprint
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

    
    def get_names_list(self, cases:list=None) -> list:
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

    
    def take(self, who):
        game = self.game
        message = [f'{who.name} берет {self:accus}.']
        second_weapon = who.get_second_weapon()
        if who.weapon.empty:
            who.weapon = self
            message.append(f'{who.name} теперь использует {self:accus} в качестве оружия.')
            if who.weapon.twohanded and not who.shield.empty:
                shield = who.shield
                who.shield = self.game.no_shield
                who.removed_shield = shield
                message.append(f'Из-за того, что {who.g("герой взял", "героиня взяла")} двуручное оружие, '
                               f'{who.g("ему", "ей")} пришлось убрать {shield.get_full_names("accus")} за спину.')
        else:
            if not second_weapon.empty:
                message.append(f'В рюкзаке для нового оружия нет места, поэтому приходится бросить {who.weapon.name}.')
                who.drop(who.weapon.name)
                who.weapon = self
            else:
                message.append('В рюкзаке находится место для второго оружия. Во время схватки можно "Сменить" оружие.')
                who.backpack.append(self)
        tprint(game, message)

    
    def show(self):
        damage_string = self.damage.text()
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
            who.backpack.append(who.weapon)
            who.weapon = self
            who.backpack.remove(self, who)
            message = [f'{who.name} теперь использует {self:accus} в качестве оружия.']
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
                               f'{who.g("герой", "героиня")} теперь держит во второй руке {shield.get_full_name("accus")}.')
        tprint(game, message)

    
    def place(self, castle, room_to_place = None):
        if room_to_place:
            room = room_to_place
        else:
            room = randomitem(castle.plan)
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
        room.loot.add(self)
