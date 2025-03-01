from dataclasses import dataclass
from src.functions.functions import randomitem

from src.class_trap import Trap
from src.class_controller import Controller

class TrapsController(Controller):
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

    detection_texts = [
        'Сбоку отчетливо виден какой-то странный механизм.',
        'Тоненький волосок прикреплен к крышке.',
        'Изнутри слышно какое-то странное пощелкивание.',
        'В щели между крышкой и корпусом видно натянутую нитку.',
        'Кто-то явно что-то делал с крышкой - щель с одной стороны шире, чем с другой.'
    ]
    
    _classes = {
        "Trap": Trap,
    }
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/traps.json')
        self.all_objects = []
    
    
    def additional_actions(self, trap) -> bool:
        self.set_difficulty(trap)
        self.set_detection_text(trap)
        return True
    

    def set_difficulty(self, trap):
        return
    

    def get_detection_text(self, trap):
        texts = TrapsController.detection_texts
        text = randomitem(texts)
        trap.detection_text = text
        return