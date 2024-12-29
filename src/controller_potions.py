from dataclasses import dataclass

from src.class_potions import Potion, HealPotion, HealthPotion, StrengtheningPotion, StrengthPotion, IntelligencePotion, EnlightmentPotion, DexterityPotion, EvasionPotion, Antidote
from src.class_controller import Controller
from src.functions.functions import randomitem

class BookController(Controller):
    """Класс для управления героями."""

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
        "Potion": Potion,
        "HealPotion": HealPotion,
        "HealthPotion": HealthPotion,
        "StrengtheningPotion": StrengtheningPotion,
        "StrengthPotion": StrengthPotion,
        "IntelligencePotion": IntelligencePotion,
        "EnlightmentPotion": EnlightmentPotion,
        "DexterityPotion": DexterityPotion,
        "EvasionPotion": EvasionPotion,
        "Antidote": Antidote
    }
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/potions.json')
        self.all_objects = []
    
    
    def additional_actions(self, object) -> bool:
        return True