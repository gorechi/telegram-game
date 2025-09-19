from dataclasses import dataclass

from src.class_rune import Rune
from src.class_controller import Controller
from src.class_dice import Dice
from src.functions.functions import randomitem

class RunesController(Controller):
    """Класс для управления героями."""

    @dataclass
    class Template():
        class_name: str
        can_use_in_fight: bool
        name: str
        base_price: int
                   
    _classes = {
        "Rune": Rune,
    }
    
    _elements = (1, 3, 7, 12)
    
    _lexemes = {
            "nom": "руна",
            "accus": "руну",
            "gen": "руны",
            "dat": "руне",
            "prep": "руне",
            "inst": "руной"
            }
    
    _poison_probability = Dice([3])
    """
    Вероятность того, что руна будет отравленной. 

    """

    _elements_dictionary = {1: 'огня',
                        2: 'пламени',
                        3: 'воздуха',
                        4: 'света',
                        6: 'ветра',
                        7: 'земли',
                        8: 'лавы',
                        10: 'пыли',
                        12: 'воды',
                        13: 'пара',
                        14: 'камня',
                        15: 'дождя',
                        19: 'грязи',
                        24: 'потопа'}
    """Словарь стихий."""

    _base_price_dice = Dice([15])
    
    _poison_price_modifier = Dice([5])
    
    _damage_dice = Dice([4])
    
    _defence_dice = Dice([3])
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/runes.json')
        self.all_objects = []
    
    
    def additional_actions(self, item) -> bool:
        """
        Функция выполняет дополнительные действия по настройке руны.
        """
        self.generate_element(item)
        self.generate_base_price(item)
        self.generate_description(item)
        self.generate_damage(item)
        self.generate_defence(item)
        self.generate_lexemes(item)
        self.generate_poison(item)
        return True
    
    
    def generate_lexemes(self, rune:Rune):
        """
        Функция генерирует лексемы для руны.
        """
        lexemes = {}
        for key in RunesController._lexemes:
            lexemes[key] = f'{RunesController._lexemes[key]} {RunesController._elements_dictionary[rune.element]}'
        rune.lexemes = lexemes
        
    
    def generate_damage(self, rune:Rune):
        """
        Функция генерирует урон для руны.
        """
        rune.damage = RunesController._damage_dice.roll()
    
    
    def generate_defence(self, rune:Rune):
        """
        Функция генерирует защиту для руны.
        """
        rune.defence = RunesController._defence_dice.roll()
        
    
    def generate_element(self, rune:Rune):
        """
        Функция случайным образом выбирает стихию руны из доступных стихий.
        """
        rune.element = randomitem(RunesController._elements)
        
        
    def generate_description(self, rune:Rune):
        """
        Функция генерирует описание для руны.
        """
        rune.description = f'{rune.name} {RunesController._elements_dictionary[rune.element]}'
        
        
    def generate_poison(self, rune:Rune) -> bool:
        """
        Функция случайным образом определяет, будет ли руна отравленной.
        """    
        if RunesController._poison_probability.roll() == 1:
            rune.poison = True
            rune.description = f'ядовитая {rune.description}'
            rune.base_price += RunesController._poison_price_modifier.roll()
        else:
            rune.poison = False
        return True
        
    
    def generate_base_price(self, rune:Rune):
        """
        Функция генерирует базовую цену для руны.
        """
        rune.base_price += RunesController._base_price_dice.roll()
    