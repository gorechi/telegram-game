from random import randint as dice
from typing import Any, NoReturn

from src.functions.functions import randomitem, tprint, roll, pprint


class Spell:
    def __init__(self, 
                 game, 
                 name='Обычное заклинание', 
                 element='магия', 
                 min_damage=1,
                 max_damage=5, 
                 min_damage_mult=1, 
                 max_damage_mult=1, 
                 actions='кастует'):
        self.game = game
        self.name = name
        self.description = self.name
        self.element = element
        self.min_damage_mult = min_damage_mult
        self.max_damage_mult = max_damage_mult
        self.actions = actions
        self.max_damage = max_damage
        self.min_damage = min_damage
        self.empty = False

    
    def __str__(self):
        return self.name


    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def take(self, who=''):
        if who == '':
            return False
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self.name} себе.')
            
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['заклинание']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def use(self, who_is_using, in_action:bool=False) -> str:
        
        """ 
        Метод использования заклинания. Возвращает строку ответа и ничего не делает 
        так как заклинание использовать нельзя.
        
        """
        
        tprint(
            self.game, f'{who_is_using.name} не знает, как использовать такие штуки.')



class Matches:
    
    """ Класс Спички. """
    
    _max_quantity = (10,)
    """Кубик, который нужно кинуть чтобы определить, сколько спичек в коробке"""
    
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'спички'
        self.lexemes = {
            "nom": "спички",
            "accus": "спички",
            "gen": "спичек",
            "dat": "спичкам",
            "prep": "спичках",
            "inst": "спичками"
        }
        self.description = 'Спички, которыми можно что-то поджечь'
        self.room = None
        self.empty = False
        self.quantity = self.get_quantity()


    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
        
 
    def check_name(self, message:str) -> bool:
        return message.lower() in ['спички', 'коробок']
    
    
    def get_quantity(self) -> int:
        return roll(Matches._max_quantity)

    
    def get_quantity_text(self, quantity:int) -> str:
        quantity_text = {
            quantity == 1: 'Коробок со всего одной спичкой',
            quantity == 2: 'Коробок, в котором болтается пара спичек',
            quantity > 2 and quantity <= 5: 'Коробок, в котором есть немного спичек',
            quantity > 5 and quantity <= 9: 'Коробок, в котором много спичек',
            quantity > 9: 'Полный спичек коробок',
        }
        return quantity_text[True]
    
    
    def __add__(self, other) -> bool:
        if not isinstance(other, Matches):
            return False
        self.quantity += other.quantity
        return True   
    
    
    def __str__(self) -> str:
        return f'Коробок спичек, {self.quantity}'    
    
    
    def show(self) -> str:
        
        """ Метод возвращает описание спичек в виде строки. """
        
        return self.get_quantity_text(self.quantity)

    
    def place(self, castle, room=None) -> bool:
        
        """ Метод раскидывания спичек по замку. """
        
        if not room:
            rooms = [i for i in castle.plan if not i.locked and i.light]
            room = randomitem(rooms)
        if room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
        self.room = room
        return True

    
    def take(self, who=None) -> bool:
        
        """ Метод вызывается когда кто-то забирает спички себе. """
        
        if not who:
            return False
        if not who.backpack.no_backpack:
            matches_in_backpack = who.backpack.get_first_item_by_class(Matches)
            if matches_in_backpack:
                matches_in_backpack + self
            else:
                who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')
            return True
        return False

    
    def use(self, who_is_using=None, in_action=False) -> bool:
        
        """ Метод использования спичек. """
        
        if not who_is_using:
            who_is_using = self.game.player
        room = who_is_using.current_position
        if room.light:
            tprint(self.game, 'Незачем тратить спички, здесь и так светло.')
            return False
        if who_is_using.check_fear(print_message=False) and roll([2]) == 1:
            tprint(self.game, f'От страха пальцы {who_is_using.g("героя", "героини")} не слушаются. Спичка ломается и падает на пол.')    
        else:
            room.turn_on_light(who_is_using)
        self.quantity -= 1
        self.check_if_empty(who_is_using)
        return True
    
    
    def check_if_empty(self, who) -> bool:
        if self.quantity <= 0:
            who.backpack.remove(self)
            return True
        return False
  

class Map:

    _width_coefficient = 72
    """Коэффициент для расчета ширины карты."""
    
    _height_coefficient = 90
    """Коэффициент для расчета высоты карты."""

    def __init__(self, game, floor):
        self.game = game
        self.floor = floor
        self.can_use_in_fight = False
        self.name = 'карта'
        self.lexemes = {
            "nom": "карта",
            "accus": "карту",
            "gen": "карты",
            "dat": "карте",
            "prep": "карте",
            "inst": "картой"
        }
        self.empty = False
        self.decorate()
    

    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def decorate(self) -> None:
        self.description = f'Карта, показывающая расположение комнат {self.floor.floor_number} этажа замка'
        for lexeme in self.lexemes:
            self.lexemes[lexeme] += f' {self.floor.floor_number} этажа'
    
    
    def check_name(self, message:str) -> bool:
        return message.lower() in ['карта', 'карту']
    
    
    def place(self, room=None) -> bool:
        
        """ Метод размещения карты в замке. """
        
        if not room:
            rooms = self.floor.plan
            room = randomitem(rooms)
        if room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    
    def show(self) -> str:
        
        """ Метод возвращает описание карты в виде строки. """
        
        return self.description

    
    def use(self, who, in_action: bool = False) -> bool:
        """
        Метод использования карты. Если вызывается в бою, то ничего не происходит. 
        В мирное время выводит на экран карту замка.

        Параметры:
        - who - герой, который использует карту
        - in_action - признак того, что предмет используется в бою. По умолчанию False.

        """
        game = self.game
        read_map, map_text = who.generate_map_text(in_action)
        tprint(game, map_text, 'direction')
        if read_map:    
            self.show_map()
            return True
        return False

    
    def show_map(self):
        
        """
        Функция генерирует и выводит в чат карту этажа замка.
        
        """
        
        rows = self.floor.rows
        rooms = self.floor.rooms
        game = self.game
        text = []
        text.append('======' * rooms + '=')
        for i in range(rows):
            text.append('║' + '     ║' * rooms)
            line1 = '║'
            line2 = ''
            for j in range(rooms):
                room = self.plan[i*rooms+j]
                symbol = room.get_symbol_for_map()
                line1 += f'  {symbol}  {room.doors[1]:vertical}'
                line2 += f'==={room.doors[2]:horizontal}=='
            text.append(line1)
            text.append('║' + '     ║' * rooms)
            text.append(line2 + '=')
        pprint(game, text, rooms*Map._width_coefficient, rows*Map._height_coefficient)

    
    def take(self, who) -> NoReturn:
        
        """ Метод вызывается когда кто-то забирает карту себе. """
        
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')


class Key:
    
    def __init__(self, game):
        self.game = game
        self.can_use_in_fight = False
        self.name = 'ключ'
        self.lexemes = {
            "nom": "ключ",
            "accus": "ключ",
            "gen": "ключа",
            "dat": "ключу",
            "prep": "ключе",
            "inst": "ключом"
        }
        self.description = 'Ключ, пригодный для дверей и сундуков'
        self.empty = False


    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def check_name(self, message:str) -> bool:
        return message.lower() in ['ключ']
    
    
    def __str__(self) -> str:
        return self.description

    
    def show(self):
        return self.description

    
    def on_create(self):
        return True

    
    def place(self, floor, room=None) -> bool:
        if not room:
            room = floor.get_random_unlocked_room()
        furniture = room.get_random_unlocked_furniture()
        if furniture:
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    
    def take(self, who):
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self.name} себе.')
            return True
        return False
    
    
    def use(self, who_is_using, in_action:bool=False) -> str:
        
        """ 
        Метод использования ключа. 
        
        """
        
        tprint(
            self.game, f'{who_is_using.name} не знает, как можно использовать ключ если не открывать им что-то.')
