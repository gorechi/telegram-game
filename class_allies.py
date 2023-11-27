from class_items import Book, Key, Money, Rune
from class_monsters import Monster, Vampire
from class_protection import Armor, Shield
from class_room import Furniture, Room
from class_weapon import Weapon
from functions import howmany, normal_count, randomitem, showsides, tprint
from settings import *

class Trader:
    """Класс Торговец"""
    
    def __init__(self,
                 game,
                 name,
                 lexeme,
                 gender):
        self.game = game
        self.name = name
        self.lexeme = lexeme
        self.gender = gender
    
    
    