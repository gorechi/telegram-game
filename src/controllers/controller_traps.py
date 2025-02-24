from dataclasses import dataclass

from src.class_trap import Trap
from src.class_controller import Controller

class PotionsController(Controller):
    """Класс для управления ловушками."""

    @dataclass
    class Template():
        class_name: str
        can_use_in_fight: bool
        name: str
        effect: int
        description: str
        lexemes: dict
        base_price: int
              
    
    _classes = {
        "Trap": Trap,
    }
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/potions.json')
        self.all_objects = []
    
    
    def additional_actions(self, object) -> bool:
        return True