from src.class_backpack import Backpack
from src.controllers.controller_monsters import MonstersController
from src.controllers.controller_protection import ProtectionController
from src.controllers.controller_weapon import WeaponController
from src.controllers.controller_heroes import HeroController
from src.controllers.controller_books import BooksController
from src.controllers.controller_potions import PotionsController
from src.controllers.controller_runes import RunesController
from src.controllers.controller_furniture import FurnitureController
from src.controllers.controller_floors import FloorsController


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
        self.floors_controller = FloorsController(self)
        self.all_corpses = []
        self.all_traders = []
        self.no_weapon = self.weapon_controller.get_empty_object_by_class_name('Weapon')
        self.no_shield = self.protection_controller.get_empty_object_by_class_name('Shield')
        self.no_armor = self.protection_controller.get_empty_object_by_class_name('Armor')
        self.no_backpack = Backpack(self, no_backpack=True)
        self.castle_floors = self.floors_controller.create_castle()
        self.current_floor = self.castle_floors[0]
        self.player = self.hero_controller.get_random_object_by_filters()
        self.player.place(self.current_floor.plan[0])
        self.game_is_on = False
        self.traders_update_counter = Game._traders_update_counter
        

    def check_endgame(self) -> bool:
        if True in [
            self.monsters_controller.check_endgame()
            ]:
            return True
        return False
    
    
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
        
    
    def __del__ (self):
        print("=" * 40)
        print('Игра удалена')
        print("=" * 40)
     
    
    def test(self, hero):
        book1 = self.books_controller.get_random_object_by_filters()
        book2 = self.books_controller.get_random_object_by_filters()
        book1.take(self.player)
        book2.take(self.player)
        self.current_floor.plan[0].light = False
