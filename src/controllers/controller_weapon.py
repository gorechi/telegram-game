from dataclasses import dataclass

from src.class_weapon import Weapon, Torch
from src.class_controller import Controller
from src.functions.functions import randomitem

class WeaponController(Controller):
    """Класс для управления оружием."""

    _decorators = {
    "колющее":
    [
        {
        "damage_modifier": 1,
        0: 
            {
            "nom": "Большой",
            "accus": "Большой",
            "gen": "Большого",
            "dat": "Большому",
            "prep": "Большом",
            "inst": "Большим",
            }, 
        1: 
            {
            "nom": "Большая",
            "accus": "Большую",
            "gen": "Большой",
            "dat": "Большой",
            "prep": "Большой",
            "inst": "Большой",
            }, 
        2: 
            {
            "nom": "Большое",
            "accus": "Большое",
            "gen": "Большого",
            "dat": "Большому",
            "prep": "Большом",
            "inst": "Большим",
        }
        },
        {
        "damage_modifier": -1,
        0: 
            {
            "nom": "Малый",
            "accus": "Малый",
            "gen": "Малого",
            "dat": "Малому",
            "prep": "Малом",
            "inst": "Малым",
            }, 
        1: 
            {
            "nom": "Малая",
            "accus": "Малую",
            "gen": "Малой",
            "dat": "Малой",
            "prep": "Малой",
            "inst": "Малой",
            }, 
        2: 
            {
            "nom": "Малое",
            "accus": "Малое",
            "gen": "Малого",
            "dat": "Малому",
            "prep": "Малом",
            "inst": "Малым",
        }
        },
        {
        "damage_modifier": -1,
        0: 
            {
            "nom": "Старый",
            "accus": "Старый",
            "gen": "Старого",
            "dat": "Старому",
            "prep": "Старом",
            "inst": "Старым",
            }, 
        1: 
            {
            "nom": "Старая",
            "accus": "Старую",
            "gen": "Старой",
            "dat": "Старой",
            "prep": "Старой",
            "inst": "Старой",
            }, 
        2: 
            {
            "nom": "Старое",
            "accus": "Старое",
            "gen": "Старого",
            "dat": "Старому",
            "prep": "Старом",
            "inst": "Старым",
        }
        },
        {
        "damage_modifier": 1,
        0: 
            {
            "nom": "Новый",
            "accus": "Новый",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым",
            }, 
        1: 
            {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой",
            }, 
        2: 
            {
            "nom": "Новое",
            "accus": "Новое",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым",
            }
        }
    ],
    "ударное":
    [
        {
        "damage_modifier": 2,
        0: 
            {
            "nom": "Большой",
            "accus": "Большой",
            "gen": "Большого",
            "dat": "Большому",
            "prep": "Большом",
            "inst": "Большим",
            }, 
        1: 
            {
            "nom": "Большая",
            "accus": "Большую",
            "gen": "Большой",
            "dat": "Большой",
            "prep": "Большой",
            "inst": "Большой",
            }, 
        2: 
            {
            "nom": "Большое",
            "accus": "Большое",
            "gen": "Большого",
            "dat": "Большому",
            "prep": "Большом",
            "inst": "Большим",
        }
        },
        {
        "damage_modifier": -1,
        0: 
            {
            "nom": "Малый",
            "accus": "Малый",
            "gen": "Малого",
            "dat": "Малому",
            "prep": "Малом",
            "inst": "Малым",
            }, 
        1: 
            {
            "nom": "Малая",
            "accus": "Малую",
            "gen": "Малой",
            "dat": "Малой",
            "prep": "Малой",
            "inst": "Малой",
            }, 
        2: 
            {
            "nom": "Малое",
            "accus": "Малое",
            "gen": "Малого",
            "dat": "Малому",
            "prep": "Малом",
            "inst": "Малым",
        }
        },
        {
        "damage_modifier": 0,
        0: 
            {
            "nom": "Старый",
            "accus": "Старый",
            "gen": "Старого",
            "dat": "Старому",
            "prep": "Старом",
            "inst": "Старым",
            }, 
        1: 
            {
            "nom": "Старая",
            "accus": "Старую",
            "gen": "Старой",
            "dat": "Старой",
            "prep": "Старой",
            "inst": "Старой",
            }, 
        2: 
            {
            "nom": "Старое",
            "accus": "Старое",
            "gen": "Старого",
            "dat": "Старому",
            "prep": "Старом",
            "inst": "Старым",
        }
        },
        {
        "damage_modifier": 1,
        0: 
            {
            "nom": "Тяжелый",
            "accus": "Тяжелый",
            "gen": "Тяжелого",
            "dat": "Тяжелому",
            "prep": "Тяжелом",
            "inst": "Тяжелым",
            }, 
        1: 
            {
            "nom": "Тяжелая",
            "accus": "Тяжелую",
            "gen": "Тяжелой",
            "dat": "Тяжелой",
            "prep": "Тяжелой",
            "inst": "Тяжелой",
            }, 
        2: 
            {
            "nom": "Тяжелое",
            "accus": "Тяжелое",
            "gen": "Тяжелого",
            "dat": "Тяжелому",
            "prep": "Тяжелом",
            "inst": "Тяжелым",
            }
        }
    ],
        "рубящее":
    [
        {
        "damage_modifier": 2,
        0: 
            {
            "nom": "Большой",
            "accus": "Большой",
            "gen": "Большого",
            "dat": "Большому",
            "prep": "Большом",
            "inst": "Большим",
            }, 
        1: 
            {
            "nom": "Большая",
            "accus": "Большую",
            "gen": "Большой",
            "dat": "Большой",
            "prep": "Большой",
            "inst": "Большой",
            }, 
        2: 
            {
            "nom": "Большое",
            "accus": "Большое",
            "gen": "Большого",
            "dat": "Большому",
            "prep": "Большом",
            "inst": "Большим",
        }
        },
        {
        "damage_modifier": -1,
        0: 
            {
            "nom": "Малый",
            "accus": "Малый",
            "gen": "Малого",
            "dat": "Малому",
            "prep": "Малом",
            "inst": "Малым",
            }, 
        1: 
            {
            "nom": "Малая",
            "accus": "Малую",
            "gen": "Малой",
            "dat": "Малой",
            "prep": "Малой",
            "inst": "Малой",
            }, 
        2: 
            {
            "nom": "Малое",
            "accus": "Малое",
            "gen": "Малого",
            "dat": "Малому",
            "prep": "Малом",
            "inst": "Малым",
        }
        },
        {
        "damage_modifier": -1,
        0: 
            {
            "nom": "Старый",
            "accus": "Старый",
            "gen": "Старого",
            "dat": "Старому",
            "prep": "Старом",
            "inst": "Старым",
            }, 
        1: 
            {
            "nom": "Старая",
            "accus": "Старую",
            "gen": "Старой",
            "dat": "Старой",
            "prep": "Старой",
            "inst": "Старой",
            }, 
        2: 
            {
            "nom": "Старое",
            "accus": "Старое",
            "gen": "Старого",
            "dat": "Старому",
            "prep": "Старом",
            "inst": "Старым",
        }
        },
        {
        "damage_modifier": 1,
        0: 
            {
            "nom": "Новый",
            "accus": "Новый",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым",
            }, 
        1: 
            {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой",
            }, 
        2: 
            {
            "nom": "Новое",
            "accus": "Новое",
            "gen": "Нового",
            "dat": "Новому",
            "prep": "Новом",
            "inst": "Новым",
            }
        }
    ]
    }
    """Словарь первых слов в описании оружия."""
    
    @dataclass
    class Template():
        class_name: str
        weapon_type: str
        gender: int
        name: str
        lexemes: dict
        damage: dict
        enchantable: bool
        actions: list
        hit_chance: dict
        twohanded: bool
        fencing: bool
        
    _classes = {
        "Weapon": Weapon,
        "Torch": Torch,
    }       
        
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/weapon.json')
        self.all_objects = []
        
    
    def additional_actions(self, weapon) -> bool:
        if not type(weapon) == Torch:
            self.decorate(weapon)
        return True
    
    
    def decorate(self, weapon) -> bool:
        decorators = WeaponController._decorators.get(weapon.weapon_type, [])
        decorator = randomitem(decorators)
        if not decorator:
            return False
        if not decorator.get(weapon.gender, False):
            return False
        lexemes = {}
        for lexeme in weapon.lexemes:
            decorate_string = decorator[weapon.gender].get(lexeme, False)
            if decorate_string:
                lexemes[lexeme] = f'{decorate_string} {weapon.lexemes[lexeme]}'
        weapon.damage.increase_modifier(decorator['damage_modifier'])
        weapon.lexemes = lexemes
        return True
    
    def get_empty_object_by_class_name(self, class_name:str):
        new_class = self.__class__._classes[class_name]
        new_object = new_class(game=self.game)
        new_object.empty = True
        new_object.twohanded = False
        new_object.fencing = False
        return new_object

