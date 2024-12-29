from dataclasses import dataclass

from src.class_furniture import Furniture
from src.class_controller import Controller
from src.class_dice import Dice
from src.class_basic import Money, Loot
from src.class_room import Trap
from src.functions.functions import randomitem

class FurnitureController(Controller):
    """Класс для управления героями."""

    @dataclass
    class Template():
        class_name: str
        furniture_type: int
        name: str
        lexemes: dict
        empty_text: str
        lockable: bool
        can_hide: bool
        can_contain_weapon: bool
        can_rest: bool
        states: list
        wheres: list
        can_contain_trap: bool
              
    
    _classes = {
        "Furniture": Furniture
    }
    
    _money_probability_dice = Dice([2])
    
    _money_dice = Dice([50])
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/furniture.json')
        self.all_objects = []
    
    
    def additional_actions(self, item) -> bool:
        self.add_loot(item)
        self.add_trap(item)
        self.generate_state(item)
        self.generate_where(item)
        self.add_money(item)
        return True
    
    
    def generate_state(self, furniture: Furniture):
        furniture.state = randomitem(furniture.states)
        
        
    def generate_where(self, furniture: Furniture):
        furniture.where = randomitem(furniture.wheres)
        
        
    def add_money(self, furniture: Furniture):
        if FurnitureController._money_probability_dice.roll() == 1:
            new_money = Money(self.game, FurnitureController._money_dice.roll())
            furniture.loot.pile.append(new_money)
            
    
    def add_loot(self, furniture: Furniture):
        new_loot = Loot(self.game)
        furniture.loot = new_loot
        
    
    def add_trap(self, furniture: Furniture):
        new_trap = Trap(self.game, furniture)
        furniture.trap = new_trap