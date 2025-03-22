from typing import Optional

from src.class_basic import Loot
from src.controllers.controller_actions import ActionController
from src.functions.functions import pprint, randomitem, tprint, roll, randomitem_dict


class Ladder:
    """ 
    Класс лестниц.    
    """
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
        self.name = 'лестница'
        self.room_down = room_down
        self.locked = locked
        self.decorate()
        self.place()
        self.room_actions = {
            "отпереть": {
                "method": "unlock",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "show_for_unlock",
                "condition": "is_locked",
                "duration": 2
                },
            "спуститься": {
                "method": "go_down",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "presentation": "show_for_go",
                "condition": "going_down",
                "duration": 1
                },
            "подняться": {
                "method": "go_up",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "presentation": "show_for_go",
                "condition": "going_up",
                "duration": 1
                },
        }
    
    
    def going_down(self, room=None) -> bool:
        """ 
        Возвращает True если лестница ведет вниз
        """
        return self.get_direction(room) == 'вниз'
    

    def going_up(self, room=None) -> bool:
        """ 
        Возвращает True если лестница ведет вверх
        """
        return self.get_direction(room) == 'вверх'

    
    def is_locked(self, room=None) -> bool:
        """ 
        Возвращает True если лестница заперта
        """
        return self.locked
    
    
    def get_direction(self, room) -> str:
        """ 
        Возвращает текст направления лестницы из указанной комнаты - вниз или вверх
        """
        if self.room_down == room:
            return 'вверх'
        if self.room_up == room:
            return 'вниз'
        return ''
    
    
    def go_down(self, who, in_action:bool=False) -> str:
        """ 
        Обрабатывает спуск по лестнице
        """
        if not who.check_light():
            return who.go_down_with_light_off()
        return who.go_down_with_light_on()


    def go_up(self, who, in_action:bool=False) -> str:
        """ 
        Обрабатывает подъем по лестнице
        """
        if not who.check_light():
            return who.go_up_with_light_off()
        return who.go_up_with_light_on()

    
    def show_for_go(self, who) -> str:
        """ 
        Возвращает текст описани для команды 'идти'
        """
        direction = self.get_direction(who.current_position)
        return f'Лестница, ведущая {direction}'
    

    def show_for_unlock(self, who) -> str:
        """ 
        Возвращает текст описания для команды 'отпереть'
        """
        room = who.current_position
        direction = self.get_direction(room)
        if direction == 'вверх':
            return 'Люк в потолке, закрытый тяжелой крышкой.'
        if direction == 'вниз':
            return 'Квадратный люк в полу, плотно закрытый крышкой.'
        return f'{self:nom}'
    
    
    def unlock(self, who, in_action:bool=False) -> str:
        """ 
        Обрабатывает действие Отпереть
        """
        if not self.locked:
            return 'Лестница не заперта, по ней спокойно можно подниматься и спускаться.'
        room = who.current_position
        direction = self.get_direction(room)
        key = who.backpack.get_first_item_by_class('Key')
        if not key:
            return f'У {who:gen} нет подходящего ключа чтобы отпереть эту лестницу.'
        who.backpack.remove(key)
        self.locked = False
        return f'{who.name} отпирает {self:accus}, ведущую {direction}, ключом.'
    
    
    def __format__(self, format:str) -> str:
        """ 
        Возвращает представление экземпляра класса в виде форматированной строки
        """
        return self.lexemes.get(format, '')

    
    def place(self) -> bool:
        """ 
        Размещает лестницу в замке
        """
        if not isinstance(self.room_down, Room):
            raise TypeError(f'К лестнице привязан неправильный объект {self.room_down.__class__.__name__} в качестве нижней комнаты.')
        self.room_down.ladder_up = self
        if not isinstance(self.room_up, Room):
            self.room_up = self.get_random_room_up()
        self.room_up.ladder_down = self
        self.room_down.action_controller.add_actions(self)
        self.room_up.action_controller.add_actions(self)
        return True
    
    
    def decorate(self) -> None:
        """ 
        Генерирует описание и лексемы лестницы
        """
        self.lexemes = {}
        first_words = randomitem(Ladder._first_decorators)
        second_words = randomitem(Ladder._second_decorators)
        for key in Ladder._lexemes:
            description = f'{first_words[key]} {second_words[key]} {Ladder._lexemes[key]}'
            self.lexemes[key] = description

    
    def show_in_room_as_ladder_down(self) -> str:
        """ 
        Возвращает текст описания лестницы, ведущей вниз, для описания комнаты
        """
        if self.locked:
            return 'В полу имеется квадратный люк, плотно закрытый крышкой.'
        return f'{self:nom} спускается вниз в темноту.'.capitalize()
        

    def show_in_room_as_ladder_up(self) -> str:
        """ 
        Возвращает текст описания лестницы, ведущей вверх, для описания комнаты
        """
        if self.locked:
            return f'{self:nom} поднимается к люку в потолке, закрытому тяжелой крышкой.'.capitalize()
        return f'{self:nom} ведет куда-то вверх.'.capitalize()
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """ 
        Возвращает список имен лестницы
        """
        return ['лестница', 'лестницу']



class Door:
    """Класс дверей."""
    
    _directions = {
        0: 'вверх',
        1: 'направо',
        2: 'вниз',
        3: 'налево'
    }
    
    def __init__(self, game):
        self.locked = False
        self.rooms = []
        self.closed = True
        self.empty = True
        self.game = game
        self.name = 'дверь'
        self.room_actions = {
            "отпереть": {
                "method": "unlock",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "show_for_unlock",
                "condition": "is_locked",
                "duration": 2
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "show_for_unlock",
                "duration": 1
                },
            "идти": {
                "method": "go",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "presentation": "show_for_unlock",
                "post_process": "check_disturbed_monsters",
                "duration": 1
                },
        }
    
    
    def go(self, who, in_action:bool=False) -> list[str]:
        """
        Метод обрабатывает команду Идти
        """
        direction_number = self.get_direction_index(who.current_position)
        if who.check_light():
            return who.go_with_light_on(direction_number)
        return who.go_with_light_off(direction_number)
    
    
    def examine(self, who, in_action:bool=False) -> str:
        """
        Метод генерирует текст сообщения когда герой осматривает дверь.
        """
        room = who.current_position
        if self.empty:
            message = f'{who.name} осматривает стену и не находит ничего заслуживающего внимания.'
        elif who.check_fear():
            message = f'{who.name} не может заставить себя заглянуть в замочную скважину. Слишком страшно.'
        else:
            room_behind_the_door = self.get_another_room(room)
            message = room_behind_the_door.show_through_key_hole(who)
        return message
    
    
    def get_another_room(self, room) -> 'Room':
        """ 
        Возвращает комнату, в которую ведет дверь
        """
        if room not in self.rooms or len(self.rooms) < 2:
            return None
        return [another_room for another_room in self.rooms if not another_room == room][0]
    
    
    def is_locked(self, room=None) -> bool:
        """ 
        Возвращает True если дверь заперта
        """
        return self.locked
    
    
    def get_direction_index(self, room) -> int:
        """ 
        Возвращает целочисленный индекс направления, в котором ведет дверь
        """
        try:
            index = room.doors.index(self)
        except Exception:
            print(f'Дверь {self} не найдена в комнате {room}.')
            return None
        return index
    
    
    def show_for_unlock(self, who) -> str:
        """ 
        Возвращает описание для команды Отпереть
        """
        room = who.current_position
        direction_index = self.get_direction_index(room)
        direction = Door._directions.get(direction_index, False)
        if direction:
            return f'Дверь, ведущая {direction}.'
    
    
    def unlock(self, who, in_action:bool=False) -> str:
        """ 
        Обрабатывает команду Отпереть
        """
        if not self.locked:
            return 'Дверь не заперта, через нее вполне можно пройти.'
        room = who.current_position
        direction_index = self.get_direction_index(room)
        direction = Door._directions.get(direction_index, False)
        key = who.backpack.get_first_item_by_class('Key')
        if not key:
            return f'У {who:gen} нет подходящего ключа чтобы отпереть эту дверь.'
        who.backpack.remove(key)
        self.locked = False
        return f'{who.name} отпирает дверь, ведущую {direction}, ключом.'
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """ 
        Возвращает список текстовых представлений двери
        """
        names = ['дверь']
        if room:
            index = self.get_direction_index(room)
            direction = Door._directions.get(index, False)
            if direction:
                names.append(direction)
        return names
    
    
    def __bool__(self):
        """ 
        Преобразует состояние двери boolean
        """
        return not self.empty
    
    
    def __format__(self, format_string:str):
        """ 
        Возвращает представление экземпляра класса в виде форматированной строки
        """
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
        """ 
        Активирует дверь
        """
        self.empty = False
        self.locked = False
        self.closed = True
        

class Room:
    """Класс комнат."""
    
    _decor1 = (
        'большую',
        'темную',
        'тесную',
        'просторную',
        'зловещую',
        'веселенькую',
        'сырую',
        'древнюю',
        'грязную',
        'оклееную обоями',
        'увешанную трофеями',
        'захламленную',
        'замызганную',
        'недоремонтированную',
        'безвкусную',
        'стильную',
        'удобную',
        'уютную',
        'светлую',
        'малюсенькую',
        'чистую',
        'строгую',
        'крохотную',
        'огромную',
        'жилую',
        'нежилую',
        'вонючую',
        'несимпатичную',
        'душную',
        'прохладную',
        'сумрачную',
        'продолговатую',
        'квадратную',
        'обшарпаную',
        'уединенную',
        'комфортабельную',
        'убогую',
        'прямоугольную',
        'безликую',
        'овальную',
        'унылую',
        'крошечную',
        'потаенную',
        'невзрачную',
        'пыльную',
        'роскошную',
    )
    
    _decor2 = {
        'с огромными окнами': [],
        'с полом, застеленным красным старым ковром': [],
        'с красивой люстрой на потолке': [],
        'с картинами, изображающими кошечек, на стенах': [],
        'с унитазом в углу': ['унитаз'],
        'с паутиной по углам': [],
        'с птичьей клеткой на подоконнике': ['клетка'],
        'с аквариумом во всю стену': ['аквариум'],
        'со скользким от крови полом': [],
        'с красивой мебелью': [],
        'с резными ручками на дверях': [],
        'с барной стойкой посередине': ['стойка'],
        'с длинным столом': ['стол'],
        'с кучей стульев': [],
        'с выбитыми стеклами в окнах': [],
        'со стильными светильниками': [],
        'с деревянным полом': [],
        'с раковиной у двери': ['раковина'],
        'с низким потолком': [],
        'со скамейками вдоль стен': [],
        'с белыми стенами': [],
        'с черными стенами': [],
        'с грязным полом': [],
        'с помойным баком у двери': ['бак'],
        'с маленьким балконом': [],
        'с видом на озеро': [],
        'с видом на двор': [],
        'с видом на помойку': [],
        'со следами борьбы повсюду': [],
        'со сломанной дверью': [],
        'с хламом в углу': ['хлам'],
        'с приятным интерьером': [],
        'с пыльными шторами': [],
        'с треснувшим зеркалом на стене': [],
        'с древними книгами на полках': [],
        'с мягким диваном в углу': ['диван'],
        'с яркими граффити на стенах': [],
        'с фонтаном в центре': ['фонтан'],
        'с винтажными обоями': [],
        'с металлическими решетками на окнах': [],
        'с тихо журчащим аквариумом': ['аквариум'],
        'с потухшим камином': ['камин'],
        'со странными рисунками на стенах': [],
        'с руной, начертанной на полу': [],
        'с кружевными занавесками': [],
        'с разбитой посудой': [],
        'с желтой лужей в углу': [],
        'с петлей, свисающей с потолка': [],
        'с цветами на подоконнике': [],
        'с отбитой плиткой на полу': [],
        'со скрипучим полом': [],
        'с помойным ведром у двери': ['ведро'],
        'с хрустальной люстрой': [],
        'с заклееными газетами окнами': [],
        'с головой льва на стене': [],
    }
    
    _decor3 = (
        'В центре комнаты',
        'В углу',
        'У окна',
        'У дальней стены',
        'Перед дверью',
        'Вдалеке',
        'На расстоянии удара',
        'В поле зрения',
        'В помещении',
        'Неподалеку',
        'У стола',
        'У стены',
        'В тени',
        'В пятне света от окна',
        'За занавеской',
        'На расстоянии выстрела из лука',
        'На расстоянии прыжка',
        'Под светильником',
    )
    
    _decor4 = {
        'Пахнет свежей едой.': [],
        'В воздухе полно пыли.': [],
        'Похоже, сейчас не лучшее время здесь быть!': [],
        'По стенам скачут солнечные блики.': [],
        'В комнате полно мух.': [],
        'На подоконнике развалился огромный кот.': [],
        'В канделябрах горят свечи.': [],
        'Веет могильным холодом.': [],
        'По комнате гуляют сквозняки.': [],
        'Паук плетет паутину в углу.': [],
        'За стеной громко играет музыка.': [],
        'Где-то неподалеку плачет ребенок.': [],
        'Из темного угла слышны звуки какой-то возни.': [],
        'Ветер хлопает створками окна.': [],
        'Комнату явно давно не проветривали.': [],
        'Комната заполнена дымом, от которого щиплет глаза.': [],
        'Повсюду валяется какой-то хлам.': ['хлам'],
        'Дождь барабанит по оконному стеклу.': [],
        'Один из светильников неприятно мигает.': [],
        'Непонятно откуда слышатся тихие шепоты.': [],
        'По полу летают сухие листья.': [],
        'Под окном валяются детские игрушки.': ['игрушки'],
        'На стене висит окровавленная пила.': [],
        'Под ногами чавкает какая-то жижа.': [],
        'Приходится идти по разбитому стеклу.': [],
        'На стенах висят гобелены с гербами.': [],
        'На полу разбросаны соломенные циновки.': [],
        'В комнате пахнет воском и ладаном.': [],
        'На столе лежат пергаменты и чернильница.': ['стол'],
        'В комнате слышен звон колоколов.': [],
        'На полу лежит медвежья шкура.': ['шкура'],
        'В углу стоит арфа.': [],
        'На стенах висят охотничьи трофеи.': [],
        'В комнате пахнет свежим хлебом.': [],
        'В комнате слышен треск дров в камине.': ['камин'],
        'В углу стоит деревянная статуя.': [],
        'На стенах висят портреты королей.': [],
        'В комнате пахнет травами и специями.': [],
        'На столе лежат шахматные фигуры.': [],
        'На полу лежит коврик из овечьей шерсти.': [],
        'В углу стоит деревянная кадка с водой.': ['кадка'],
    }
   
    _torch_die = 5
    """
    Кубик, который кидается чтобы определить, горит в комнате факел, или нет 
    (берется выпадение одного конкретного значения).

    """
    
    _stink_levels = {1: 'Немного', 2: 'Сильно', 3: 'Невыносимо'}
    """Уровни вони."""
    
    _plan_picture_width = 100
    """Ширина картинки плана комнаты."""

    _plan_picture_height = 120
    """Высота картинки плана комнаты."""

    
    def __init__(self, game, floor, doors):
        self.game = game
        self.name = 'комната'
        self.action_controller = ActionController(game=self.game, room=self)
        self.floor = floor
        self.doors = doors
        self.link_doors()
        self.generate_doors_actions()
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
        self.ladder_up:Ladder = self.game.empty_thing
        self.ladder_down:Ladder = self.game.empty_thing
        self.last_seen_trap = None
        self.torch = self.set_torch()
        self.secrets:list = list()
        self.has_secrets:bool = False
        self.enter_point = False
        self.decorate()
        self.generate_actions()

    
    def generate_actions(self):
        """ 
        Генерирует действия, которые можно совершить с комнатой.
        """
        self.room_actions = {
            "обыскать": {
                "method": "search",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 2
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "map_for_examine",
                "duration": 1
                },
            "осмотреться": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "map_for_examine",
                "duration": 1
                },
            "оглядеться": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "map_for_examine",
                "duration": 1
                },
        }
        self.action_controller.add_actions(self)
    
    
    def noise(self, noise_level:int, noise_source=None):
        """
        Функция распространения шума по замку.
        """
        self.noise_trigger(noise_source)
        available_rooms = self.get_rooms_around()
        if noise_level > 1:
            for next_room in available_rooms:
                next_room.noise(noise_level - 1, self)
        return True
    

    def set_stink(self, stink_level:int):
        """
        Функция распространения вони по замку.
        """
        if self.stink >= stink_level:
            return True
        else:
            self.stink = stink_level
        available_rooms = self.get_rooms_around()
        if stink_level > 1:
            for next_room in available_rooms:
                next_room.set_stink(stink_level - 1)
        return True
    
    
    def get_rooms_around(self) -> list:
        """
        Возвращает список всех комнат, в которые можно перейти из заданной комнаты.
        """
        available_rooms = []
        for door in self.doors:
            if door and not door.locked and not door.empty:
                available_rooms.append(door.get_another_room(self))
        if self.ladder_down and not self.ladder_down.locked:
            available_rooms.append(self.ladder_down.room_down)
        if self.ladder_up and not self.ladder_up.locked:
            available_rooms.append(self.ladder_up.room_up)
        return available_rooms
    

    def noise_trigger(self, noise_source):
        """ 
        Обрабатывает событие возникновения в комнате шума
        """
        return
    
    
    def link_doors(self):
        """ 
        Связывает комнату с ее дверями
        """
        for door in self.doors:
            door.rooms.append(self)
    
    
    def map_for_examine(self, who):
        """ 
        Возвращает план комнаты для команды Осмотреть
        """
        self.map()
    
    
    def examine(self, who, in_action:bool=False) -> str:
        """ 
        Обрабатывает команду Осмотреть
        """
        if self.light:
            message = self.show_with_light_on(who)
        else:
            message = self.show_with_light_off()
        return message
    
    
    def generate_doors_actions(self):
        """ 
        Добавляет действия дверей комнаты в массив действий комнтаы
        """
        for door in self.doors:
            if not door.empty:
                self.action_controller.add_actions(door)
        return
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """ 
        Возвращает список текстовых представлений экземпляра класса
        """
        return ['комната', 'комнату']
    
    
    def search(self, who, in_action:bool=False) -> list[str]:
        """
        Метод обыскивания комнаты.
        """
        message = []
        if who.check_monster_in_ambush(place=self):
            return ''
        for furniture in self.furniture:
            message.append(str(furniture))
        if not self.loot.empty and len(self.loot.pile) > 0:
            message.append('В комнате есть:')
            message += self.loot.show_sorted()
        else:
            message.append('В комнате нет ничего интересного.')
        if self.has_a_corpse():
            message + self.show_corpses()
        return message
    
    
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
        """ 
        Зажигает в комнате факел
        """
        if not self.light or roll([Room._torch_die]) != Room._torch_die:
            return False
        new_torch = self.game.weapon_controller.get_random_objects_by_class_name('Torch')[0]
        new_torch.place(self.floor, self)
        return new_torch

    
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

    
    def has_furniture(self) -> bool:
        """ 
        Возвращает True если в комнате есть мебель
        """
        return bool(self.furniture)
    
    
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
        self.decoration1 = randomitem(Room._decor1)
        self.decoration2, secrets1 = randomitem_dict(Room._decor2)
        self.decoration3 = randomitem(Room._decor3)
        self.decoration4, secrets2 = randomitem_dict(Room._decor4)
        secret_places = secrets1 + secrets2
        self.description = f'{self.decoration1} комнату {self.decoration2}. {self.decoration4}'
        self.generate_secrets(secret_places)
    

    def generate_secrets(self, secret_places):
        """ 
        Генерирует в комнате секретные места
        """
        for place in secret_places:
            new_secret = self.game.secret_places_controller.create_object_by_name(place)
            new_secret.place(self)
        if self.secrets:
            self.has_secrets = True

    
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
        """ 
        Генерирует описание комнаты если в ней выключен свет
        """
        monster = self.monsters('first')
        message = ['В комнате нет ни одного источника света. Невозможно различить ничего определенного.']
        if monster:
            message.append('В темноте слышатся какие-то странные звуки, кто-то шумно дышит и сопит.')
        message.append(self.get_stink_text())
        return message
    
    
    def show_with_light_on(self, player) -> list[str]:
        """ 
        Генерирует описание комнаты если в ней включен свет
        """
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
        message.extend(monster_text)
        message.append(self.get_stink_text())
        return message
        

    def get_ladders_text(self) -> list[str]:
        """ 
        Генерирует описание лестниц, которые ведут из комнаты
        """
        message = []
        if self.ladder_down:
            message.append(self.ladder_down.show_in_room_as_ladder_down())
        if self.ladder_up:
            message.append(self.ladder_up.show_in_room_as_ladder_up())
        return message
    
    
    def get_monster_text_for_show(self) -> list[str]:
        """ 
        Генерирует описание находящихся в комнате монстров
        """
        monsters = self.monsters()
        message = []
        if not monsters:
            return ['Не видно ничего интересного.']
        for monster in monsters:
            message.append(f'{randomitem(Room._decor3)} {monster.state} {monster.name}.')
        return message
    
    
    def get_decoration_for_show(self) -> str:
        """ 
        Добавляет в описание комнаты упоминание того, что она освещена факелом
        """
        if self.torch:
            return f'освещенную факелом {self.decoration1}'
        return self.decoration1
    
    
    def get_stink_text(self) -> str|None:
        """ 
        Генерирует описание комнаты если в ней что-то воняет
        """
        if self.stink > 0:
            return f'{Room._stink_levels[self.stink]} воняет чем-то очень неприятным.'
        return None
    
    
    def show_through_key_hole(self, who):
        """
        Отображает, что можно увидеть через замочную скважину двери.
        """
        if self.trader:
            return self.trader.show_through_key_hole()
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
        """
        types = []
        for furniture in self.furniture:
            if furniture.furniture_type not in types:
                types.append(furniture.furniture_type)
        return types

    
    def clear_from_monsters(self):
        """
        Очищает комнату от всех монстров.
        """
        monsters = self.monsters()
        for monster in monsters:
            monster.place(self.floor, old_place=self)           
    
    
    def monsters(self, mode=None):
        """ 
        Возвращает список монстров, находящихся в комнате
        """
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
        """ 
        Возвращает True если в комнате есть хотя бы один монстр
        """
        monsters = self.floor.monsters_in_rooms[self]
        return bool(monsters)
    
    
    def monster_in_ambush(self):
        """ 
        Возвращает монстра, сидящего в засаде
        """
        monsters = self.monsters()
        if monsters:
            for monster in self.monsters():
                if monster.hiding_place == self:
                    return monster 
        return False
    
    
    def map(self):
        """ 
        Генерирует план комнаты
        """
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
        """ 
        Возвращает символ, который должен отображаться на плане комнаты
        """
        monster = self.monsters('first')
        if monster:
            return self.get_monsters_symbol()
        if self.trader:
            return '₽'
        return ' '
    
    
    def get_number_of_monsters(self) -> int:
        """ 
        Возвращает количество монстров в комнате
        """
        return len(self.floor.monsters_in_rooms[self])
    
    
    def get_monsters_symbol(self) -> str:
        """ 
        Возвращает первую букву имени монстра или символ, обозначающий, что монстров несколько
        """
        number_of_monsters = self.get_number_of_monsters()
        if number_of_monsters == 1:
            return '~'
        return '≈'
        
    
    def get_second_line_for_plan(self) -> str:
        """ 
        Возвращает вторую строку для генерации плана
        """
        if self.ladder_up:
            return '║  #║'
        return '║   ║'
    
    
    def get_fourth_line_for_plan(self) -> str:
        """ 
        Возвращает четвертую строку для генерации плана
        """
        if self.ladder_down:
            return '║#  ║'
        return '║   ║'
    
    def lock(self):
        """ 
        Запирает комнату
        """
        for door in self.doors:
            if not door.empty:
                door.locked = True
        self.locked = True
        return None
    
    
    # def turn_on_light(self, who) -> list[str]:
        
    #     """Метод зажигания в комнате света. """
        
    #     self.light = True
    #     self.torch = True
    #     monster = self.monsters('first')
    #     message = [
    #             f'{who.name} зажигает факел и комната озаряется светом']
    #     if monster:
    #         if monster.frightening:
    #             message.append(f'{who.name} замирает от ужаса глядя на чудовище перед собой.')
    #             who.fear += 1
    #     return message
                
    
    def get_random_unlocked_furniture(self):
        """ 
        Возвращает случаный незапертый объект мебели, находящийся в комнате
        """
        if self.furniture:
            furniture_list = [f for f in self.furniture if not f.locked]
            if furniture_list:
                return randomitem(furniture_list)
        return None
