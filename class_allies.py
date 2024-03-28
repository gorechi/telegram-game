from class_items import Book, Key, Money, Rune
from class_room import Furniture, Room
from functions import randomitem, tprint, roll


class Trader:
    """Класс Торговец"""
    
    _types = (
        'books',
        'runes'
    )
    
    _how_many_books_trader_can_have = 5
    """Кубик, который надо кинуть чтобы определить количество книг у торговца"""

    _how_many_runes_trader_can_have = 4
    """Кубик, который надо кинуть чтобы определить количество рун у торговца"""

    _how_many_potions_trader_can_have = 6
    """Кубик, который надо кинуть чтобы определить количество зелий у торговца"""

    _maximum_money = 50
    """Максимальное количество денег у торговца"""

    _minimum_money = 20
    """Минимальное количество денег у торговца"""

    
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
        self.type = randomitem(Trader._types)
        self.get_items()
        self.money = self.generate_money()    
    
    
    def generate_money(self) -> Money:
        """
        Генерирует объект денег для торговца.

        Метод вычисляет случайное количество денег в пределах заданных настроек (минимум и максимум),
        создает и возвращает объект Money с этим количеством денег.

        Returns:
            Money: Объект денег с сгенерированным количеством.
        """
        delta = Trader._maximum_money - Trader._minimum_money
        money_amount = Trader._minimum_money + roll([delta])
        new_money = Money(self.game, money_amount)
        return new_money
    
    
    def get_items(self) -> bool:
        """
        Получает предметы для магазина торговца в зависимости от его типа.

        Метод определяет тип торговца (книги или руны) и вызывает соответствующий метод для получения предметов этого типа.
        Если тип торговца не поддерживается, метод возвращает False.

        Returns:
            bool: Возвращает True, если предметы успешно получены и добавлены в магазин торговца, иначе False.
        """
        actions = {
            'books': self.get_books,
            'runes': self.get_runes
        }
        if not actions.get(self.type):
            return False
        return actions[self.type]()
    
    
    def get_books(self) -> bool:
        """
        Получает книги для магазина торговца.

        Метод определяет случайное количество книг, которое может иметь торговец, используя настройку `_how_many_books_trader_can_have`.
        Затем создает указанное количество книг, загружая их из файла 'books.json' в случайном порядке, и добавляет их в магазин торговца.

        Returns:
            bool: Всегда возвращает True, так как предполагается, что операция добавления книг в магазин всегда успешна.
        """
        how_many_books = roll([Trader._how_many_books_trader_can_have])
        books = self.game.create_objects_from_json(file='books.json',
                                    how_many=how_many_books,
                                    random=True)
        self.shop += books
        return True
    
    
    def get_runes(self) -> bool:
        """
        Получает руны для магазина торговца.

        Этот метод определяет количество рун, которые может иметь торговец, на основе настройки `_how_many_runes_trader_can_have`.
        Затем он создает указанное количество рун, инстанцируя класс `Rune`, и добавляет их в магазин торговца.

        Возвращает:
            bool: Возвращает True, если руны успешно получены и добавлены в магазин, иначе False.
        """
        how_many_runes = roll([Trader._how_many_runes_trader_can_have])
        runes = [Rune(self.game) for _ in range(how_many_runes)]
        self.shop.extend(runes)
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
            for i, item in enumerate(self.shop):
                description = f'{str(i + 1)}: {item.show_in_shop()}'
                message.append(description)
            message.append(self.money.show())
        tprint(self.game, message)
        return True