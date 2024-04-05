from class_items import Book, Money, Rune, Matches
from class_potions import Potion
from class_backpack import Backpack
from class_room import Furniture, Room
from functions import randomitem, tprint, roll, howmany
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
    
    
    @staticmethod
    def search_item_by_index(items_list:list, index:int) -> Union[Book, Rune, Potion, Matches, None]:
        for item in items_list:
            if item.index == index:
                return item
        return None
    
    
    @staticmethod
    def search_item_by_name(items_list:list, name:int) -> Union[Book, Rune, Potion, Matches, None]:
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
        self.place()
        self.money = self.generate_money()    
    
    
    def sell(self, item_text:str, who) -> bool:
        item_in_shop = self.get_item_by_text(item_text, 'sell')
        if not item_in_shop:
            tprint(self.game, f'{self.lexemes["nom"]} растерянно качает головой, явно не понимая, о чем идет речь.')
            return False
        item = item_in_shop.item
        item_price = item_in_shop.price
        available_money = who.money.get_sum()
        if item_price > available_money:
            tprint(self.game, f'У {who.lexemes["gen"]} не хватает денег чтобы купить {item.lexemes["accus"]}.')
            return False
        self.take_money(who, item_price)
        self.give_item(who, item_in_shop)
        tprint(self.game, f'{who.lexemes["gen"]} платит {howmany(item_price, "монета,монеты,монет")} и кладет {item.lexemes["accus"]} в свой рюкзак')
        self.update_indexes()
        return True
     
     
    def buy(self, item_text:str, who) -> bool:
        item_to_buy = self.get_item_by_text(item_text, 'buy')
        if not item_to_buy:
            tprint(self.game, f'{self.lexemes["nom"]} на такое предложение даже не поднимает глаз от фолианта, лежащего у него на коленях. Ему не нужен подобный хлам.')
            return False
        item = item_to_buy.item
        item_price = item_to_buy.price
        if self.money < item_price:
            tprint(self.game, f'{self.lexemes["nom"]} не может позволить себе купить такую дорогую вещь.')
            return False
        self.give_money(who, item_price)
        self.take_item(who, item_to_buy)
        tprint(self.game, f'{who.lexemes["gen"]} продает {item.lexemes["accus"]} {self.lexemes["dat"]} и получает {howmany(item_price, "монета,монеты,монет")}.')
        self.update_indexes()
        return True
   
        
    def take_money(self, who, amount) -> bool:
        who.money -= amount
        self.money += amount
        return True
    
    
    def give_money(self, who, amount) -> bool:
        who.money += amount
        self.money -= amount
        return True

    
    def give_item(self, who, item_to_give:ItemInShop) -> bool:
        item = item_to_give.item
        who.backpack.append(item)
        self.shop.remove(item_to_give)
        self.goods_to_buy.append(item_to_give)
        return True
    
    
    def take_item(self, who, item_to_take:ItemInShop) -> bool:
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
        index = 0
        for item in list_of_items:
            index += 1
            item.index = index
        return True
    
    
    def update_indexes(self) -> None:
        self.update_index(self.goods_to_buy)
        self.update_index(self.shop)
 
    
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
    
    
    def place(self, room=None):
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
            new_rest_place = Furniture(game=self.game, name='Удобное кресло', can_rest=True)
            new_rest_place.place(room_to_place=self.room)
    
    
    def show_through_key_hole(self) -> str|list:
        return 'Видно кусок витрины, наполненной разноцветными непонятными вещицами.'
    
    
    def show(self) -> str:
        return
    
    
    def get_prices(self, backpack:Backpack) -> list[str]:
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
        self.get_books()
    
    
    def get_books(self) -> bool:
        how_many_books = roll([Scribe._books_quantity_die])
        for _ in range(how_many_books):
            book = Book(self.game)
            price = self.evaluate(book)
            new_book = Trader.ItemInShop(item=book, price=price)
            self.shop.append(new_book)
        self.update_index(self.shop)
        return True

    
    def evaluate(self, book:Book) -> int:
        return book.base_price + roll(Scribe._sell_price_modifier)


    def generate_selling_text(self) -> list[str]:
        if not self.shop:
            return ['На полках торговца пусто. Ему нечего предложить на продажу.']
        message = ['В лавке торговца на полках стоят следующие книги:']
        for item in self.shop:
            name = item.item.lexemes['nom']
            price_text = howmany(item.price, 'монета,монеты,монет')
            message.append(f'{item.index} - {name}: {price_text}')
        return message


    def generate_buying_text(self) -> list[str]:
        if not self.goods_to_buy:
            return ['Книжник не хочет ничего покупать у героя.']
        message = ['Книжник с удовольствием приобрел бы у героя следующие вещи по сходной цене:']
        for item in self.goods_to_buy:
            name = item.item.lexemes['nom']
            price_text = howmany(item.price, 'монета,монеты,монет')
            message.append(f'{item.index} - {name}: {price_text}')
        return message
        
    
    def evaluate_items(self, backpack:Backpack) -> bool:
        books:list[Book] = backpack.get_items_by_class(Book)
        if not books:
            self.goods_to_buy.clear()
            return False
        books_list = []
        for book in books:
            price = book.base_price + roll(Scribe._buy_price_modifier)
            new_book = Trader.ItemInShop(item=book, price=price)
            books_list.append(new_book)
        self.update_index(books_list)
        self.goods_to_buy = books_list
        return True
    
    
    def show(self) -> str:
        return 'У стены, под лампой среди пыльных томов сидит торговец книгами.'
