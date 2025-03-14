from dataclasses import dataclass

from src.class_secret_place import SecretPlace
from src.class_controller import Controller
from src.class_basic import Loot

class SecretPlacesController(Controller):
    """Класс для управления секретами."""

    @dataclass
    class Template():
        class_name: str
        name: str
        lexemes: dict
    
    _classes = {
        "SecretPlace": SecretPlace,
    }
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/secrets.json')
        self.all_objects = []
    
    
    def additional_actions(self, secret_place) -> bool:
        self.add_loot(secret_place)
        return True
    

    def add_loot(self, secret_place: SecretPlace):
        new_loot = Loot(self.game)
        secret_place.loot = new_loot

    
    def add_trap(self, secret_place: SecretPlace):
        new_trap = self.game.traps_controller.get_random_object_by_filters()
        secret_place.trap = new_trap