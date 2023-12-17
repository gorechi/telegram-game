from class_items import Book, Key, Money, Rune
from class_monsters import Monster, Vampire
from class_protection import Armor, Shield
from class_room import Furniture, Room
from class_weapon import Weapon
from functions import howmany, normal_count, randomitem, tprint, roll
from settings import *


class Trader:
    """Класс Торговец"""
    
    trader_types = [
        'books',
        'runes'
    ]
    
    def __init__(self,
                 floor,
                 game,
                 name,
                 lexeme,
                 gender):
        self.game = game
        self.floor = floor
        self.name = name
        self.room = None
        self.lexeme = lexeme
        self.gender = gender
        self.shop = []
        self.place()
        self.type = randomitem(Trader.trader_types)
        self.get_items()
        self.money = self.generate_money()    
    
    
    def generate_money(self) -> Money:
        delta = s_traider_maximum_money - s_traider_minimum_money
        money_amount = s_traider_minimum_money + roll([delta])
        new_money = Money(self.game, money_amount)
        return new_money
    
    
    def get_items(self) -> bool:
        actions = {
            'books': self.get_books,
            'runes': self.get_runes
        }
        if not actions.get(self.type):
            return False
        return actions[self.type]()
    
    
    def get_books(self) -> bool:
        how_many_books = roll([s_how_many_books_trader_can_have])
        books = self.game.create_objects_from_json(file='books.json',
                                    how_many=how_many_books,
                                    random=True)
        self.shop += books
        return True
    
    
    def get_runes(self) -> bool:
        how_many_runes = roll([s_how_many_runes_trader_can_have])
        runes = [Rune(self.game) for _ in range(how_many_runes)]
        self.shop += runes
        return True
    
    
    def place(self):
        locked_rooms = [room for room in self.floor.plan if room.locked]
        traiders_room = randomitem(locked_rooms)
        traiders_room.traider = self
        traiders_room.clear_from_monsters()
        traiders_room.light = True
        self.room = traiders_room
        if not self.room.can_rest(mode='simple'):
            new_rest_place = Furniture(game=self.game, name='Удобное кресло', can_rest=True)
            new_rest_place.place(room_to_place=self.room)
    
    
    def show_through_key_hole(self) -> str|list:
        return 'Видно кусок витрины, наполненной разноцветными непонятными вещицами.'
    
    
    def show(self) -> str:
        descriptions = {
            'books': 'У стены, под лампой среди пыльных томов сидит торговец книгами.',
            'runes': 'Перед окном стоит яркий прилавок, из-за которого еле видно торговца рунами.'
        }
        return descriptions[self.type]
    
    
    def get_item_by_number(self, number:str):
        """
        Метод возвращает вещь из магазина по ее порядковому номеру.
        
        """
        
        number = int(number) - 1
        if number < len(self.shop):
            return self.shop[number]
        else:
            return False
    
    
    def show_shop(self):
        """Метод генерирует список товаров в лавке торговца."""
        
        message = []
        if len(self.shop) == 0:
            message.append('Торговцу нечего предложить.')
        else:
            message.append('Торговец предлагает на продажу следующие диковины:')
            for i, item in enumerate(self.backpack):
                description = f'{str(i + 1)}: {item.show_in_shop()}'
                message.append(description)
            message.append(self.money.show())
        tprint(self.game, message)
        return True