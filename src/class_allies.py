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
    """Базовый класс для торговцев в игре. 
    Определяет общую логику торговли, хранения товаров, взаимодействия с игроком и генерации ассортимента.
    """

    _maximum_money = 50
    """Максимальное количество денег у торговца"""

    _minimum_money = 20
    """Минимальное количество денег у торговца"""

    @dataclass
    class ItemInShop:
        """Структура для хранения информации о товаре в магазине торговца."""
        item: Book | Rune | Potion | Matches
        price: int
        index: Optional[int] = None

    @classmethod
    def random_trader(cls, game, floor) -> 'Trader':
        """
        Создает и возвращает случайного торговца (одного из подклассов Trader).

        Args:
            game: Экземпляр текущей игры.
            floor: Этаж, на котором будет размещён торговец.

        Returns:
            Trader: Экземпляр случайного торговца.
        """
        trader_class = randomitem(cls.__subclasses__())
        new_trader = trader_class(game, floor)
        return new_trader

    @staticmethod
    def search_item_by_index(items_list: list, index: int) -> Union[Book, Rune, Potion, Matches, None]:
        """
        Ищет предмет в списке товаров по его индексу.

        Args:
            items_list (list): Список товаров (ItemInShop).
            index (int): Индекс искомого предмета.

        Returns:
            ItemInShop | None: Найденный товар или None, если не найден.
        """
        for item in items_list:
            if item.index == index:
                return item
        return None

    @staticmethod
    def search_item_by_name(items_list: list, name: str) -> Union[Book, Rune, Potion, Matches, None]:
        """
        Ищет предмет в списке товаров по его имени.

        Args:
            items_list (list): Список товаров (ItemInShop).
            name (str): Имя искомого предмета.

        Returns:
            ItemInShop | None: Найденный товар или None, если не найден.
        """
        if not name or not isinstance(name, str):
            raise ValueError('В метод search_item_by_name передано неверное имя объекта')
        for item in items_list:
            if item.item.check_name(name):
                return item
        return None

    def __init__(
        self,
        game,
        floor,
        name: str = '',
        lexemes: dict = None
    ):
        """
        Инициализирует торговца, задаёт его имя, этаж, стартовые деньги и добавляет в список всех торговцев.

        Args:
            game: Экземпляр текущей игры.
            floor: Этаж, на котором находится торговец.
            name (str, optional): Имя торговца.
            lexemes (dict, optional): Словарь с падежными формами имени.
        """
        self.game = game
        self.floor = floor
        self.name = name
        self.room = None
        self.lexemes = lexemes
        self.shop = []
        self.goods_to_buy = []
        self.money = self.generate_money()
        self.game.all_traders.append(self)

    def __format__(self, format: str) -> str:
        """
        Форматирует имя торговца в зависимости от падежа.

        Args:
            format (str): Ключ падежа (например, 'nom', 'gen').

        Returns:
            str: Имя торговца в нужном падеже.
        """
        if not self.lexemes:
            return self.name
        return self.lexemes.get(format, '')

    def sell(self, item_text: str, who) -> bool:
        """
        Продаёт предмет из магазина торговца герою.

        Args:
            item_text (str): Текстовое описание или индекс предмета.
            who: Герой, совершающий покупку.

        Returns:
            bool: True, если продажа успешна, иначе False.
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

    def buy(self, item_text: str, who) -> bool:
        """
        Покупает предмет у героя (герой продаёт торговцу).

        Args:
            item_text (str): Текстовое описание или индекс предмета.
            who: Герой, продающий предмет.

        Returns:
            bool: True, если покупка успешна, иначе False.
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
        Принимает деньги от героя (уменьшает деньги героя, увеличивает свои).

        Args:
            who: Герой, отдающий деньги.
            amount (int): Сумма.

        Returns:
            bool: True всегда.
        """
        who.money -= amount
        self.money += amount
        return True

    def give_money(self, who, amount) -> bool:
        """
        Отдаёт деньги герою (увеличивает деньги героя, уменьшает свои).

        Args:
            who: Герой, получающий деньги.
            amount (int): Сумма.

        Returns:
            bool: True всегда.
        """
        who.money += amount
        self.money -= amount
        return True

    def give_item(self, who, item_to_give: ItemInShop) -> bool:
        """
        Передаёт предмет герою, удаляет его из магазина и добавляет в список товаров, которые торговец готов купить обратно.

        Args:
            who: Герой, получающий предмет.
            item_to_give (ItemInShop): Товар для передачи.

        Returns:
            bool: True всегда.
        """
        item = item_to_give.item
        who.backpack.add(item)
        self.shop.remove(item_to_give)
        self.goods_to_buy.append(item_to_give)
        return True

    def take_item(self, who, item_to_take: ItemInShop) -> bool:
        """
        Принимает предмет от героя, добавляет его в магазин и удаляет из списка товаров на покупку.

        Args:
            who: Герой, отдающий предмет.
            item_to_take (ItemInShop): Товар для приёма.

        Returns:
            bool: True всегда.
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
        Генерирует случайное количество денег для торговца в заданных пределах.

        Returns:
            Money: Объект денег с сгенерированной суммой.
        """
        delta = Trader._maximum_money - Trader._minimum_money
        money_amount = Trader._minimum_money + roll([delta + 1]) - 1
        new_money = Money(self.game, money_amount)
        return new_money

    def get_item_by_text(self, text: str, mode: Literal['buy', 'sell']) -> Union[Book, Rune, Potion, Matches, None]:
        """
        Ищет предмет по тексту (имя или индекс) в зависимости от режима (покупка или продажа).

        Args:
            text (str): Имя или индекс предмета.
            mode (Literal['buy', 'sell']): Режим поиска ('buy' — покупка у героя, 'sell' — продажа герою).

        Returns:
            ItemInShop | None: Найденный товар или None.
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

    def update_index(self, list_of_items: list) -> bool:
        """
        Обновляет индексы товаров в переданном списке.

        Args:
            list_of_items (list): Список товаров (ItemInShop).

        Returns:
            bool: True всегда.
        """
        index = 0
        for item in list_of_items:
            index += 1
            item.index = index
        return True

    def update_indexes(self) -> None:
        """
        Обновляет индексы товаров в списках товаров на продажу и на покупку.
        """
        self.update_index(self.goods_to_buy)
        self.update_index(self.shop)

    def place(self, room=None):
        """
        Размещает торговца в комнате. Если комната не указана, выбирает случайную запертую комнату на этаже.

        Args:
            room (optional): Комната для размещения торговца.
        """
        if room and not room.trader:
            traders_room = room
        else:
            locked_rooms = [room for room in self.floor.plan if room.locked and not room.trader]
            free_rooms = [room for room in self.floor.plan if not room.trader]
            available_rooms = locked_rooms or free_rooms
            if not available_rooms:
                return False
            traders_room = randomitem(available_rooms)
        traders_room.trader = self
        traders_room.clear_from_monsters()
        traders_room.light = True
        self.room = traders_room
        if not self.room.can_rest(mode='simple'):
            new_rest_place = self.game.furniture_controller.get_random_object_by_filters(name="кресло")
            new_rest_place.place(room_to_place=self.room)
        return True

    def show_through_key_hole(self) -> str | list:
        """
        Возвращает описание того, что видно через замочную скважину в комнате с торговцем.

        Returns:
            str | list: Описание витрины торговца.
        """
        return 'Видно кусок витрины, наполненной разноцветными непонятными вещицами.'

    def get_prices(self, backpack: Backpack) -> list[str]:
        """
        Оценивает вещи в рюкзаке героя и возвращает список строк с ценами на продажу и покупку.

        Args:
            backpack (Backpack): Рюкзак героя.

        Returns:
            list[str]: Список строк с описанием цен.
        """
        self.evaluate_items(backpack)
        message = self.generate_selling_text()
        message.extend(self.generate_buying_text())
        return message

class Scribe(Trader):
    """Торговец-книжник. Продаёт и покупает книги."""

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

    def __init__(
        self,
        game,
        floor,
        name: str = '',
        lexemes: dict = None
    ):
        """
        Инициализирует книжника, задаёт имя, падежные формы и генерирует ассортимент книг.

        Args:
            game: Экземпляр текущей игры.
            floor: Этаж, на котором находится книжник.
            name (str, optional): Имя книжника.
            lexemes (dict, optional): Словарь с падежными формами имени.
        """
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
        Генерирует случайный ассортимент книг для продажи у книжника.

        Returns:
            bool: True всегда.
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

    def evaluate(self, book: Book) -> int:
        """
        Оценивает стоимость книги для продажи.

        Args:
            book (Book): Книга для оценки.

        Returns:
            int: Цена книги.
        """
        return book.base_price + roll(Scribe._sell_price_modifier)

    def generate_selling_text(self) -> list[str]:
        """
        Генерирует текстовое описание ассортимента книг на продажу.

        Returns:
            list[str]: Список строк с описанием книг и цен.
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
        Генерирует текстовое описание книг, которые книжник готов купить у героя.

        Returns:
            list[str]: Список строк с описанием книг и цен.
        """
        if not self.goods_to_buy:
            return ['Книжник не хочет ничего покупать у героя.']
        message = ['Книжник с удовольствием приобрел бы у героя следующие вещи по сходной цене:']
        for item in self.goods_to_buy:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message

    def evaluate_items(self, backpack: Backpack) -> bool:
        """
        Оценивает книги в рюкзаке героя для покупки книжником.

        Args:
            backpack (Backpack): Рюкзак героя.

        Returns:
            bool: True, если есть книги для покупки, иначе False.
        """
        books: list[Book] = backpack.get_items_by_class('Book')
        if not books:
            self.goods_to_buy.clear()
            return False
        books_list = []
        for book in books:
            price = max(1, book.base_price - roll(Scribe._buy_price_modifier))
            new_book = Trader.ItemInShop(item=book, price=price)
            books_list.append(new_book)
        self.update_index(books_list)
        self.goods_to_buy = books_list
        return True

    def show(self) -> str:
        """
        Возвращает описание книжника в комнате.

        Returns:
            str: Описание книжника.
        """
        return 'У стены, под лампой среди пыльных томов сидит торговец книгами.'

class RuneMerchant(Trader):
    """Торговец рунами. Продаёт и покупает руны."""

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

    def __init__(
        self,
        game,
        floor,
        name: str = 'Торговец рунами',
        lexemes: dict = None
    ):
        """
        Инициализирует торговца рунами, задаёт имя, падежные формы и генерирует ассортимент рун.

        Args:
            game: Экземпляр текущей игры.
            floor: Этаж, на котором находится торговец.
            name (str, optional): Имя торговца.
            lexemes (dict, optional): Словарь с падежными формами имени.
        """
        super().__init__(game, floor, name, lexemes)
        self.name = name
        self.lexemes = lexemes
        if not self.lexemes:
            self.lexemes = RuneMerchant._lexemes
        self.get_goods()

    def get_goods(self) -> bool:
        """
        Генерирует случайный ассортимент рун для продажи у торговца.

        Returns:
            bool: True всегда.
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

    def evaluate(self, rune: Rune) -> int:
        """
        Оценивает стоимость руны для продажи.

        Args:
            rune (Rune): Руна для оценки.

        Returns:
            int: Цена руны.
        """
        return rune.base_price + roll(RuneMerchant._sell_price_modifier)

    def generate_selling_text(self) -> list[str]:
        """
        Генерирует текстовое описание ассортимента рун на продажу.

        Returns:
            list[str]: Список строк с описанием рун и цен.
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
        Генерирует текстовое описание рун, которые торговец готов купить у героя.

        Returns:
            list[str]: Список строк с описанием рун и цен.
        """
        if not self.goods_to_buy:
            return ['Торговец рунами не хочет ничего покупать у героя.']
        message = ['Торговец рунами с удовольствием приобрел бы у героя следующие руны:']
        for item in self.goods_to_buy:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message

    def evaluate_items(self, backpack: Backpack) -> bool:
        """
        Оценивает руны в рюкзаке героя для покупки торговцем рунами.

        Args:
            backpack (Backpack): Рюкзак героя.

        Returns:
            bool: True, если есть руны для покупки, иначе False.
        """
        runes: list[Rune] = backpack.get_items_by_class('Rune')
        if not runes:
            self.goods_to_buy.clear()
            return False
        runes_list = []
        for rune in runes:
            price = max(1, rune.base_price - roll(RuneMerchant._buy_price_modifier))
            new_rune = Trader.ItemInShop(item=rune, price=price)
            runes_list.append(new_rune)
        self.goods_to_buy = runes_list
        self.update_indexes()
        return True

    def show(self) -> str:
        """
        Возвращает описание торговца рунами в комнате.

        Returns:
            str: Описание торговца рунами.
        """
        return 'Посреди комнаты стоит прилавок торговца рунами. Сам он суетится вокруг.'

class PotionsMerchant(Trader):
    """Торговец зельями. Продаёт и покупает зелья."""

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

    def __init__(
        self,
        game,
        floor,
        name: str = 'Торговец зельями',
        lexemes: dict = None
    ):
        """
        Инициализирует торговца зельями, задаёт имя, падежные формы и генерирует ассортимент зелий.

        Args:
            game: Экземпляр текущей игры.
            floor: Этаж, на котором находится торговец.
            name (str, optional): Имя торговца.
            lexemes (dict, optional): Словарь с падежными формами имени.
        """
        super().__init__(game, floor, name, lexemes)
        self.name = name
        self.lexemes = lexemes
        if not self.lexemes:
            self.lexemes = PotionsMerchant._lexemes
        self.get_goods()

    def get_goods(self) -> bool:
        """
        Генерирует случайный ассортимент зелий для продажи у торговца.

        Returns:
            bool: True всегда.
        """
        self.shop = []
        how_many_potions = roll([PotionsMerchant._potions_quantity_die])
        for _ in range(how_many_potions):
            potion = self.game.potions_controller.get_random_object_by_filters()
            price = self.evaluate(potion)
            new_potion = Trader.ItemInShop(item=potion, price=price)
            self.shop.append(new_potion)
        self.update_index(self.shop)
        return True

    def evaluate(self, potion: Potion) -> int:
        """
        Оценивает стоимость зелья для продажи.

        Args:
            potion (Potion): Зелье для оценки.

        Returns:
            int: Цена зелья.
        """
        return potion.base_price + roll(PotionsMerchant._sell_price_modifier)

    def generate_selling_text(self) -> list[str]:
        """
        Генерирует текстовое описание ассортимента зелий на продажу.

        Returns:
            list[str]: Список строк с описанием зелий и цен.
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
        Генерирует текстовое описание зелий, которые торговец готов купить у героя.

        Returns:
            list[str]: Список строк с описанием зелий и цен.
        """
        if not self.goods_to_buy:
            return ['Торговец зельями не хочет ничего покупать у героя.']
        message = ['Торговец зельями с удовольствием приобрел бы у героя следующие напитки:']
        for item in self.goods_to_buy:
            name = f'{item.item:nom}'
            price_text = howmany(item.price, ["монета", "монеты", "монет"])
            message.append(f'{item.index} - {name}: {price_text}')
        return message

    def evaluate_items(self, backpack: Backpack) -> bool:
        """
        Оценивает зелья в рюкзаке героя для покупки торговцем зельями.

        Args:
            backpack (Backpack): Рюкзак героя.

        Returns:
            bool: True, если есть зелья для покупки, иначе False.
        """
        potions: list[Potion] = backpack.get_items_by_class('Potion')
        if not potions:
            self.goods_to_buy.clear()
            return False
        potions_list = []
        for potion in potions:
            price = max(1, potion.base_price - roll(PotionsMerchant._buy_price_modifier))
            new_potion = Trader.ItemInShop(item=potion, price=price)
            potions_list.append(new_potion)
        self.goods_to_buy = potions_list
        self.update_indexes()
        return True

    def show(self) -> str:
        """
        Возвращает описание торговца зельями в комнате.

        Returns:
            str: Описание торговца зельями.
        """
        return 'Посреди комнаты стоит прилавок торговца зельями. Торговец занимается приготовлением какой-то микстуры.'