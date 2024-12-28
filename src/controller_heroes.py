from dataclasses import dataclass

from src.class_hero import Hero
from src.class_controller import Controller
from src.functions.functions import randomitem

class HeroController(Controller):
    """Класс для управления героями."""

    @dataclass
    class Template():
        class_name: str
        name: str
        lexemes: dict
        stren: dict
        dext: dict
        intel: dict
        health: int
        hit_chance: dict
        can_hide: bool
        can_run: bool
        actions: list
        frightening: bool
        aggressive: bool
        carry_weapon: bool
        carry_shield: bool
        poison_level: dict
        poison_protection: dict
        gender: int
        corpse: bool
        wear_armor: bool
        weakness: dict
        monster_knowledge: dict
        level: int
        levels: list
        elements: dict
        element_levels: dict
        weapon_mastery: dict
        initiative: dict
        trap_mastery: int
        rage: dict
    
    
    _classes = {
        "Hero": Hero,
    }    
    
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/hero.json')
        self.all_objects = []