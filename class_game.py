import json

from class_castle import Floor
from class_hero import Hero
from class_items import Book, Key, Map, Matches, Rune, Spell
from class_potions import Potion, HealPotion, HealthPotion, StrengtheningPotion, StrengthPotion, IntelligencePotion, EnlightmentPotion, DexterityPotion, EvasionPotion, Antidote
from class_monsters import Berserk, Monster, Plant, Shapeshifter, Vampire, Corpse, Animal, WalkingDead
from class_protection import Armor, Shield
from class_room import Furniture
from class_weapon import Weapon
from class_allies import Trader, Scribe
from class_backpack import Backpack
from functions import randomitem, tprint


class Empty():
    
    """
    Класс пустого объекта. Используется вместо объектов игры, 
    таких, как мечи, щиты, защита, монстры, чтобы обозначить, что их нет.
    
    """
    
    def __init__(self):
        self.empty = True
        self.frightening = False
        self.agressive = False


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
            'ловушка': 3}
        }
    }
    """Размеры этажей замка. Каждый подмассив - это этаж замка."""
    
    _how_many_traders = 1
    """Сколько торговцев в игре"""



    def __init__(self, chat_id:str, bot, hero:Hero=None):
        self.classes = { 
            'монстр': Monster,
            'мертвец': WalkingDead,
            'герой': Hero,
            'оружие': Weapon,
            'щит': Shield,
            'доспех': Armor,
            'притворщик': Shapeshifter,
            'мебель': Furniture,
            'вампир': Vampire,
            'берсерк': Berserk,
            'растение': Plant,
            'животное': Animal,
            'труп': Corpse,
            'ключ': Key,
            'карта': Map,
            'спички': Matches,
            'книга': Book,
            'зелье': Potion,
            'руна': Rune,
            'заклинание': Spell,
            'торговец': Trader,
            'книжник': Scribe,
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
        self.no_weapon = Weapon(self, empty=True)
        self.no_shield = Shield(self, empty=True)
        self.no_armor = Armor(self, empty=True)
        self.no_backpack = Backpack(self, no_backpack=True)
        self.castle_floors = self.create_floors()
        self.current_floor = self.castle_floors[0]
        self.player = self.check_hero(hero=hero)
        self.player.current_position = self.current_floor.plan[0]
        self.current_floor.plan[0].visited = '+'
        new_key = Key(self)
        self.player.backpack + new_key
        self.game_is_on = False
        

    def trigger_on_movement(self):
        """Метод обрабатывает событие движения героя"""
        
        self.raise_dead()
        
    
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
            floor = Floor(self, i, Game._castle_floors_sizes[i])
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
                                 obj_class:str=None, 
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
        if obj_class and isinstance(obj_class, str):
            parsed_data = [i for i in parsed_data if i['class'] == obj_class]
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
        floor = self.current_floor
        room = floor.plan[0]
        new_trader = Scribe(self, floor)
        new_trader.place(room)
        hero.money += 100
        return None
            