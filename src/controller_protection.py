from dataclasses import dataclass

from src.class_protection import Armor, Shield, Protection
from src.class_controller import Controller

class ProtectionController(Controller):
    """Класс для управления доспехами."""

    @dataclass
    class Template():
        class_name: str
        protection_type: str
        gender: int
        name: str
        lexemes: dict
        protection: dict
        enchantable: bool
        actions: list
        
    _classes = {
        "Armor": Armor,
        "Shield": Shield
    }

    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/protection.json')
        self.all_objects = []