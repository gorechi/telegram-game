import json

from class_castle import Floor, Ladder
from class_book import Book, ThrustingWeaponBook, CuttingWeaponBook, BluntgWeaponBook, TrapsBook, WisdomBook
from class_hero import Hero
from class_items import Key, Map, Matches, Rune, Spell
from class_potions import Potion, HealPotion, HealthPotion, StrengtheningPotion, StrengthPotion, IntelligencePotion, EnlightmentPotion, DexterityPotion, EvasionPotion, Antidote
from class_monsters import Berserk, Monster, Plant, Vampire, Corpse, Animal, WalkingDead, Skeleton
from class_protection import Armor, Shield
from class_room import Furniture
from class_weapon import Weapon
from class_allies import Trader, Scribe, RuneMerchant, PotionsMerchant
from class_backpack import Backpack
from functions import randomitem


class Empty():
    
    """
    Класс пустого объекта. Используется вместо объектов игры, 
    таких, как мечи, щиты, защита, монстры, чтобы обозначить, что их нет.
    
    """
    
    def __init__(self):
        self.empty = True
        self.frightening = False
        self.agressive = False
        self.locked = False
    
    def __bool__(self):
        return False


class Game():
    
    """
    Класс игры. 
    Хранит состояния игры. 
    Содержит методы создания объектов игры, а также методы обработки комманд игрока.
    
    """
        
    _castle_floors_sizes = {
        1: {
        'rows': 5, 
        'rooms': 5,
        'traps_difficulty': 4, 
        'how_many': {
            'монстры': 10,
            'оружие': 10,
            'щит': 5,
            'доспех': 5,
            'зелье': 10,
            'мебель': 10,
            'книга': 5,
            'очаг': 2,
            'руна': 10,
            'лестницы': 2,
            'ловушка': 3}
        },
        2: {
        'rows': 3, 
        'rooms': 3,
        'traps_difficulty': 4, 
        'how_many': {
            'монстры': 9,
            'оружие': 3,
            'щит': 2,
            'доспех': 2,
            'зелье': 5,
            'мебель': 6,
            'книга': 2,
            'очаг': 1,
            'руна': 3,
            'лестницы': 0,
            'ловушка': 2}
        }
    }
    """Размеры этажей замка. Каждый подмассив - это этаж замка."""
    
    _how_many_traders = 1
    """Сколько торговцев в игре"""

    _traders_update_counter = 30
    
    _floor_monsters = {
        1: ['вампир', 'растение'],
        2: ['вампир', 'растение']
    }
    """Словарь типов монстров для некоторых этажей"""


    def __init__(self, chat_id:str, bot, hero:Hero=None):
        self.classes = { 
            'монстр': Monster,
            'мертвец': WalkingDead,
            'этаж': Floor,
            'лестница': Ladder,
            'герой': Hero,
            'оружие': Weapon,
            'щит': Shield,
            'доспех': Armor,
            'мебель': Furniture,
            'вампир': Vampire,
            'берсерк': Berserk,
            'растение': Plant,
            'животное': Animal,
            'скелет': Skeleton,
            'труп': Corpse,
            'ключ': Key,
            'карта': Map,
            'спички': Matches,
            'книга': Book,
            'книга о колющем оружии': ThrustingWeaponBook,
            'книга о рубящем оружии': CuttingWeaponBook,
            'книга об ударном оружии': BluntgWeaponBook,
            'книга о ловушках': TrapsBook,
            'книга об ученых': WisdomBook,
            'зелье': Potion,
            'руна': Rune,
            'заклинание': Spell,
            'торговец': Trader,
            'книжник': Scribe,
            'торговец рунами': RuneMerchant,
            'торговец заклинаниями': PotionsMerchant,
            'рюкзак': Backpack,
            'зелье исцеления': HealPotion,
            'зелье здоровья': HealthPotion,
            'зелье силы': StrengthPotion,
            'зелье усиления': StrengtheningPotion,
            'зелье ловкости': DexterityPotion,
            'зелье увертливости': EvasionPotion,
            'зелье ума': IntelligencePotion,
            'зелье просветления': EnlightmentPotion,
            'противоядие': Antidote,
            }
        self.empty_thing = Empty()
        self.how_many_monsters = 0
        self.selected_item = self.empty_thing
        self.chat_id = chat_id
        self.bot = bot
        self.all_corpses = []
        self.all_traders = []
        self.no_weapon = Weapon(self, empty=True)
        self.no_shield = Shield(self, empty=True)
        self.no_armor = Armor(self, empty=True)
        self.no_backpack = Backpack(self, no_backpack=True)
        self.castle_floors = self.create_floors()
        self.create_ladders()
        self.current_floor = self.castle_floors[0]
        self.player = self.check_hero(hero=hero)
        self.player.place(self.current_floor.plan[0])
        new_key = Key(self)
        self.player.backpack + new_key
        self.game_is_on = False
        self.traders_update_counter = Game._traders_update_counter
        

    def create_ladders(self):
        for floor in self.castle_floors[:-1]:
            floor.create_ladders()
            

    def get_floor_by_number(self, number:int) -> Floor:
        return next((floor for floor in self.castle_floors if floor.floor_number == number), None)
    
    
    def trigger_on_movement(self):
        """Метод обрабатывает событие движения героя"""
        self.raise_dead()
        self.check_traders_update()

    
    def check_traders_update(self) -> bool:
        if self.traders_update_counter > 0:
            self.traders_update_counter -= 1
            return False
        self.update_traders()
        return True
    
    
    def update_traders(self) -> bool:
        for trader in self.all_traders:
            trader.get_goods()
        return True
    
    
    def raise_dead(self):
        """Метод воскрешения мертвецов"""
        
        for corpse in self.all_corpses: 
            if corpse.can_resurrect:
                corpse.try_to_rise()
    
    
    def check_hero(self, hero:Hero) -> Hero:
        
        """
        Метод проверяет, передан ли в игру герой. 
        Если не передан, то создает нового героя с настройками по умолчанию.
        
        """
        
        if not hero:
            hero = self.create_objects_from_json('hero.json')[0]
        return hero
    
    
    def create_floors(self) -> list[Floor]:
        
        """Метод создания этажей замка"""
        
        floors = []
        for i in Game._castle_floors_sizes:
            monsters_classes = Game._floor_monsters.get(i, None)
            floor = Floor(self, 
                          floor_number = i, 
                          data = Game._castle_floors_sizes[i], 
                          monsters_classes = monsters_classes
                          )
            floors.append(floor)
        return floors
    
    
    def __del__ (self):
        print("=" * 40)
        print('Игра удалена')
        print("=" * 40)

    
    def create_objects_from_json(self, 
                                 file:str, 
                                 random:bool=False, 
                                 how_many:int=None, 
                                 obj_classes:list[str]=None, 
                                 floor:int=None
                                 ) -> list:
        
        """
        Метод создает список объектов из файла JSON. 
        Получает на вход следующие параметры:
        - file - имя файла, содержащего данные;
        - random - нужно ли создавать случайный набор объектов из прочитанных данных?
        - how_many - сколько объектов нужно прочитать из файла и вернуть?
        - obj_class - объекты какого класса нужно начитывать?
        - floor - некоторые объекты могут появиться только на определенном этаже и выше. 
        Параметр указывает, объекты какого этажа нужно начитывать.
        
        Очевидно, что передавать random без how_many не имеет смысла.
        
        """
        
        objects = []
        with open(file, encoding='utf-8') as read_data:
            parsed_data = json.load(read_data)
        if not parsed_data:
            raise FileExistsError(f'Не удалось прочитать данные из файла {file}')
        if obj_classes and isinstance(obj_classes, list):
            parsed_data = [i for i in parsed_data if i['class'] in obj_classes]
        if floor and isinstance(floor, int):
            parsed_data = [i for i in parsed_data if int(i.get('floor')) >= floor]
        if random and how_many:
            for _ in range(how_many):
                i = randomitem(parsed_data)
                new_game_object = self.object_from_json(json_object=i)
                objects.append(new_game_object)
            return objects
        for i in parsed_data:
            new_game_object = self.object_from_json(json_object=i)
            objects.append(new_game_object)
        return objects
    
          
    def create_random_weapon(self, how_many:int=1, weapon_type:str=None) -> Weapon | list[Weapon]:
        """
        Метод создания случайного оружия.
        
        """
        
        objects = []
        with open('weapon.json', encoding='utf-8') as read_data:
            parsed_data = json.load(read_data)
        if weapon_type:
            parsed_data = [i for i in parsed_data if i['type'] == weapon_type]
        for _ in range(how_many):
            i = randomitem(parsed_data)
            new_game_object = self.object_from_json(json_object=i)
            objects.append(new_game_object)
        if len(objects) == 1:
            return objects[0]
        return objects
    
    
    def object_from_json(self, json_object:object) -> object:
        
        """Метод создает один игровой объект из объекта JSON."""
        
        new_object = self.classes[json_object['class']](self)
        for param in json_object:
            vars(new_object)[param] = json_object[param]
        new_object.on_create()
        return new_object
        
    
    def monsters(self):
        return self.how_many_monsters
    
    
    def test(self, hero:Hero):
        """ floor = self.current_floor
        room = floor.plan[1]
        new_monster1 = Monster(
            self,
            name = 'Монстр1',
            lexemes = {
                "nom": "монстр1",
                "accus": "монстра1",
                "gen": "монстра1",
                "dat": "монстру1",
                "prep": "монстре1",
                "inst": "моснтром1"
            }
        )
        new_monster2 = Monster(
            self,
            name = 'Монстр2',
            lexemes = {
                "nom": "монстр2",
                "accus": "монстра2",
                "gen": "монстра2",
                "dat": "монстру2",
                "prep": "монстре2",
                "inst": "моснтром2"
            }
        )
        new_monster3 = Monster(
            self,
            name = 'Монстр3',
            lexemes = {
                "nom": "монстр3",
                "accus": "монстра3",
                "gen": "монстра3",
                "dat": "монстру3",
                "prep": "монстре3",
                "inst": "моснтром3"
            }
        )
        new_monster1.initiative = 100
        new_monster2.initiative = 100
        new_monster3.initiative = 100
        new_monster1.place(floor=floor, room_to_place=room)
        new_monster2.place(floor=floor, room_to_place=room)
        new_monster3.place(floor=floor, room_to_place=room)
        new_fight = Fight(
            game=self, 
            hero=None, 
            who_started=new_monster1, 
            fighters=[new_monster1, new_monster2, new_monster3]
            )
        new_fight.start()
        return None """
        book1 = Book.random_book(self)
        book2 = Book.random_book(self)
        self.player.backpack + book1
        self.player.backpack + book2
        print('Тестирование чтения книг')