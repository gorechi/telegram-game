
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
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
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
        self.hero_actions = {
            "осмотреть": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 1
                },
            "пересчитать": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 1
                },
            "посчитать": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 1
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
            }
        self.room_actions = {
            "взять": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "брать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "собрать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                }
        }


    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
        
 
    def check_name(self, message:str) -> bool:
        return message.lower() in ['спички', 'коробок']
    
    
    def get_quantity(self) -> int:
        return roll(Matches._max_quantity)

    
    def get_quantity_text(self, quantity:int) -> str:
        quantity_text = {
            quantity == 0: 'Пустой спичечный коробок',
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

    
    def take(self, who=None) -> str:
        
        """ Метод вызывается когда кто-то забирает спички себе. """
        
        if not who:
            return False
        if not who.backpack.no_backpack:
            matches_in_backpack = who.backpack.get_first_item_by_class('Matches')
            if matches_in_backpack:
                matches_in_backpack + self
            else:
                who.put_in_backpack(self)
            return f'{who.name} забирает {self:accus} себе.'
        return f'{who.name} не может забрать спички себе - {who.g("ему", "ей")} некуда их положить.'

    
    def use(self, who_is_using=None, in_action=False) -> str|list[str]:
        
        """ Метод использования спичек. """
        
        if not who_is_using:
            who_is_using = self.game.player
        room = who_is_using.current_position
        if room.light:
            return 'Незачем тратить спички, здесь и так светло.'
        if who_is_using.check_fear(print_message=False) and roll([2]) == 1:
            return f'От страха пальцы {who_is_using.g("героя", "героини")} не слушаются. Спичка ломается и падает на пол.'  
        message = room.turn_on_light(who_is_using)
        self.quantity -= 1
        message.append(self.check_if_empty(who_is_using))
        return message
    
    
    def check_if_empty(self, who) -> str:
        if self.quantity <= 0:
            who.backpack.remove(self)
            return f'{who.g("Герой", "Героиня")} зашвыривает пустую коробочку от спичек в угол комнаты.'
        return f'{who.g("Герой", "Героиня")} бержно убирает оставшиеся спички в рюкзак'
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        names_list = ['спички', 'спичку', 'спичка']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания спичек.
        """
        room = who.current_position
        room.loot.add(self)
        who.backpack.remove(item=self, place=room)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} бросает спички на пол.'
    
    
    def use_one(self):
        if self.quantity > 0:
            self.quantity -= 1

  
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
        self.hero_actions = {
            "смотреть": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 2
                },
            "использовать": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 2
                },
            "прочитать": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 2
                },
            "читать": {
                "method": "show",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 2
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
            }
        self.room_actions = {
            "взять": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "брать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "собрать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                }
        }
    

    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def decorate(self) -> None:
        self.description = f'Карта, показывающая расположение комнат {self.floor.floor_number} этажа замка'
        for lexeme in self.lexemes:
            self.lexemes[lexeme] += f' {self.floor.floor_number} этажа'
    
    
    def check_name(self, message:str) -> bool:
        return message.lower() in ['карта', 'карту', 'карты']
    
    
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
        read_map, map_text = who.generate_map_text(who, in_action)
        if read_map:    
            self.show_map()
        return map_text

    
    def generate_map_text(self, who, in_action: bool = False) -> list[bool, str]:
        if not in_action:
            if not who.check_fear:
                return False, f'{who.name} от страха не может сосредоточиться и что-то разобрать на карте.'
            elif not who.current_position.light:
                return False, 'В комнате слишком темно чтобы разглядывать карту'
            else:
                return True, f'{who.name} смотрит на карту этажа замка.'
        else:
            return False, 'Во время боя это совершенно неуместно!'


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

    
    def take(self, who) -> str:
        
        """ 
        Метод вызывается когда кто-то забирает карту себе. 
        """
        if not who.backpack.no_backpack:
            who.put_in_backpack(self)
            return f'{who.name} забирает {self:accus} себе.'
        return f'{who.name} не может забрать {self:accus} - {who.g("ему", "ей")} некуда ее положить.'
            
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        names_list = []
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания карты.
        """
        room = who.current_position
        room.loot.add(self)
        who.backpack.remove(item=self, place=room)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} неосмотрительно оставляет карту лежать в пыли.'


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
        self.hero_actions = {
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
        }
        self.room_actions = {
            "взять": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "брать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "собрать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                }
        }


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
            who.put_in_backpack(self)
            return f'{who.name} забирает {self.name} себе.'
        return f'{who.name} не может забрать {self:accus} - {who.g("ему", "ей")} некуда ее положить.'
            
        
    def get_names_list(self, cases:list=None, room=None) -> list:
        names_list = []
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list


    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания ключа.
        """
        room = who.current_position
        room.loot.add(self)
        who.backpack.remove(item=self, place=room)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        return f'Непонятно зачем, но {who.name} бросает ключ в угол комнаты.'
