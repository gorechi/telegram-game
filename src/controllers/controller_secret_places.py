from dataclasses import dataclass
from src.functions.functions import randomitem

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
        self.all_objects = list()
    
    
    def additional_actions(self, secret_place) -> bool:
        """
        Функция выполняет дополнительные действия по настройке секрета.
        """
        self.add_loot(secret_place)
        return True
    

    def add_loot(self, secret_place: SecretPlace):
        """
        Функция добавляет лут в секретное место.
        """
        new_loot = Loot(self.game)
        secret_place.loot = new_loot

    
    def add_trap(self, secret_place: SecretPlace):
        """
        Функция добавляет ловушку в секретное место.
        """
        new_trap = self.game.traps_controller.get_random_object_by_filters()
        secret_place.trap = new_trap

    
    def get_random_secret_by_floor(self, floor) -> SecretPlace:
        """
        Функция возвращает случайное секретное место на этаже.
        """
        secrets_on_floor = [secret for secret in self.all_objects if secret.floor == floor]
        if secrets_on_floor:
            return randomitem(secrets_on_floor)
        return False
    

    def get_random_secret_by_room(self, room) -> SecretPlace:
        """
        Функция возвращает случайное секретное место в комнате.
        """
        secrets_in_room = [secret for secret in self.all_objects if secret.room == room]
        if secrets_in_room:
            return randomitem(secrets_in_room)
        return False