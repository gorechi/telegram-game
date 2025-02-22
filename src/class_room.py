from typing import Optional

from src.class_basic import Loot
from src.controllers.controller_actions import ActionController
from src.functions.functions import pprint, randomitem, tprint, roll


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
                "condition": "is_locked"
                },
            "спуститься": {
                "method": "go_down",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "presentation": "show_for_go",
                "condition": "going_down"
                },
            "подняться": {
                "method": "go_up",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "presentation": "show_for_go",
                "condition": "going_up"
                },
        }
    
    
    def going_down(self, room=None) -> bool:
        return self.get_direction(room) == 'вниз'
    

    def going_up(self, room=None) -> bool:
        return self.get_direction(room) == 'вверх'

    
    def is_locked(self, room=None) -> bool:
        return self.locked
    
    
    def get_direction(self, room) -> str:
        if self.room_down == room:
            return 'вверх'
        if self.room_up == room:
            return 'вниз'
        return ''
    
    
    def go_down(self, who, in_action:bool=False) -> str:
        if not who.check_light():
            return who.go_down_with_light_off()
        return who.go_down_with_light_on()


    def go_up(self, who, in_action:bool=False) -> str:
        if not who.check_light():
            return who.go_up_with_light_off()
        return who.go_up_with_light_on()

    
    def show_for_go(self, who) -> str:
        direction = self.get_direction(who.current_position)
        return f'Лестница, ведущая {direction}'
    

    def show_for_unlock(self, who) -> str:
        room = who.current_position
        direction = self.get_direction(room)
        if direction == 'вверх':
            return 'Люк в потолке, закрытый тяжелой крышкой.'
        if direction == 'вниз':
            return 'Квадратный люк в полу, плотно закрытый крышкой.'
        return f'{self:nom}'
    
    
    def unlock(self, who, in_action:bool=False) -> str:
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
        return self.lexemes.get(format, '')

    
    def place(self) -> bool:
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
        self.lexemes = {}
        first_words = randomitem(Ladder._first_decorators)
        second_words = randomitem(Ladder._second_decorators)
        for key in Ladder._lexemes:
            description = f'{first_words[key]} {second_words[key]} {Ladder._lexemes[key]}'
            self.lexemes[key] = description

    
    def show_in_room_as_ladder_down(self) -> str:
        if self.locked:
            return 'В полу имеется квадратный люк, плотно закрытый крышкой.'
        return f'{self:nom} спускается вниз в темноту.'.capitalize()
        

    def show_in_room_as_ladder_up(self) -> str:
        if self.locked:
            return f'{self:nom} поднимается к люку в потолке, закрытому тяжелой крышкой.'.capitalize()
        return f'{self:nom} ведет куда-то вверх.'.capitalize()
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
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
                "condition": "is_locked"
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "presentation": "show_for_unlock"
                },
            "идти": {
                "method": "go",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "presentation": "show_for_unlock",
                "post_process": "check_disturbed_monsters"
                },
        }
    
    
    def check_disturbed_monsters (self, who) -> None:
        who.check_disturbed_monsters()
    
    
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
        if room not in self.rooms or len(self.rooms) < 2:
            return None
        return [another_room for another_room in self.rooms if not another_room == room][0]
    
    
    def is_locked(self, room=None) -> bool:
        return self.locked
    
    
    def get_direction_index(self, room) -> int:
        try:
            index = room.doors.index(self)
        except Exception:
            print(f'Дверь {self} не найдена в комнате {room}.')
            return None
        return index
    
    
    def show_for_unlock(self, who) -> str:
        room = who.current_position
        direction_index = self.get_direction_index(room)
        direction = Door._directions.get(direction_index, False)
        if direction:
            return f'Дверь, ведущая {direction}.'
    
    
    def unlock(self, who, in_action:bool=False) -> str:
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
        names = ['дверь']
        if room:
            index = self.get_direction_index(room)
            direction = Door._directions.get(index, False)
            if direction:
                names.append(direction)
        return names
    
    
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
    
    _decor2 = (
        'с огромными окнами',
        'с полом, застеленным красным старым ковром',
        'с красивой люстрой на потолке',
        'с картинами, изображающими кошечек, на стенах',
        'с унитазом в углу',
        'с паутиной по углам',
        'с птичьей клеткой на подоконнике',
        'с аквариумом во всю стену',
        'со скользким от крови полом',
        'с красивой мебелью',
        'с резными ручками на дверях',
        'с барной стойкой посередине',
        'с длинным столом',
        'с кучей стульев',
        'с выбитыми стеклами в окнах',
        'со стильными светильниками',
        'с деревянным полом',
        'с раковиной у двери',
        'с низким потолком',
        'со скамейками вдоль стен',
        'с белыми стенами',
        'с черными стенами',
        'с грязным полом',
        'с помойным баком у двери',
        'с маленьким балконом',
        'с видом на озеро',
        'с видом на двор',
        'с видом на помойку',
        'со следами борьбы повсюду',
        'со сломанной дверью',
        'с хламом в углу',
        'с приятным интерьером',
        'с пыльными шторами',
        'с треснувшим зеркалом на стене',
        'с древними книгами на полках',
        'с мягким диваном в углу',
        'с яркими граффити на стенах',
        'с фонтаном в центре',
        'с винтажными обоями',
        'с металлическими решетками на окнах',
        'с тихо журчащим аквариумом',
        'с потухшим камином',
        'со странными рисунками на стенах',
        'с руной, начертанной на полу',
        'с кружевными занавесками',
        'с разбитой посудой',
        'с желтой лужей в углу',
        'с петлей, свисающей с потолка',
        'с цветами на подоконнике',
        'с отбитой плиткой на полу',
        'со скрипучим полом',
        'с помойным ведром у двери',
        'с хрустальной люстрой',
        'с заклееными газетами окнами',
        'с головой льва на стене',
    )
    
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
    
    _decor4 = (
        'Пахнет свежей едой.',
        'В воздухе полно пыли.',
        'Похоже, сейчас не лучшее время здесь быть!',
        'По стенам скачут солнечные блики.',
        'В комнате полно мух.',
        'На подоконнике развалился огромный кот.',
        'В канделябрах горят свечи.',
        'Веет могильным холодом.',
        'По комнате гуляют сквозняки.',
        'Паук плетет паутину в углу.',
        'За стеной громко играет музыка.',
        'Где-то неподалеку плачет ребенок.',
        'Из темного угла слышны звуки какой-то возни.',
        'Ветер хлопает створками окна.',
        'Комнату явно давно не проветривали.',
        'Комната заполнена дымом, от которого щиплет глаза.',
        'Повсюду валяется какой-то хлам.',
        'Дождь барабанит по оконному стеклу.',
        'Один из светильников неприятно мигает.',
        'Непонятно откуда слышатся тихие шепоты.',
        'По полу летают сухие листья.',
        'Под окном валяются детские игрушки.',
        'На стене висит окровавленная пила.',
        'Под ногами чавкает какая-то жижа.',
        'Приходится идти по разбитому стеклу.',
        'На стенах висят гобелены с гербами.',
        'На полу разбросаны соломенные циновки.',
        'В комнате пахнет воском и ладаном.',
        'На столе лежат пергаменты и чернильница.',
        'В комнате слышен звон колоколов.',
        'На полу лежит медвежья шкура.',
        'В углу стоит арфа.',
        'На стенах висят охотничьи трофеи.',
        'В комнате пахнет свежим хлебом.',
        'В комнате слышен треск дров в камине.',
        'В углу стоит деревянная статуя.',
        'На стенах висят портреты королей.',
        'В комнате пахнет травами и специями.',
        'На столе лежат шахматные фигуры.',
        'На полу лежит коврик из овечьей шерсти.',
        'В углу стоит деревянная кадка с водой.',
    )
   
    _torch_die = 5
    """
    Кубик, который кидается чтобы определить, горит в комнате факел, или нет 
    (берется выпадение одного конкретного значения).

    """
    
    _stink_levels = {1: 'Немного', 2: 'Сильно', 3: 'Невыносимо'}
    """Уровни вони."""
    
    _secrets = ('унитаз',
                'аквариум',
                'фонтан',
                'хлам',
                'бак',
                'камин',
                'ведро',
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
        self.last_seen_trap:Trap = None
        self.torch = self.set_torch()
        self.decorate()
        self.secret_word = self.get_secret_word()
        self.enter_point = False
        self.generate_actions()

    
    def generate_actions(self):
        self.room_actions = {
            "обыскать": {
                "method": "search",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                },
            "осмотреть": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "map_for_examine"
                },
            "осмотреться": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "map_for_examine"
                },
            "оглядеться": {
                "method": "examine",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "post_process": "map_for_examine"
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
    

    def stink(self, stink_level:int):
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
                self.stink(next_room, stink_level - 1)
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
        return
    
    
    def link_doors(self):
        for door in self.doors:
            door.rooms.append(self)
    
    
    def map_for_examine(self, who):
        self.map()
    
    
    def examine(self, who, in_action:bool=False) -> str:
        if self.light:
            message = self.show_with_light_on(who)
        else:
            message = self.show_with_light_off()
        return message
    
    
    def generate_doors_actions(self):
        for door in self.doors:
            if not door.empty:
                self.action_controller.add_actions(door)
        return
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
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
        if not self.light or roll([Room._torch_die]) != Room._torch_die:
            return False
        new_torch = self.game.weapon_controller.get_random_objects_by_class_name('Torch')
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
        self.decoration1 = randomitem(Room._decor1)
        self.decoration2 = randomitem(Room._decor2)
        self.decoration3 = randomitem(Room._decor3)
        self.decoration4 = randomitem(Room._decor4)
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
        torch_text = ', освещеннуб факелом' if self.torch else ''
        message.append(f'{player.name} попадает в {decoration} '
                       f'комнату {self.decoration2}{torch_text}. {self.decoration4}')
        message.extend(self.show_furniture())
        message.extend(self.get_ladders_text())
        if self.trader:
            message.append(self.trader.show())
        message += self.show_corpses()
        message.extend(monster_text)
        message.append(self.get_stink_text())
        return message
        

    def get_ladders_text(self) -> list[str]:
        message = []
        if self.ladder_down:
            message.append(self.ladder_down.show_in_room_as_ladder_down())
        if self.ladder_up:
            message.append(self.ladder_up.show_in_room_as_ladder_up())
        return message
    
    
    def get_monster_text_for_show(self) -> list[str]:
        monsters = self.monsters()
        message = []
        if not monsters:
            return ['Не видно ничего интересного.']
        for monster in monsters:
            message.append(f'{randomitem(Room._decor3)} {monster.state} {monster.name}.')
        return message
    
    
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
            return self.get_monsters_symbol()
        if self.trader:
            return '₽'
        return ' '
    
    
    def get_number_of_monsters(self) -> int:
        return len(self.floor.monsters_in_rooms[self])
    
    
    def get_monsters_symbol(self) -> str:
        number_of_monsters = self.get_number_of_monsters()
        if number_of_monsters == 1:
            return '~'
        return '≈'
        
    
    def get_second_line_for_plan(self) -> str:
        if self.ladder_up:
            return '║  #║'
        return '║   ║'
    
    
    def get_fourth_line_for_plan(self) -> str:
        if self.ladder_down:
            return '║#  ║'
        return '║   ║'
    
    def lock(self):
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
        if self.furniture:
            furniture_list = [f for f in self.furniture if not f.locked]
            if furniture_list:
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
        message = ['От неловкого прикосновения в ловушка начинает противно щелкать, а потом взрывается.']
        while True:
            if not types:
                message.append(f'{target.name} настолько {target.g("некчемен", "некчемна")},' 
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
        return ['Ловушка тихонько щелкает и больше не издает ни звука. Похоже, она больше не опасна.']
    
    
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