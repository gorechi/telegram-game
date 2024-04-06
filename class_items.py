from math import floor, sqrt
from random import randint as dice
from typing import Any, NoReturn

from class_basic import *
from functions import howmany, randomitem, tprint, roll, pprint


class Rune:
    
    """ Класс Руна. """
    
    _elements = (1, 3, 7, 12)
    
    _lexemes = {
            "nom": "руна",
            "accus": "руну",
            "gen": "руны",
            "dat": "руне",
            "prep": "руне",
            "inst": "руной"
            }
    
    _poison_probability = (3)
    """
    Вероятность того, что руна будет отравленной. 
    Цифра указывает на количество граней кубика, который надо кинуть. 
    Если 1 - руна отравлена.

    """

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

    _glowing_elements = (1, 2, 4)
    """Массив стихий, которые заставляют оружие светиться в темноте"""

    _base_price = 15
    
    _base_price_die = (15)
    
    _poison_price_modifier = (5)
    
    def __init__(self, game):
        self.game = game
        self.damage = 4 - floor(sqrt(dice(1, 15)))
        self.defence = 3 - floor(sqrt(dice(1, 8)))
        self.element = randomitem(Rune._elements)
        self.can_use_in_fight = False
        self.name = 'руна'
        self.lexemes = self.generate_lexemes()
        self.description = f'{self.name} {Rune._elements_dictionary[self.element]}'
        self.empty = False
        self.base_price = self.define_base_price()
        self.check_if_poisoned()
        
         
    def generate_lexemes(self) -> dict:
        lexemes = {}
        for key in Rune._lexemes:
            lexemes[key] = f'{Rune._lexemes[key]} {Rune._elements_dictionary[self.element]}'
        return lexemes
    
    
    def __str__(self) -> str:
        return f'{self.name} {Rune._elements_dictionary[self.element]} - ' \
            f'урон + {str(self.damage)} или защита + {str(self.defence)}'

      
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['руна', 'руну']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def define_base_price(self) -> int:
        return Rune._base_price + roll(Rune._base_price_die)

    
    def check_if_poisoned(self) -> NoReturn:    
        
        """ Метод определяет, ядовитая руна, или нет. """
        
        if roll(Rune._poison_probability) == 1:
            self.poison = True
            self.description = f'ядовитая {self.description}'
            self.base_price += roll(Rune._poison_price_modifier)
        else:
            self.poison = False

    
    def on_create(self) -> Any:
        
        """ Метод вызывается после создания экземпляра класса. Ничего не делает. """
        
        return True

    
    def place(self, castle, room=None) -> bool:
        
        """ Метод раскидывания рун по замку. """
        
        rooms_with_secrets = castle.secret_rooms()
        if not room:
            rooms = castle.plan
            room = randomitem(rooms)
        if room in rooms_with_secrets:
            room.secret_loot.add(self)
        elif room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    
    def element(self) -> int:
        
        """ Метод возвращает элемент руны в виде целого числа. """
        
        return int(self.element)

    
    def take(self, who) -> NoReturn:
        
        """ Метод вызывается когда кто-то забирает руну себе. """
        
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self.lexemes["accus"]} себе.')

    
    def show(self) -> str:
        
        """ Метод возвращает описание руны в виде строки. """
        
        return f'{self.description} - урон + {str(self.damage)} или защита + {str(self.defence)}'.capitalize()

    
    def use(self, who_is_using, in_action:bool=False) -> str:
        
        """ 
        Метод использования руны. Возвращает строку ответа и ничего не делает 
        так как руну использовать нельзя.
        
        """
        
        tprint(
            self.game, f'{who_is_using.name} не знает, как использовать такие штуки.')


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
    
    _max_quantity = 10
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
        
 
    def check_name(self, message:str) -> bool:
        return message.lower() in ['спички', 'коробок']
    
    
    def get_quantity(self) -> int:
        return roll([Matches._max_quantity])

    
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
            tprint(self.game, f'{who.name} забирает {self.lexemes["accus"]} себе.')
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
            tprint(self.game, f'От страха пальцы {who_is_using.g(["героя", "героини"])} не слушаются. Спичка ломается и падает на пол.')    
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

    def __init__(self, game):
        self.game = game
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
        self.description = 'Карта, показывающая расположение комнат замка'
        self.floor = None

    
    def check_name(self, message:str) -> bool:
        return message.lower() in ['карта', 'карту']
    
    
    def place(self, floor, room=None) -> bool:
        
        """ Метод размещения карты в замке. """
        
        if not room:
            rooms = floor.plan
            room = randomitem(rooms)
        if room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
        self.floor = floor
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
                line1 += f'  {symbol}  {room.doors[1].vertical_symbol()}'
                line2 += f'==={room.doors[2].horizontal_symbol()}=='
            text.append(line1)
            text.append('║' + '     ║' * rooms)
            text.append(line2 + '=')
        pprint(game, text, rooms*Map._width_coefficient, rows*Map._height_coefficient)

    
    def take(self, who) -> NoReturn:
        
        """ Метод вызывается когда кто-то забирает карту себе. """
        
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self.lexemes["accus"]} себе.')


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


class Book:
    
    _names = {
        "nom": "книга",
        "accus": "книгу",
        "gen": "книги",
        "dat": "книге",
        "prep": "книге",
        "inst": "книгой"
      }
    
    _descriptions = (
        {
            "nom": "Старая",
            "accus": "Старую",
            "gen": "Старой",
            "dat": "Старой",
            "prep": "Старой",
            "inst": "Старой"
          },
          {
            "nom": "Древняя",
            "accus": "Древнюю",
            "gen": "Древней",
            "dat": "Древней",
            "prep": "Древней",
            "inst": "Древней"
          },
          {
            "nom": "Пыльная",
            "accus": "Пыльную",
            "gen": "Пыльной",
            "dat": "Пыльной",
            "prep": "Пыльной",
            "inst": "Пыльной"
          },
          {
            "nom": "Зачитанная",
            "accus": "Зачитанную",
            "gen": "Зачитанной",
            "dat": "Зачитанной",
            "prep": "Зачитанной",
            "inst": "Зачитанной"
          },
          {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой"
          },
          {
            "nom": "Потрепанная",
            "accus": "Потрепанную",
            "gen": "Потрепанной",
            "dat": "Потрепанной",
            "prep": "Потрепанной",
            "inst": "Потрепанной"
          },
          {
            "nom": "Красивая",
            "accus": "Красивую",
            "gen": "Красивой",
            "dat": "Красивой",
            "prep": "Красивой",
            "inst": "Красивой"
          },
          {
            "nom": "Большая",
            "accus": "Большую",
            "gen": "Большой",
            "dat": "Большой",
            "prep": "Большой",
            "inst": "Большой"
          }
    )
    
    _texts = (
        [0, "Книга повествует о временах мастеров-фехтовальщиков. Тогда величайшим достижением считалось заколоть соперника в честном поединке на шпагах."],
        [0, "В книге во всех красках описывается история двух друзей-авантюристов, которые берутся за любое, даже самое опасное дело. Попав в беду они всегда чудом избегают гибели благодаря их умениям в бою на шпагах."],
        [0, "Это история о молодой девушке, отец которой считает, что она добьется всего сама, если будет обладать характером и умением фехтовать. Уроки отца девушки описаны подробно и основательно, что позволяет читателю почерпнуть много нового."],
        [1, "Книга рассказывает о злобных пиратах под предводительством знаменитого капитана Рыжая (с проседью) Борода, который был великим мастером сабли."],
        [1, "Повествование в книге ведется от лица боцмана пиратской шхуны, бороздившей южные моря. Команда корабля не гнушалась любой добычи и нападала на любые проходящие мимо суда. Не сгинуть в морской пучине главному герою помогает его мастерское владение саблей."],
        [1, "Автор книги провел несколько лет в пиратском логове в качестве врача. Наблюдая за жизнью пиратов, за их тренировками, он составил подробное описание боевого стиля пиратских воинов."],
        [2, "В книге описывается жизнь вождя викингов Олафа, который ходил в походы на соседние земли и прославился тем, что дрался только своей любимой дубиной."],
        [2, "Книга представляет собой вольное изложение легенд северных народов с особым упором на ратные подвиги героев и их умения в применении ударного оружия."],
        [2, "История кузница в норвежской деревне начинается мирно и размеренно, но резко превращается в абсолютный кошмар после эпизода убийства его семьи воинами соседнего племени. Бросив кузницу и вооружившись лишь своим молотом герой отправляется мстить."],
        [3, "Книга рассказывает про команду взломщиков сейфов, которая сталкивается с самым сложным вызовом в своей карьере, пытаясь проникнуть в неприступное хранилище, охраняемое страшными ловушками."],
        [3, "Книга описывает мир, где заклинания могут открывать любые двери. Группа храбрых плутов бросает вызов забытому замку, полному магических загадок и смертельных ловушек, чтобы обнаружить сокровище, способное изменить судьбы."],
        [3, "В книге описывается как в зачарованном лесу, где каждое дерево и камень хранит свои тайны, молодой вор предпринимает опасное путешествие к сердцу древнего лабиринта, полного мистических ловушек и неизведанных опасностей, в поисках затерянного сокровища великих магов."]
    )
    
    _decorations = (
        "о мушкетерах",
        "о пиратах",
        "о викингах",
        "о взломщиках"
    )
    
    _weapon_types = (
        "колющее",
        "рубящее",
        "ударное",
        0
    )
    
    _base_price = 7
    
    _base_price_die = [8]
    
    def __init__(self, game):
        self.game = game
        self.empty = False
        self.type = roll([4]) - 1
        self.create_description()
        self.name = self.lexemes['nom']
        available_texts = [i for i in Book._texts if i[0] == self.type]
        self.text = randomitem(available_texts)
        self.weapon_type = Book._weapon_types[self.type]
        self.can_use_in_fight = False
        self.base_price = self.define_base_price()

    
    def __str__(self):
        return self.name
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['книга', 'книгу', 'книжка', 'книжку']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
            
    
    def define_base_price(self) -> int:
        return Book._base_price + roll(Book._base_price_die)
               
   
    def create_description(self):
        description_dict = randomitem(Book._descriptions)
        name_dict = Book._names
        self.lexemes = {}
        for lexeme in name_dict:
            self.lexemes[lexeme] =f'{description_dict[lexeme]} {name_dict[lexeme]} {Book._decorations[self.type]}'
        return True
        
    
    def get_mastery_string(self, who):
        return f'{who.name} теперь немного лучше знает, как использовать {self.weapon_type} оружие.'
    
    
    def place(self, floor, room=None):
        if not room:
            room = floor.get_random_room_with_furniture()
        furniture = randomitem(room.furniture)
        furniture.put(self)
        return True
    
    
    def show(self):
        return self.lexemes['nom']
    
    
    def use(self, who_using, in_action:bool=False):
        if in_action:
            tprint(self.game, 'Сейчас абсолютно не подходящее время для чтения.')
            return False
        else:
            return who_using.read(self)
    
    
    def take(self, who):
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self.lexemes["accus"]} себе.')
            return True
        return False
