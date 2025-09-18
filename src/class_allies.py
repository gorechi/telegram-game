from src.class_items import Matches
from src.class_rune import Rune
from src.class_basic import Money
from src.class_book import Book
from src.class_potions import Potion
from src.class_backpack import Backpack
from src.functions.functions import randomitem, tprint, roll, howmany

from dataclasses import dataclass
from typing import Union, Literal, Optional

class Trader:
    """Класс Торговец"""
    
    _how_many_runes_trader_can_have = 4
    """Кубик, который надо кинуть чтобы определить количество рун у торговца"""

    _how_many_potions_trader_can_have = 6
    """Кубик, который надо кинуть чтобы определить количество зелий у торговца"""

    _maximum_money = 50
    """Максимальное количество денег у торговца"""

    _minimum_money = 20
    """Минимальное количество денег у торговца"""

    @dataclass
    class ItemInShop:
        item: Book | Rune | Potion | Matches
        price: int
        index: Optional[int] = None
    
    
    @classmethod
    def random_trader(cls, game, floor) -> 'Trader':
        """
        Функция возвращает случайного торговца.
        """
        trader_class = randomitem(cls.__subclasses__())
        new_trader = trader_class(game, floor)
        return new_trader
    
    
    @staticmethod
    def search_item_by_index(items_list:list, index:int) -> Union[Book, Rune, Potion, Matches, None]:
        """
        Функция ищет предмет в списке по его индексу.
        """
        for item in items_list:
            if item.index == index:
                return item
        return None
    
    
    @staticmethod
    def search_item_by_name(items_list:list, name:str) -> Union[Book, Rune, Potion, Matches, None]:
        """
        Функция ищет предмет в списке по его имени.
        """
        if not name or not isinstance(name, str):
            raise ValueError('В метод randomitem передан пустой массив')
        for item in items_list:
            if item.item.check_name(name):
                return item
        return None
    

    def __init__(self,
                 game,
                 floor,
                 name:str = '',
                 lexemes:dict = None):
        self.game = game
        self.floor = floor
        self.name = name
        self.room = None
        self.lexemes = lexemes
        self.shop = []
        self.goods_to_buy = []
        self.money = self.generate_money()
        self.game.all_traders.append(self)    
    
    
    def __format__(self, format:str) -> str:
        """
        Функция форматирует имя торговца в зависимости от падежа.
        """
        return self.lexemes.get(format, '')
    
    
    def sell(self, item_text:str, who) -> bool:
        """
        Функция продает предмет у торговца.
        """
        item_in_shop = self.get_item_by_text(item_text, 'sell')
        if not item_in_shop:
            tprint(self.game, f'{self:nom} растерянно качает головой, явно не понимая, о чем идет речь.')
            return False
        item = item_in_shop.item
        item_price = item_in_shop.price
        available_money = who.money.get_sum()
        if item_price > available_money:
            tprint(self.game, f'У {who:gen} не хватает денег чтобы купить {item:accus}.')
            return False
        self.take_money(who, item_price)
        self.give_item(who, item_in_shop)
        tprint(self.game, f'{who:gen} платит {howmany(item_price, ["монета", "монеты", "монет"])} и кладет {item:accus} в свой рюкзак')
        self.update_indexes()
        return True
     
     
    def buy(self, item_text:str, who) -> bool:
        """
        Функция покупает предмет у торговца.
        """
        item_to_buy = self.get_item_by_text(item_text, 'buy')
        if not item_to_buy:
            tprint(self.game, f'{self:nom} на такое предложение даже не поднимает глаз от какого-то документа. Ему не нужен подобный хлам.')
            return False
        item = item_to_buy.item
        item_price = item_to_buy.price
        if self.money < item_price:
            tprint(self.game, f'{self:nom} не может позволить себе купить такую дорогую вещь.')
            return False
        self.give_money(who, item_price)
        self.take_item(who, item_to_buy)
        tprint(self.game, f'{who:gen} продает {item:accus} {self:dat} и получает {howmany(item_price, ["монета", "монеты", "монет"])}.')
        self.update_indexes()
        return True
   
        
    def take_money(self, who, amount) -> bool:
        """
        Функция принимает деньги от героя.
        """
        who.money -= amount
        self.money += amount
        return True
    
    
    def give_money(self, who, amount) -> bool:
        """
        Функция отдает деньги герою.
        """
        who.money += amount
        self.money -= amount
        return True

    
    def give_item(self, who, item_to_give:ItemInShop) -> bool:
        """
        Функция отдает предмет герою.
        """
        item = item_to_give.item
        who.backpack.append(item)
        self.shop.remove(item_to_give)
        self.goods_to_buy.append(item_to_give)
        return True
    
    
    def take_item(self, who, item_to_take:ItemInShop) -> bool:
        """
        Функция принимает предмет от героя.
        """
        item = item_to_take.item
        price = self.evaluate(item)
        item_to_take.price = price
        self.shop.append(item_to_take)
        self.update_index(self.shop)
        self.goods_to_buy.remove(item_to_take)
        who.backpack.remove(item)
        return True
    
    
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
      
    
    def get_item_by_text(self, text:str, mode: Literal['buy', 'sell']) -> Union[Book, Rune, Potion, Matches, None]:
        """
        Функция ищет предмет по тексту в зависимости от режима (покупка или продажа).
        """
        if mode == 'sell':
            items_list = self.shop
        elif mode == 'buy':
            items_list = self.goods_to_buy
        else:
            return None
        if text.isdigit():
            index = int(text)
            return Trader.search_item_by_index(items_list, index)
        return Trader.search_item_by_name(items_list, text)
    
    
    def update_index(self, list_of_items:list) -> bool:
        """
        Функция обновляет индексы предметов в списке.
        """
        index = 0
        for item in list_of_items:
            index += 1
            item.index = index
        return True
    
    
    def update_indexes(self) -> None:
        """
        Функция обновляет индексы предметов в списках товаров и покупок.
        """
        self.update_index(self.goods_to_buy)
        self.update_index(self.shop)
     
    
    def place(self, room=None):
        """
        Функция размещает торговца в комнате.
        """
        if room:
            traders_room = room
        else:
            locked_rooms = [room for room in self.floor.plan if room.locked]
            traders_room = randomitem(locked_rooms)
        traders_room.trader = self
        traders_room.clear_from_monsters()
        traders_room.light = True
        self.room = traders_room
        if not self.room.can_rest(mode='simple'):
            new_rest_place = self.game.furniture_controller.get_random_object_by_filters(name="кресло")
            new_rest_place.place(room_to_place=self.room)
    
    
    def show_through_key_hole(self) -> str|list:
        """
        Функция показывает торговца через замочную скважину.
        """
        return 'Видно кусок витрины, наполненной разноцветными непонятными вещицами.'
    
    
    def get_prices(self, backpack:Backpack) -> list[str]:
        """
        Функция оценивает вещи в рюкзаке героя и генерирует текст с ценами.
        """
        self.evaluate_items(backpack)
        message = self.generate_selling_text()
        message.extend(self.generate_buying_text())
        return message 
    
            
class Scribe(Trader):
    """Класс Книжник"""
    
    _books_quantity_die = 10
    """Кубик, который надо кинуть чтобы определить количество книг у книжника"""

    _lexemes = {
        "nom": "Книжник",
        "accus": "Книжника",
        "gen": "Книжника",
        "dat": "Книжнику",
        "prep": "Книжнике",
        "inst": "Книжником"
    }
    
    _buy_price_modifier = [3]
    
    _sell_price_modifier = [3]
    
    
    def __init__(self,
                 game,
                 floor,
                 name:str = '',
                 lexemes:dict = None
                 ):
        super().__init__(game, floor, name, lexemes)
        self.name = name
        if not self.name:
            self.name = 'Книжник'
        self.lexemes = lexemes
        if not self.lexemes:
            self.lexemes = Scribe._lexemes
        self.get_goods()
    
    
    def get_goods(self) -> bool:
        """
        Функция генерирует книги для продажи у книжника.
        """
        self.shop = []
        how_many_books = roll([Scribe._books_quantity_die])
        for _ in range(how_many_books):
            book = self.game.books_controller.get_random_object_by_filters()
            price = self.evaluate(book)
            new_book = Trader.ItemInShop(item=book, price=price)
            self.shop.append(new_book)
        self.update_index(self.shop)
        return True

    
    def evaluate(self, book:Book) -> int:
        """
        Функция оценивает книгу для продажи.
        """
        return book.base_price + roll(Scribe._sell_price_modifier)


    def generate_selling_text(self) -> list[str]:
        """
        Функция генерирует текст с книгами на продажу.
        """
        if not self.shop:
            return ['На полках торговца пусто. Ему нечего предложить на продажу.']
        message = ['В лавке торговца на полках стоят следующие книги:']
        for item in self.shop:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message


    def generate_buying_text(self) -> list[str]:
        """
        Функция генерирует текст с книгами, которые книжник готов купить.
        """
        if not self.goods_to_buy:
            return ['Книжник не хочет ничего покупать у героя.']
        message = ['Книжник с удовольствием приобрел бы у героя следующие вещи по сходной цене:']
        for item in self.goods_to_buy:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message
        
    
    def evaluate_items(self, backpack:Backpack) -> bool:
        """
        Функция оценивает книги в рюкзаке героя для покупки.
        """
        books:list[Book] = backpack.get_items_by_class('Book')
        if not books:
            self.goods_to_buy.clear()
            return False
        books_list = []
        for book in books:
            price = book.base_price - roll(Scribe._buy_price_modifier)
            new_book = Trader.ItemInShop(item=book, price=price)
            books_list.append(new_book)
        self.update_index(books_list)
        self.goods_to_buy = books_list
        return True
    
    
    def show(self) -> str:
        """
        Функция показывает книжника в комнате.
        """
        return 'У стены, под лампой среди пыльных томов сидит торговец книгами.'


class RuneMerchant(Trader):
    """Класс Торговец рунами"""
    
    _runes_quantity_die = 15
    """Кубик, который надо кинуть чтобы определить количество рун у торговца"""

    _lexemes = {
        "nom": "Торговец рунами",
        "accus": "Торговца рунами",
        "gen": "Торговца рунами",
        "dat": "Торговцу рунами",
        "prep": "Торговце рунами",
        "inst": "Торговцем рунами"
    }
    
    _buy_price_modifier = [8]
    
    _sell_price_modifier = [5]
    
    
    def __init__(self,
                 game,
                 floor,
                 name:str = 'Торговец рунами',
                 lexemes:dict = None
                 ):
        super().__init__(game, floor, name, lexemes)
        self.name = name
        self.lexemes = lexemes
        if not self.lexemes:
            self.lexemes = RuneMerchant._lexemes
        self.get_goods()
    
    
    def get_goods(self) -> bool:
        """
        Функция генерирует книги для продажи у торговца рунами.
        """
        self.shop = []
        how_many_runes = roll([RuneMerchant._runes_quantity_die])
        for _ in range(how_many_runes):
            rune = self.game.runes_controller.get_random_object_by_filters()
            price = self.evaluate(rune)
            new_rune = Trader.ItemInShop(item=rune, price=price)
            self.shop.append(new_rune)
        self.update_index(self.shop)
        return True

    
    def evaluate(self, rune:Rune) -> int:
        """
        Функция оценивает руну для продажи.
        """
        return rune.base_price + roll(RuneMerchant._sell_price_modifier)


    def generate_selling_text(self) -> list[str]:
        """
        Функция генерирует текст с рунами на продажу.
        """
        if not self.shop:
            return ['В сундуках торговца пусто. Ему нечего предложить на продажу.']
        message = ['Перед торговцем на прилавке разложены следующие руны:']
        for item in self.shop:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message


    def generate_buying_text(self) -> list[str]:
        """
        Функция генерирует текст с рунами, которые торговец готов купить.
        """
        if not self.goods_to_buy:
            return ['Торговец рунами не хочет ничего покупать у героя.']
        message = ['Торговец рунами с удовольствием приобрел бы у героя следующие руны:']
        for item in self.goods_to_buy:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message
        
    
    def evaluate_items(self, backpack:Backpack) -> bool:
        """
        Функция оценивает руны в рюкзаке героя для покупки.
        """
        runes:list[Rune] = backpack.get_items_by_class('Rune')
        if not runes:
            self.goods_to_buy.clear()
            return False
        runes_list = []
        for rune in runes:
            price = rune.base_price - roll(RuneMerchant._buy_price_modifier)
            new_rune = Trader.ItemInShop(item=rune, price=price)
            runes_list.append(new_rune)
        self.update_indexes()
        self.goods_to_buy = runes_list
        return True
    
    
    def show(self) -> str:
        """
        Функция показывает торговца рунами в комнате.
        """
        return 'Посреди комнаты стоит прилавок торговца рунами. Сам он суетится вокруг.'
    
    
class PotionsMerchant(Trader):
    """Класс Торговец зельями"""
    
    _potions_quantity_die = 10
    """Кубик, который надо кинуть чтобы определить количество зелий у торговца"""

    _lexemes = {
        "nom": "Торговец зельями",
        "accus": "Торговца зельями",
        "gen": "Торговца зельями",
        "dat": "Торговцу зельями",
        "prep": "Торговце зельями",
        "inst": "Торговцем зельями"
    }
    
    _buy_price_modifier = [5]
    
    _sell_price_modifier = [5]
    
    
    def __init__(self,
                 game,
                 floor,
                 name:str = 'Торговец зельями',
                 lexemes:dict = None
                 ):
        super().__init__(game, floor, name, lexemes)
        self.name = name
        self.lexemes = lexemes
        if not self.lexemes:
            self.lexemes = PotionsMerchant._lexemes
        self.get_goods()
    
    
    def get_goods(self) -> bool:
        """
        Функция генерирует книги для продажи у торговца зельями.
        """
        self.shop = []
        how_many_potions = roll([PotionsMerchant._potions_quantity_die])
        for _ in range(how_many_potions):
            potion = self.game.potions_controller.get_random_object_by_filters()
            price = self.evaluate(potion)
            new_potion = Trader.ItemInShop(item= potion, price=price)
            self.shop.append(new_potion)
        self.update_index(self.shop)
        return True

    
    def evaluate(self, potion:Potion) -> int:
        """
        Функция оценивает зелье для продажи.
        """
        return potion.base_price + roll(PotionsMerchant._sell_price_modifier)


    def generate_selling_text(self) -> list[str]:
        """
        Функция генерирует текст с зельями на продажу.
        """
        if not self.shop:
            return ['В сундуках торговца пусто. Ему нечего предложить на продажу.']
        message = ['На витрине стоят бутылочки с различными зельями:']
        for item in self.shop:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message


    def generate_buying_text(self) -> list[str]:
        """
        Функция генерирует текст с зельями, которые торговец готов купить.
        """
        if not self.goods_to_buy:
            return ['Торговец зельями не хочет ничего покупать у героя.']
        message = ['Торговец зельями с удовольствием приобрел бы у героя следующие напитки:']
        for item in self.goods_to_buy:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message
        
    
    def evaluate_items(self, backpack:Backpack) -> bool:
        """
        Функция оценивает зелья в рюкзаке героя для покупки.
        """
        potions:list[Potion] = backpack.get_items_by_class('Potion')
        if not potions:
            self.goods_to_buy.clear()
            return False
        potions_list = []
        for potion in potions:
            price = potion.base_price - roll(PotionsMerchant._buy_price_modifier)
            new_potion = Trader.ItemInShop(item=potion, price=price)
            potions_list.append(new_potion)
        self.update_indexes()
        self.goods_to_buy = potions_list
        return True
    
    
    def show(self) -> str:
        """
        Функция показывает торговца зельями в комнате.
        """
        return 'Посреди комнаты стоит прилавок торговца зельями. Торговец занимается приготовлением какой-то микстуры.'