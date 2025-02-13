from dataclasses import dataclass

from src.class_protection import Armor, Shield, Protection
from src.class_controller import Controller
from src.functions.functions import randomitem

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
        noisy: bool
        
    _classes = {
        "Armor": Armor,
        "Shield": Shield
    }
    
    _armor_decorators = {
    "кованый":
    [
        {
        "protection_modifier": 2,
        0: 
            {
            "nom": "Сияющий",
            "accus": "Сияющего",
            "gen": "Сияющего",
            "dat": "Сияющему",
            "prep": "Сияющем",
            "inst": "Сияющим",
            }, 
        1: 
            {
            "nom": "Сияющая",
            "accus": "Сияющую",
            "gen": "Сияющей",
            "dat": "Сияющей",
            "prep": "Сияющей",
            "inst": "Сияющей",
            }, 
        2: 
            {
            "nom": "Сияющее",
            "accus": "Сияющее",
            "gen": "Сияющего",
            "dat": "Сияющему",
            "prep": "Сияющем",
            "inst": "Сияющим",
        }
        },
        {
        "protection_modifier": -2,
        0: {
            "nom": "Ржавый",
            "accus": "Ржавого",
            "gen": "Ржавого",
            "dat": "Ржавому",
            "prep": "Ржавом",
            "inst": "Ржавым"
        },
        1: {
            "nom": "Ржавая",
            "accus": "Ржавую",
            "gen": "Ржавой",
            "dat": "Ржавой",
            "prep": "Ржавой",
            "inst": "Ржавой"
        },
        2: {
            "nom": "Ржавое",
            "accus": "Ржавое",
            "gen": "Ржавого",
            "dat": "Ржавому",
            "prep": "Ржавом",
            "inst": "Ржавым"
        }
        },
        {
        "protection_modifier": 0,
        0: {
            "nom": "Новый",
            "accus": "Нового",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        },
        1: {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой"
        },
        2: {
            "nom": "Новое",
            "accus": "Новое",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        }
        },
        {
        "protection_modifier": -1,
        0: 
            {
            "nom": "Помятый",
            "accus": "Помятого",
            "gen": "Помятого",
            "dat": "Помятому",
            "prep": "Помятом",
            "inst": "Помятым",
            }, 
        1: 
            {
            "nom": "Помятая",
            "accus": "Помятую",
            "gen": "Помятой",
            "dat": "Помятой",
            "prep": "Помятой",
            "inst": "Помятой",
            }, 
        2: 
            {
            "nom": "Помятое",
            "accus": "Помятое",
            "gen": "Помятого",
            "dat": "Помятому",
            "prep": "Помятом",
            "inst": "Помятым",
        }
        },
        {
        "protection_modifier": 1,
        0: 
            {
            "nom": "Крепкий",
            "accus": "Крепкого",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
            }, 
        1: 
            {
            "nom": "Крепкая",
            "accus": "Крепкую",
            "gen": "Крепкой",
            "dat": "Крепкой",
            "prep": "Крепкой",
            "inst": "Крепкой",
            }, 
        2: 
            {
            "nom": "Крепкое",
            "accus": "Крепкое",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
        }
        }
    ],
    "кожаный":
    [
        {
        "protection_modifier": 0,
        0: {
            "nom": "Новый",
            "accus": "Нового",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        },
        1: {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой"
        },
        2: {
            "nom": "Новое",
            "accus": "Новое",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым"
        }
        },
        {
        "protection_modifier": 1,
        0: 
            {
            "nom": "Крепкий",
            "accus": "Крепкого",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
            }, 
        1: 
            {
            "nom": "Крепкая",
            "accus": "Крепкую",
            "gen": "Крепкой",
            "dat": "Крепкой",
            "prep": "Крепкой",
            "inst": "Крепкой",
            }, 
        2: 
            {
            "nom": "Крепкое",
            "accus": "Крепкое",
            "gen": "Крепкого",
            "dat": "Крепкому",
            "prep": "Крепком",
            "inst": "Крепким",
        }
        },
        {
        "protection_modifier": 2,
        0: 
            {
            "nom": "Мощный",
            "accus": "Мощного",
            "gen": "Мощного",
            "dat": "Мощному",
            "prep": "Мощном",
            "inst": "Мощным",
            }, 
        1: 
            {
            "nom": "Мощная",
            "accus": "Мощную",
            "gen": "Мощной",
            "dat": "Мощной",
            "prep": "Мощной",
            "inst": "Мощной",
            }, 
        2: 
            {
            "nom": "Мощное",
            "accus": "Мощное",
            "gen": "Мощного",
            "dat": "Мощному",
            "prep": "Мощном",
            "inst": "Мощным",
        }
        },
        {
        "protection_modifier": -1,
        0: {
            "nom": "Дырявый",
            "accus": "Дырявого",
            "gen": "Дырявого",
            "dat": "Дырявому",
            "prep": "Дырявом",
            "inst": "Дырявым"
        },
        1: {
            "nom": "Дырявая",
            "accus": "Дырявую",
            "gen": "Дырявой",
            "dat": "Дырявой",
            "prep": "Дырявой",
            "inst": "Дырявой"
        },
        2: {
            "nom": "Дырявое",
            "accus": "Дырявое",
            "gen": "Дырявого",
            "dat": "Дырявому",
            "prep": "Дырявом",
            "inst": "Дырявым"
        }
        }
    ]
    }
    """Словарь декораторов для защины"""


    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/protection.json')
        self.all_objects = []
        
    
    def additional_actions(self, protection) -> bool:
        self.decorate(protection)
        return True
    
    
    def decorate(self, protection) -> None:
        if isinstance(protection, Armor):
            self.decorate_armor(protection)
    
    
    def decorate_armor(self, armor) -> bool:
        decorators = ProtectionController._armor_decorators.get(armor.protection_type, [])
        decorator = randomitem(decorators)
        if not decorator:
            return False
        if not decorator.get(armor.gender, False):
            return False
        lexemes = {}
        for lexeme in armor.lexemes:
            decorate_string = decorator[armor.gender].get(lexeme, False)
            if decorate_string:
                lexemes[lexeme] = f'{decorate_string} {armor.lexemes[lexeme]}'
        armor.protection.increase_modifier(decorator['protection_modifier'])
        armor.lexemes = lexemes
        return True