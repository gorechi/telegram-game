from dataclasses import dataclass
from src.functions.functions import randomitem

from src.class_trap import Trap
from src.class_controller import Controller

class TrapsController(Controller):
    """Класс для управления ловушками."""

    @dataclass
    class Template():
        class_name: str
        name: str
        description: str
        lexemes: dict

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
        """
        Функция выполняет дополнительные действия по настройке ловушки.
        """
        self.set_detection_text(trap)
        return True
    

    def set_detection_text(self, trap):
        """
        Функция устанавливает текст обнаружения ловушки.
        """
        trap.detection_text = randomitem(TrapsController.detection_texts)
        return