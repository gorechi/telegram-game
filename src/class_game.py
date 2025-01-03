from src.class_castle import Floor
from src.class_book import Book
from src.class_hero import Hero
from src.class_items import Key
from src.class_backpack import Backpack
from src.controller_monsters import MonstersController
from src.controller_protection import ProtectionController
from src.controller_weapon import WeaponController
from src.controller_heroes import HeroController
from src.controller_books import BooksController
from src.controller_potions import PotionsController
from src.controller_runes import RunesController
from src.controller_furniture import FurnitureController


class Empty():
    
    """
    Класс пустого объекта. Используется вместо объектов игры, 
    таких, как мечи, щиты, защита, монстры, чтобы обозначить, что их нет.
    
    """
    
    def __init__(self):
        self.empty = True
        self.frightening = False
        self.aggressive = False
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
            'торговец': 2,
            'лестницы': 2,
            'ловушка': 3}
        },
        2: {
        'rows': 3, 
        'rooms': 3,
        'traps_difficulty': 4, 
        'how_many': {
            'монстры': 5,
            'оружие': 3,
            'щит': 2,
            'доспех': 2,
            'зелье': 5,
            'мебель': 6,
            'книга': 2,
            'очаг': 1,
            'руна': 3,
            'торговец': 1,
            'лестницы': 0,
            'ловушка': 2}
        }
    }
    """Размеры этажей замка. Каждый объект - это этаж замка."""
  
    _traders_update_counter = 30
    

    def __init__(self, chat_id:str, bot):
        self.empty_thing = Empty()
        self.selected_item = self.empty_thing
        self.chat_id = chat_id
        self.bot = bot
        self.monsters_controller = MonstersController(self)
        self.protection_controller = ProtectionController(self)
        self.weapon_controller = WeaponController(self)
        self.hero_controller = HeroController(self)
        self.books_controller = BooksController(self)
        self.potions_controller = PotionsController(self)
        self.runes_controller = RunesController(self)
        self.furniture_controller = FurnitureController(self)
        self.all_corpses = []
        self.all_traders = []
        self.no_weapon = self.weapon_controller.get_empty_object_by_class_name('Weapon')
        self.no_shield = self.protection_controller.get_empty_object_by_class_name('Shield')
        self.no_armor = self.protection_controller.get_empty_object_by_class_name('Armor')
        self.no_backpack = Backpack(self, no_backpack=True)
        self.castle_floors = self.create_floors()
        self.create_ladders()
        self.current_floor = self.castle_floors[0]
        self.player = self.hero_controller.get_random_object_by_filters()
        self.player.place(self.current_floor.plan[0])
        new_key = Key(self)
        self.player.backpack + new_key
        self.game_is_on = False
        self.traders_update_counter = Game._traders_update_counter
        

    def create_ladders(self):
        for floor in self.castle_floors[:-1]:
            floor.create_ladders()
            

    def check_endgame(self) -> bool:
        if True in [
            self.monsters_controller.check_endgame()
            ]:
            return True
        return False
    
    
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
        
    
    def create_floors(self) -> list[Floor]:
        
        """Метод создания этажей замка"""
        
        floors = []
        for i in Game._castle_floors_sizes:
            floor = Floor(self, 
                          floor_number = i, 
                          data = Game._castle_floors_sizes[i]
                          )
            floors.append(floor)
        return floors
    
    
    def __del__ (self):
        print("=" * 40)
        print('Игра удалена')
        print("=" * 40)
     
    
    def test(self, hero:Hero):
        book1 = Book.random_book(self)
        book2 = Book.random_book(self)
        self.player.backpack + book1
        self.player.backpack + book2
        print('Тестирование чтения книг')
