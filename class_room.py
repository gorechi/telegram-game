from random import randint as dice
from typing import NoReturn

from class_basic import Loot, Money
from class_items import Key
from functions import pprint, randomitem, readfile, tprint, roll
from typing import Optional


class Ladder:
    
    _lexemes:dict = {
            "nom": "лестница",
            "accus": "лестницу",
            "gen": "лестницы",
            "dat": "лестнице",
            "prep": "лестнице",
            "inst": "лестницой"
        }
    
    _first_decorators:tuple[dict[str, str]] = (
        {
            "nom": "крутая",
            "accus": "крутую",
            "gen": "крутой",
            "dat": "крутой",
            "prep": "крутой",
            "inst": "крутой"
        },
        {
            "nom": "грязная",
            "accus": "грязную",
            "gen": "грязной",
            "dat": "грязной",
            "prep": "грязной",
            "inst": "грязной"
        }
    )
    
    _second_decorators:tuple[dict[str, str]] = (
        {
            "nom": "каменная",
            "accus": "каменную",
            "gen": "каменной",
            "dat": "каменной",
            "prep": "каменной",
            "inst": "каменной"
        },
        {
            "nom": "деревянная",
            "accus": "деревянную",
            "gen": "деревянной",
            "dat": "деревянной",
            "prep": "деревянной",
            "inst": "деревянной"
        }
    )
    
    def __init__(self, room_down:'Room', room_up:Optional['Room']=None, locked:bool=False):
        self.room_up = room_up
        self.room_down = room_down
        self.locked = locked
        self.decorate()
        self.place()
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def place(self) -> bool:
        if not isinstance(self.room_down, Room):
            raise TypeError(f'К лестнице привязан неправильный объект {self.room_down.__class__.__name__} в качестве нижней комнаты.')
        self.room_down.ladder_up = self
        if not isinstance(self.room_up, Room):
            self.room_up = self.get_random_room_up()
        self.room_up.ladder_down = self
        return True
    
    
    def decorate(self) -> None:
        self.lexemes = {}
        first_words = randomitem(Ladder._first_decorators)
        second_words = randomitem(Ladder._second_decorators)
        for key in Ladder._lexemes:
            description = f'{first_words[key]} {second_words[key]} {Ladder._lexemes[key]}'
            self.lexemes[key] = description

    
    def show_in_room_as_ladder_down(self) -> str:
        if self.locked:
            return f'В полу имеется квадратный люк, плотно закрытый крышкой.'
        return f'{self:nom} спускается вниз в темноту.'.capitalize()
        

    def show_in_room_as_ladder_up(self) -> str:
        if self.locked:
            return f'{self:nom} поднимается к люку в потолке, закрытому тяжелой крышкой.'.capitalize()
        return f'{self:nom} ведет куда-то вверх.'.capitalize()


class Door:
    """Класс дверей."""
    
    
    def __init__(self, game):
        self.empty = True
        self.game = game
    
    
    def __bool__(self):
        return not self.empty
    
    
    def __format__(self, format_string:str):
        if format_string == 'horizontal':
            if self.empty:
                return '='
            elif self.locked:
                return '-'
            else:
                return ' '
        if format_string == 'vertical':
            if self.empty:
                return '║'
            elif self.locked:
                return '|'
            else:
                return ' '

    
    def activate(self):
        self.empty = False
        self.locked = False
        self.closed = True
        

class Furniture:
    """Класс мебели."""
    
    _basic_lexemes = {
        "полка": ['полка', 'полку'],
        "шкаф": ['шкаф'],
        "сундук": ['сундук'],
        "очаг": ['очаг']
    }
    
    _locked_possibility = 4
    """Вероятность того, что мебель будет заперта (если 4, то 1/4)."""

    _initial_money_maximum = 50
    """Верхний лимит денег в мебели при генерации."""

    
    def __init__(self, game, name:str='', furniture_type:int=0, can_rest:bool=False):
        """
        Инициализирует объект класса мебели

        Args:
            game: ссылка на объект игры
            name: название объекта мебели
            furniture_type: тип мебели (константы FURNITURE_*)
            can_rest: можно ли отдыхать на этой мебели

        """

        self.game = game
        self.loot:Loot = Loot(self.game)
        self.locked:bool = False
        self.lockable:bool = False
        self.opened:bool = True
        self.trap:Trap = Trap(self.game, self)
        self.can_contain_trap:bool = True
        self.can_contain_weapon:bool = True
        self.can_hide:bool = False
        self.can_rest:bool = can_rest
        self.name:str = name
        self.empty:bool = False
        self.empty_text:str = 'пусто'
        self.state:str = 'стоит'
        self.where:str = 'в углу'
        self.room:'Room' = None
        self.type:int = furniture_type

    
    def __str__(self):
        return self.where + ' ' + self.state + ' ' + self.name
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
    def on_create(self):
        self.state = randomitem(self.states)
        self.where = randomitem(self.wheres)
        return True

    
    def put(self, item):
        self.loot.pile.append(item)
    
    
    def check_trap(self) -> bool:
        if self.trap.activated:
            return True
        return False
   
    
    def monster_in_ambush(self):
        monsters = self.room.monsters()
        if monsters:
            for monster in monsters:
                if monster.hiding_place == self:
                    return monster 
        return False
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = Furniture._basic_lexemes[self.name]
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list


    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def show(self):
        message = []
        message.append(self.where + ' ' + self.state + ' ' + self.name + '.')
        if self.monster_in_ambush():
            message.append('Внутри слышится какая-то возня.')
        return message

    
    def place(self, castle=None, room_to_place=None):
        if room_to_place:
            if self.type not in room_to_place.furniture_types():
                room_to_place.furniture.append(self)
                self.room = room_to_place
            else:
                return False
        else:
            can_place = False
            while not can_place:
                room = randomitem(castle.plan)
                if self.type not in room.furniture_types():
                    can_place = True
            room.furniture.append(self)
            self.room = room
        if dice(1, Furniture._locked_possibility) == 1 and self.lockable:
            self.locked = True
            very_new_key = Key(self.game)
            very_new_key.place(castle)
        if dice(1, 100) <= 50:
            new_money = Money(self.game, dice(1, Furniture._initial_money_maximum))
            self.loot.pile.append(new_money)
        return True


class Room:
    """Класс комнат."""
    
    decor1 = readfile('decorate1', False)
    decor2 = readfile('decorate2', False)
    decor3 = readfile('decorate3', False)
    decor4 = readfile('decorate4', False)
    
    _torch_die = 5
    """
    Кубик, который кидается чтобы определить, горит в комнате факел, или нет 
    (берется выпадение одного конкретного значения).

    """
    
    _stink_levels = {1: 'Немного', 2: 'Сильно', 3: 'Невыносимо'}
    """Уровни вони."""
    
    _secrets = ('унитаз',
                'аквариум',
                'бак',
                'камин',
                'хлам')
    """
    Словарь секретных мест, которые могут встречаться в комнатах.
    Если в тексте описания комнаты есть эти слова, 
    то в ней может быть серкретный клад, который можно найти обыскав эти предметы.

    """
    

    _plan_picture_width = 100
    """Ширина картинки плана комнаты."""

    _plan_picture_height = 120
    """Высота картинки плана комнаты."""

    
    def __init__(self, game, floor, doors):
        self.game = game
        self.floor = floor
        self.doors = doors
        self.money:int = 0
        self.loot:Loot = Loot(self.game)
        self.secret_loot:Loot = Loot(self.game)
        self.locked:bool = False
        self.position:int = -1
        self.visited:bool = False
        self.rune_place = self.game.empty_thing
        self.light:bool = True
        self.trader = None
        self.morgue:list = []
        self.furniture:list = []
        self.stink:int = 0
        self.ledder_up:Ladder = self.game.empty_thing
        self.ledder_down:Ladder = self.game.empty_thing
        self.last_seen_trap:Trap = None
        self.torch = self.set_torch()
        self.secret_word = self.get_secret_word()
        self.decorate()

    
    def get_symbol_for_map(self) -> str:
        """
        Определяет символ для отображения комнаты на карте.

        Возвращает символ, представляющий комнату в зависимости от её состояния:
        - ' ' (пробел), если комната не была посещена;
        - Первую букву имени игрока, если игрок находится в данной комнате;
        - '₽', если в комнате есть торговец;
        - '◊', если в комнате можно отдохнуть;
        - '+', во всех остальных случаях.

        Returns:
            str: Символ, представляющий комнату на карте.
        """
        game = self.game
        cant_rest, rest_place = self.can_rest()
        if not self.visited:
            return ' '
        if game.player.current_position == self:    
            return game.player.name[0]
        if self.trader:
            return '₽'
        if rest_place:
            return '◊'
        return '+'
    
    
    def set_torch(self):
        if not self.light or roll([Room._torch_die]) != Room._torch_die:
            return False
        return True

    
    def has_a_corpse(self) -> bool:
        """
        Проверяет, есть ли в комнате труп.

        Возвращает:
            bool: True, если в комнате есть труп, иначе False.
        """
        if len(self.morgue) > 0:
            return True
        return False

    
    def show_corpses(self) -> list:
        """
        Возвращает список описаний трупов в комнате.

        Возвращает:
            list: Список строк, каждая из которых представляет описание трупа в комнате.
        """
        corpses = [corpse.description for corpse in self.morgue]
        return(corpses)

    
    def get_trap(self):
        """
        Возвращает активированную ловушку, последнюю увиденную в комнате, если таковая имеется.

        Возвращает:
            Trap|None: Объект ловушки, если в комнате есть активированная последняя увиденная ловушка. В противном случае возвращает None.
        """
        if self.last_seen_trap:
            if self.last_seen_trap.activated:
                return self.last_seen_trap
        return None

    
    def show_furniture(self) -> list:
        """
        Возвращает список описаний мебели в комнате.

        Возвращает:
            list: Список строк, каждая из которых представляет описание мебели в комнате.
        """
        furniture_list  = []
        for furniture in self.furniture:
                furniture_list.append(furniture.where + ' ' + furniture.state + ' ' + furniture.lexemes['nom'])
        return furniture_list
    
    
    def get_secret_word(self) -> str:
        """
        Возвращает секретное слово, связанное с комнатой.

        Возвращает:
            str: Секретное слово, связанное с комнатой. Если секретное слово не найдено, возвращается пустая строка.
        """
        secret_word = ''
        for i in Room._secrets:
            if self.description.find(i) > -1:
                secret_word = i
        return secret_word
    

    def get_available_directions(self) -> list:
        """
        Метод определяет, в каких направлениях герой может выйти из комнаты.
        Возвращает список направлений.
        
        """
        
        available_directions = []
        for i in range(4):
            if not self.doors[i].empty and not self.doors[i].locked:
                available_directions.append(i)
        return available_directions

      
    def decorate(self):
        """
        Украшает комнату, случайным образом выбирая декорации из предопределенных списков и создавая описание.

        Этот метод случайным образом выбирает декорации из списков 'decor1', 'decor2', 'decor3' и 'decor4' класса Room. 
        Он назначает выбранные декорации атрибутам 'decoration1', 'decoration2', 'decoration3' и 'decoration4' соответственно. 
        Затем он создает описание комнаты, комбинируя декорации следующим образом: '{decoration1} комнату {decoration2}. {decoration4}'.

        Метод не принимает параметров и не возвращает значений.
        """
        self.decoration1 = randomitem(Room.decor1)
        self.decoration2 = randomitem(Room.decor2)
        self.decoration3 = randomitem(Room.decor3)
        self.decoration4 = randomitem(Room.decor4)
        self.description = f'{self.decoration1} комнату {self.decoration2}. {self.decoration4}'

    
    def can_rest(self, mode:str='full'):
        """Функция проверяет, можно ли отдыхать в комнате

        Принимает на вход параметр mode:
        - если mode == 'full', метод возвращает список причин и объект мебели
        - если mode == 'simple', метод возвращает булево значение можно ли отдыхать в комнате
        
        Возвращает:
            - list: Список причин, почему нельзя отдыхать в комнате
            - obj Furniture: Объект мебели, который позволяет отдохнуть
        """
        message = []
        monster = self.monsters('first')
        if monster:
            message.append('Враг, который находится в комнате, точно не даст отдохнуть.')
        if self.stink > 0:
            message.append('В комнате слишком сильно воняет чтобы уснуть.')
        if not self.light:
            message.append('В комнате так темно, что нельзя толком устроиться на отдых.')
        place = False
        for furniture in self.furniture:
            if furniture.can_rest:
                place = furniture
        if not place:
            message.append('В комнате нет места, где можно было бы отдохнуть.')
        if mode == 'simple':
            return len(message) == 0
        return message, place
    
    
    def show(self, player):
        """
        Отображает описание комнаты и её содержимое игроку.

        Параметры:
            player (Player): Объект игрока.

        Возвращает:
            None
        """
        if self.light:
            message = self.show_with_light_on(player)
        else:
            message = self.show_with_light_off()
        tprint(self.game, message, state='direction')

    
    def show_with_light_off(self) -> list[str]:
        monster = self.monsters('first')
        message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
        if monster:
            message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
        message.append(self.get_stink_text())
        return message
    
    
    def show_with_light_on(self, player) -> list[str]:
        message = []
        decoration = self.get_decoration_for_show()
        monster_text = self.get_monster_text_for_show()
        message.append(f'{player.name} попадает в {decoration} '
                       f'комнату {self.decoration2}. {self.decoration4}')
        message.extend(self.show_furniture())
        message.extend(self.get_ladders_text())
        if self.trader:
            message.append(self.trader.show())
        message += self.show_corpses()
        message.append(monster_text)
        message.append(self.get_stink_text())
        return message
        

    def get_ladders_text(self) -> list[str]:
        message = []
        if self.ladder_down:
            message.append(self.ladder_down.show_in_room_as_ladder_down())
        if self.ladder_up:
            message.append(self.ladder_up.show_in_room_as_ladder_up())
        return message
    
    
    def get_monster_text_for_show(self) -> str:
        monster = self.monsters('first')
        if not monster:
            return 'Не видно ничего интересного.'
        return f'{self.decoration3} {monster.state} {monster.name}.'
    
    
    def get_decoration_for_show(self) -> str:
        if self.torch:
            return f'освещенную факелом {self.decoration1}'
        return self.decoration1
    
    
    def get_stink_text(self) -> str|None:
        if self.stink > 0:
            return f'{Room._stink_levels[self.stink]} воняет чем-то очень неприятным.'
        return None
    
    
    def show_through_key_hole(self, who):
        """
        Отображает, что можно увидеть через замочную скважину двери.

        Параметры:
            who (object): Объект, представляющий персонажа, заглядывающего в замочную скважину.

        Возвращает:
            list: Список строк, описывающих, что можно увидеть через замочную скважину.

        Если в комнате есть торговец, метод вызывает метод 'show_through_key_hole' объекта торговца и возвращает его результат.
        Если в комнате нет монстра, метод добавляет в список 'message' строку, указывающую, что персонаж не может ничего толком разглядеть через замочную скважину.
        Если в комнате есть монстр, метод добавляет в список 'message' строку, указывающую, что персонаж может видеть монстра через замочную скважину.
        Если уровень вони в комнате больше 0, метод добавляет в список 'message' строку, указывающую, что из замочной скважины воняет чем-то омерзительным.

        """
        if self.traider:
            return self.traider.show_through_key_hole()
        monster = self.monsters('first')
        message = []
        if not monster:
            message.append(f'{who.name} заглядывает в замочную скважину двери, но не может ничего толком разглядеть.')
        else:
            message.append(f'{who.name} заглядывает в замочную скважину двери и {monster.key_hole}')
        if self.stink > 0:
            message.append(f'Из замочной скважины {Room._stink_levels[self.stink].lower()} воняет чем-то омерзительным.')
        return message

    
    def furniture_types(self):
        """
        Возвращает список уникальных типов мебели, присутствующих в комнате.

        Возвращает:
            list: Список строк, каждая из которых представляет уникальный тип мебели в комнате.

        Метод проходит по объектам мебели в комнате и проверяет, присутствует ли тип каждого объекта мебели уже в списке 'types'. 
        Если нет, он добавляет тип в список. В конце концов, метод возвращает список уникальных типов мебели.
        """
        types = []
        for furniture in self.furniture:
            if furniture.type not in types:
                types.append(furniture.type)
        return types

    
    def clear_from_monsters(self):
        """
        Очищает комнату от всех монстров.

        Этот метод получает список монстров, находящихся в комнате, используя метод 'monsters'. 
        Затем он проходит по каждому монстру в списке и вызывает метод 'place' для монстра, передавая в качестве аргумента атрибут 'floor' комнаты.

        Параметры:
            Нет

        Возвращает:
            Нет
        """
        monsters = self.monsters()
        for monster in monsters:
            monster.place(self.floor, old_place=self)           
    
    
    def monsters(self, mode=None):
        all_monsters = self.floor.monsters_in_rooms[self]
        if all_monsters:
            if mode == 'random':
                return randomitem(all_monsters)
            elif mode == 'first':
                return all_monsters[0]
            else:
                return all_monsters
        else:
            return []
        
    
    def has_a_monster(self) -> bool:
        monsters = self.floor.monsters_in_rooms[self]
        return bool(monsters)
    
    
    def monster_in_ambush(self):
        monsters = self.monsters()
        if monsters:
            for monster in self.monsters():
                if monster.hiding_place == self:
                    return monster 
        return False
    
    
    def map(self):
        if not self.light:
            return False
        message = []
        game = self.game
        top_door:str = f'{self.doors[0]:horizontal}'
        left_door:str = f'{self.doors[3]:vertical}'
        right_door:str = f'{self.doors[1]:vertical}'
        bottom_door:str = f'{self.doors[2]:horizontal}'
        symbol:str = self.get_symbol_for_plan()
        second_line = self.get_second_line_for_plan()
        fourth_line = self.get_fourth_line_for_plan()
        message.append(f'=={top_door}==')
        message.append(second_line)
        message.append(f'{left_door} {symbol} {right_door}')
        message.append(fourth_line)
        message.append(f'=={bottom_door}==')
        pprint(game, message, Room._plan_picture_width, Room._plan_picture_height)
        return True

    
    def get_symbol_for_plan(self) -> str:
        monster = self.monsters('first')
        if monster:
            return monster.name[0]
        if self.trader:
            return '₽'
        return ' '
    
    
    def get_second_line_for_plan(self) -> str:
        if self.ledder_up:
            return '║  #║'
        return '║   ║'
    
    
    def get_fourth_line_for_plan(self) -> str:
        if self.ledder_down:
            return '║#  ║'
        return '║   ║'
    
    def lock(self):
        for door in self.doors:
            if not door.empty:
                door.locked = True
        self.locked = True
        return None
    
    
    def turn_on_light(self, who) -> NoReturn:
        
        """Метод зажигания в комнате света. """
        
        self.light = True
        self.torch = True
        monster = self.monsters('first')
        message = [
                f'{who.name} зажигает факел и комната озаряется светом']
        if monster:
            if monster.frightening:
                message.append(
                        f'{who.name} замирает от ужаса глядя на чудовище перед собой.')
                who.fear += 1
        tprint(self.game, message)
        self.show(who)
        self.map()
        if monster:
            if monster.agressive:
                who.fight(monster.name, True)
                
    
    def get_random_unlocked_furniture(self) -> Furniture:
        if self.furniture:
            furniture_list = [f for f in self.furniture if not f.locked]
            return randomitem(furniture_list)
        return None


class Trap:
    """
    Класс, представляющий ловушку.

    Атрибуты:
        game (Game): Экземпляр игры, связанный с ловушкой.
        activated (bool): Указывает, активирована ли ловушка.

    Методы:
        __init__(game): Инициализирует ловушку с данным экземпляром игры.
        deactivate() -> bool: Обезвреживает ловушку и возвращает True.
    """
    
    types = [
        'intel',
        'stren',
        'dex',
        'armor',
        #'weapon',
        #'backpack'
    ]
    
    detection_texts = [
        'Сбоку отчетливо виден какой-то странный механизм.',
        'Тоненький волосок прикреплен к крышке.',
        'Изнутри слышно какое-то странное пощелкивание.',
        'В щели между крышкой и корпусом видно натянутую нитку.',
        'Кто-то явно что-то делал с крышкой - щель с одной стороны шире, чем с другой.'
    ]
    
    
    def __init__(self, game, where=None, limit=0):
        self.game = game
        self.activated = False
        self.seen = False
        self.triggered = False
        self.difficulty = self.set_difficulty(limit)
        self.detection_text = None
        self.where = where
        self.actions = {
            'intel': self.damage_intel,
            'stren': self.damage_stren,
            'dex': self.damage_dex,
            'armor': self.damage_armor,
            #'weapon': self.damage_weapon,
            #'backpack': self.damage_backpack
        }
    
    
    def get_detection_text(self) -> str:
        if self.detection_text:
            return self.detection_text
        texts = Trap.detection_texts
        text = randomitem(texts)
        self.detection_text = text
        return text     
    
    
    def set_difficulty(self, limit:int):
        self.difficulty = roll([limit])
        

    def get_disarm_difficulty(self) -> int:
        return self.difficulty * 2
    
    
    def deactivate(self) -> bool:
        if not self.activated:
            return False
        self.activated = False
        return True
    
    
    def activate(self) -> bool:
        if self.activated:
            return False
        self.activated = True
        return True
      
    
    def trigger(self, target) -> list[str]:
        """
        Активирует ловушку и применяет её эффекты к цели.

        Этот метод копирует список типов ловушек, выбирает случайный тип и применяет соответствующее действие к цели.
        Если у ловушки нет метода для выбранного типа, возбуждается исключение.
        После активации ловушка деактивируется, становится видимой и помечается как сработавшая.

        Args:
            target: Цель, к которой применяется эффект ловушки.

        Returns:
            Список строк с сообщениями о последствиях активации ловушки.
        """
        types = Trap.types.copy()
        message = [f'От неловкого прикосновения в ловушка начинает противно щелкать, а потом взрывается.']
        while True:
            if not types:
                message.append(f'{target.name} настолько {target.g(["некчемен", "некчемна"])},' 
                               f' что ловушка не может причинить еще какой-то дополнительный урон.')
                return message
            action_type = randomitem(types)
            types.remove(action_type)
            action = self.actions.get(action_type, False)
            if not action:
                raise Exception(f'У ловушки нет метода для типа {action_type}')
            action_text = action(target)
            if action_text:
                message.append(action_text)
                self.deactivate()
                self.seen = True
                self.triggered = True
                return message
    
    
    def disarm(self) -> list[str]:
        self.deactivate()
        self.seen = True
        self.triggered = False
        return [f'Ловушка тихонько щелкает и больше не издает ни звука. Похоже, она больше не опасна.']
    
    
    def damage_intel(self, target) -> str:
        return target.intel_wound()
    
    
    def damage_stren(self, target) -> str:
        return target.stren_wound()
      
    
    def damage_dex(self, target) -> str:
        return target.dex_wound()
        

    def damage_armor(self, target) -> bool|str:
        if target.armor.empty:
            return False
        return True


"""     def damage_weapon(self, target) -> bool|str:
        if target.weapon.empty:
            return False
        return True
 """

"""     def damage_backpack(self, target) -> bool|str:
        if target.backpack.empty:
            return False
        return True
 """        