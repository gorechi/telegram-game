import unittest
from unittest.mock import MagicMock, patch
from src.class_items import Matches
from src.class_basic import Money
from src.class_allies import Trader, Scribe, RuneMerchant, PotionsMerchant
from src.class_backpack import Backpack
from src.class_book import Book
from src.class_rune import Rune
from src.class_potions import Potion
from src.controllers.controller_books import BooksController
from src.controllers.controller_runes import RunesController
from src.controllers.controller_potions import PotionsController
from src.functions.functions import howmany


def make_game():
    game = MagicMock()
    game.all_traders = []
    game.books_controller = BooksController(game=game)
    game.runes_controller = RunesController(game=game)
    game.potions_controller = PotionsController(game=game)
    return game


def make_hero(game, money_amount=100):
    hero = MagicMock()
    hero.name = 'Герой'
    hero.money = Money(game, money_amount)
    hero.backpack = Backpack(game)
    hero.__format__ = MagicMock(return_value='Герой')
    return hero


def make_book(game, base_price=10):
    book = Book(game)
    book.base_price = base_price
    book.name = 'книга'
    book.lexemes = {'nom': 'книга', 'gen': 'книги', 'accus': 'книгу'}
    return book


def make_rune(game, base_price=15):
    rune = Rune(game)
    rune.base_price = base_price
    rune.name = 'руна'
    rune.lexemes = {'nom': 'руна', 'gen': 'руны', 'accus': 'руну'}
    return rune


def make_potion(game, base_price=5):
    potion = Potion(game)
    potion.base_price = base_price
    potion.name = 'зелье'
    potion.lexemes = {'nom': 'зелье', 'gen': 'зелья', 'accus': 'зелье'}
    return potion

class TestItemInShop(unittest.TestCase):
    def setUp(self):
        self.books_controller = BooksController(game=MagicMock())
        self.runes_controller = RunesController(game=MagicMock())
        self.potions_controller = PotionsController(game=MagicMock())
    
    def test_item_in_shop_initialization(self):
        # Test with a Book item
        book = self.books_controller.get_random_object_by_filters()
        item_in_shop = Trader.ItemInShop(item=book, price=10)
        self.assertEqual(item_in_shop.item, book)
        self.assertEqual(item_in_shop.price, 10)
        self.assertIsNone(item_in_shop.index)

        # Test with a Rune item
        rune = self.runes_controller.get_random_object_by_filters()
        item_in_shop = Trader.ItemInShop(item=rune, price=15, index=1)
        self.assertEqual(item_in_shop.item, rune)
        self.assertEqual(item_in_shop.price, 15)
        self.assertEqual(item_in_shop.index, 1)

        # Test with a Potion item
        potion = self.potions_controller.get_random_object_by_filters()
        item_in_shop = Trader.ItemInShop(item=potion, price=5)
        self.assertEqual(item_in_shop.item, potion)
        self.assertEqual(item_in_shop.price, 5)
        self.assertIsNone(item_in_shop.index)

        # Test with a Matches item
        matches = Matches(game=MagicMock())
        item_in_shop = Trader.ItemInShop(item=matches, price=3, index=2)
        self.assertEqual(item_in_shop.item, matches)
        self.assertEqual(item_in_shop.price, 3)
        self.assertEqual(item_in_shop.index, 2)

class TestSearchItemByIndex(unittest.TestCase):
    def setUp(self):
        self.books_controller = BooksController(game=MagicMock())
        self.runes_controller = RunesController(game=MagicMock())
        self.potions_controller = PotionsController(game=MagicMock())
        self.book = Trader.ItemInShop(item=self.books_controller.get_random_object_by_filters(), price=10, index=1)
        self.rune = Trader.ItemInShop(item=self.runes_controller.get_random_object_by_filters(), price=15, index=2)
        self.potion = Trader.ItemInShop(item=self.potions_controller.get_random_object_by_filters(), price=5, index=3)
        self.matches = Trader.ItemInShop(item=Matches(game=MagicMock()), price=3, index=4)
        self.items_list = [self.book, self.rune, self.potion, self.matches]

    def test_search_existing_index(self):
        # Test searching for an existing index
        result = Trader.search_item_by_index(self.items_list, 2)
        self.assertEqual(result, self.rune)

    def test_search_non_existing_index(self):
        # Test searching for a non-existing index
        result = Trader.search_item_by_index(self.items_list, 5)
        self.assertIsNone(result)

    def test_search_with_empty_list(self):
        # Test searching in an empty list
        result = Trader.search_item_by_index([], 1)
        self.assertIsNone(result)

    def test_search_with_none_index(self):
        # Test searching with None as index
        result = Trader.search_item_by_index(self.items_list, None)
        self.assertIsNone(result)

class TestSearchItemByName(unittest.TestCase):
    def setUp(self):
        self.books_controller = BooksController(game=MagicMock())
        self.runes_controller = RunesController(game=MagicMock())
        self.potions_controller = PotionsController(game=MagicMock())
        self.book = Trader.ItemInShop(item=self.books_controller.get_random_object_by_filters(), price=10, index=1)
        self.book.name = 'книга'
        self.rune = Trader.ItemInShop(item=self.runes_controller.get_random_object_by_filters(), price=15, index=2)
        self.rune.name = 'руна'
        self.potion = Trader.ItemInShop(item=self.potions_controller.get_random_object_by_filters(), price=5, index=3)
        self.potion.name = 'зелье'
        self.matches = Trader.ItemInShop(item=Matches(game=MagicMock()), price=3, index=4)
        self.matches.name = 'спички'
        self.items_list = [self.book, self.rune, self.potion, self.matches]

    def test_search_existing_name(self):
        # Test searching for an existing name
        result = Trader.search_item_by_name(self.items_list, 'книга')
        self.assertEqual(result, self.book)

    def test_search_non_existing_name(self):
        # Test searching for a non-existing name
        result = Trader.search_item_by_name(self.items_list, 'яблоко')
        self.assertIsNone(result)

    def test_search_with_empty_list(self):
        # Test searching in an empty list
        result = Trader.search_item_by_name([], 'книга')
        self.assertIsNone(result)

    def test_search_with_none_name(self):
        # Test searching with None as name
        with self.assertRaises(ValueError):
            Trader.search_item_by_name(self.items_list, None)
    
    def test_search_with_not_string_name(self):
        # Test searching with None as name
        with self.assertRaises(ValueError):
            Trader.search_item_by_name(self.items_list, 1)

class TestTraderInit(unittest.TestCase):

    def setUp(self):
        # Mocking the game and floor objects
        self.mock_game = MagicMock()
        self.mock_floor = MagicMock()
        self.mock_game.all_traders = []

    @patch('src.class_allies.Trader.generate_money')
    def test_trader_initialization(self, mock_generate_money):
        # Mock the return value of generate_money
        mock_money = MagicMock(spec=Money)
        mock_generate_money.return_value = mock_money

        # Initialize a Trader object
        trader = Trader(game=self.mock_game, floor=self.mock_floor, name='Test Trader', lexemes={'nom': 'Торговец'})

        # Check if attributes are set correctly
        self.assertEqual(trader.game, self.mock_game)
        self.assertEqual(trader.floor, self.mock_floor)
        self.assertEqual(trader.name, 'Test Trader')
        self.assertEqual(trader.lexemes, {'nom': 'Торговец'})
        self.assertEqual(trader.shop, [])
        self.assertEqual(trader.goods_to_buy, [])
        self.assertIsNone(trader.room)

        # Check if generate_money method is called and money is set
        mock_generate_money.assert_called_once()
        self.assertEqual(trader.money, mock_money)

        # Check if the trader is added to the game's list of traders
        self.assertIn(trader, self.mock_game.all_traders)
    
class TestTraderFormatMethod(unittest.TestCase):

    def setUp(self):
        # Mocking the game and floor objects
        self.mock_game = MagicMock()
        self.mock_floor = MagicMock()

        # Sample lexemes dictionary
        self.lexemes = {
            'nom': 'Торговец',
            'gen': 'Торговца',
            'dat': 'Торговцу',
            'accus': 'Торговца'
        }

        # Initialize a Trader object
        self.trader = Trader(game=self.mock_game, floor=self.mock_floor, name='Test Trader', lexemes=self.lexemes)

    def test_format_existing_key(self):
        # Test for an existing key in lexemes
        self.assertEqual(format(self.trader, 'nom'), 'Торговец')
        self.assertEqual(format(self.trader, 'gen'), 'Торговца')
        self.assertEqual(format(self.trader, 'dat'), 'Торговцу')
        self.assertEqual(format(self.trader, 'accus'), 'Торговца')

    def test_format_f_string_existing_key(self):
        # Test for an existing key in lexemes
        self.assertEqual(f'{self.trader:nom}', 'Торговец')
        self.assertEqual(f'{self.trader:gen}', 'Торговца')
        self.assertEqual(f'{self.trader:dat}', 'Торговцу')
        self.assertEqual(f'{self.trader:accus}', 'Торговца')
        
    def test_format_non_existing_key(self):
        # Test for a non-existing key in lexemes
        self.assertEqual(format(self.trader, 'nonexistent'), '')
        self.assertEqual(f'{self.trader:nonexistent}', '')

    def test_format_without_lexemes_returns_name(self):
        # Test that formatting does not crash when lexemes is None
        trader = Trader(game=self.mock_game, floor=self.mock_floor, name='Торговец')
        self.assertIsNone(trader.lexemes)
        self.assertEqual(format(trader, 'nom'), 'Торговец')
        self.assertEqual(f'{trader:nom}', 'Торговец')
        

class TestTraderPlace(unittest.TestCase):

    def setUp(self):
        self.mock_game = MagicMock()
        self.mock_game.all_traders = []
        self.mock_game.furniture_controller = MagicMock()
        self.mock_floor = MagicMock()

    def make_room(self, locked=False, trader=None):
        room = MagicMock()
        room.locked = locked
        room.trader = trader
        room.light = False
        room.can_rest.return_value = True
        return room

    def test_place_in_locked_room(self):
        free_room = self.make_room(locked=False)
        locked_room = self.make_room(locked=True)
        self.mock_floor.plan = [free_room, locked_room]
        trader = Trader(game=self.mock_game, floor=self.mock_floor)
        result = trader.place()
        self.assertTrue(result)
        self.assertEqual(trader.room, locked_room)
        self.assertEqual(locked_room.trader, trader)

    def test_place_without_locked_rooms_falls_back_to_free_room(self):
        first = self.make_room(locked=False)
        second = self.make_room(locked=False)
        self.mock_floor.plan = [first, second]
        trader = Trader(game=self.mock_game, floor=self.mock_floor)
        result = trader.place()
        self.assertTrue(result)
        self.assertIsNotNone(trader.room)
        self.assertIn(trader.room, [first, second])
        self.assertTrue(trader.room.light)

    def test_place_with_no_free_rooms_returns_false(self):
        occupied = self.make_room(locked=True, trader=object())
        self.mock_floor.plan = [occupied]
        trader = Trader(game=self.mock_game, floor=self.mock_floor)
        result = trader.place()
        self.assertFalse(result)
        self.assertIsNone(trader.room)

    def test_place_explicit_occupied_room_is_ignored(self):
        locked_room = self.make_room(locked=True)
        occupied_room = self.make_room(locked=True, trader=object())
        self.mock_floor.plan = [locked_room, occupied_room]
        trader = Trader(game=self.mock_game, floor=self.mock_floor)
        result = trader.place(room=occupied_room)
        self.assertTrue(result)
        self.assertEqual(trader.room, locked_room)

    def test_place_explicit_free_room(self):
        room = self.make_room(locked=False)
        self.mock_floor.plan = [room]
        trader = Trader(game=self.mock_game, floor=self.mock_floor)
        result = trader.place(room=room)
        self.assertTrue(result)
        self.assertEqual(trader.room, room)
        self.assertEqual(room.trader, trader)


class TestEvaluateItemsPriceFloor(unittest.TestCase):

    def make_game(self):
        game = MagicMock()
        game.all_traders = []
        game.books_controller.get_random_object_by_filters.side_effect = lambda: MagicMock(base_price=1)
        game.runes_controller.get_random_object_by_filters.side_effect = lambda: MagicMock(base_price=1)
        game.potions_controller.get_random_object_by_filters.side_effect = lambda: MagicMock(base_price=1)
        return game

    @patch('src.class_allies.roll', return_value=99)
    def test_buy_prices_never_below_one(self, mock_roll):
        game = self.make_game()
        floor = MagicMock()
        for cls in (Scribe, RuneMerchant, PotionsMerchant):
            merchant = cls(game, floor)
            backpack = MagicMock()
            backpack.get_items_by_class.return_value = [MagicMock(base_price=1)]
            merchant.evaluate_items(backpack)
            self.assertEqual(merchant.goods_to_buy[0].price, 1, cls.__name__)


class TestTraderSell(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = Scribe(self.game, MagicMock())
        self.hero = make_hero(self.game, 100)

    @patch('src.class_allies.tprint')
    def test_sell_success(self, mock_tprint):
        item = self.merchant.shop[0]
        price = item.price
        result = self.merchant.sell(str(item.index), self.hero)
        self.assertTrue(result)
        self.assertEqual(self.hero.money.get_sum(), 100 - price)
        self.assertIn(item.item, self.hero.backpack.insides)
        self.assertNotIn(item, self.merchant.shop)
        self.assertIn(item, self.merchant.goods_to_buy)
        mock_tprint.assert_called_once()

    @patch('src.class_allies.tprint')
    def test_sell_item_not_found(self, mock_tprint):
        result = self.merchant.sell('99', self.hero)
        self.assertFalse(result)
        self.assertEqual(self.hero.money.get_sum(), 100)
        self.assertEqual(len(self.hero.backpack.insides), 0)
        mock_tprint.assert_called_once()

    @patch('src.class_allies.tprint')
    def test_sell_not_enough_money(self, mock_tprint):
        hero = make_hero(self.game, 0)
        item = self.merchant.shop[0]
        shop_len = len(self.merchant.shop)
        result = self.merchant.sell(str(item.index), hero)
        self.assertFalse(result)
        self.assertEqual(hero.money.get_sum(), 0)
        self.assertEqual(len(self.merchant.shop), shop_len)
        self.assertEqual(len(hero.backpack.insides), 0)
        mock_tprint.assert_called_once()


class TestTraderBuy(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = Scribe(self.game, MagicMock())
        self.book = make_book(self.game)
        self.hero = make_hero(self.game, 100)
        self.hero.backpack.append(self.book)
        self.merchant.evaluate_items(self.hero.backpack)

    @patch('src.class_allies.tprint')
    def test_buy_success(self, mock_tprint):
        item = self.merchant.goods_to_buy[0]
        price = item.price
        result = self.merchant.buy(str(item.index), self.hero)
        self.assertTrue(result)
        self.assertEqual(self.hero.money.get_sum(), 100 + price)
        self.assertNotIn(self.book, self.hero.backpack.insides)
        self.assertIn(item, self.merchant.shop)
        self.assertNotIn(item, self.merchant.goods_to_buy)
        mock_tprint.assert_called_once()

    @patch('src.class_allies.tprint')
    def test_buy_item_not_found(self, mock_tprint):
        result = self.merchant.buy('99', self.hero)
        self.assertFalse(result)
        self.assertEqual(self.hero.money.get_sum(), 100)
        self.assertIn(self.book, self.hero.backpack.insides)
        mock_tprint.assert_called_once()

    @patch('src.class_allies.tprint')
    def test_buy_not_enough_money(self, mock_tprint):
        self.merchant.money = Money(self.game, 0)
        item = self.merchant.goods_to_buy[0]
        result = self.merchant.buy(str(item.index), self.hero)
        self.assertFalse(result)
        self.assertEqual(self.hero.money.get_sum(), 100)
        self.assertIn(self.book, self.hero.backpack.insides)
        self.assertIn(item, self.merchant.goods_to_buy)
        mock_tprint.assert_called_once()


class TestTraderMoney(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = Trader(self.game, MagicMock(), name='Торговец')
        self.hero = make_hero(self.game, 100)

    def test_take_money(self):
        initial = self.merchant.money.get_sum()
        result = self.merchant.take_money(self.hero, 10)
        self.assertTrue(result)
        self.assertEqual(self.hero.money.get_sum(), 90)
        self.assertEqual(self.merchant.money.get_sum(), initial + 10)

    def test_give_money(self):
        initial = self.merchant.money.get_sum()
        result = self.merchant.give_money(self.hero, 10)
        self.assertTrue(result)
        self.assertEqual(self.hero.money.get_sum(), 110)
        self.assertEqual(self.merchant.money.get_sum(), initial - 10)


class TestTraderGiveTakeItem(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = Scribe(self.game, MagicMock())
        self.hero = make_hero(self.game, 100)

    def test_give_item(self):
        item = self.merchant.shop[0]
        result = self.merchant.give_item(self.hero, item)
        self.assertTrue(result)
        self.assertIn(item.item, self.hero.backpack.insides)
        self.assertNotIn(item, self.merchant.shop)
        self.assertIn(item, self.merchant.goods_to_buy)

    @patch('src.class_allies.roll', return_value=2)
    def test_take_item(self, mock_roll):
        item = self.merchant.shop[0]
        self.merchant.give_item(self.hero, item)
        shop_len = len(self.merchant.shop)
        result = self.merchant.take_item(self.hero, item)
        self.assertTrue(result)
        self.assertNotIn(item.item, self.hero.backpack.insides)
        self.assertIn(item, self.merchant.shop)
        self.assertEqual(len(self.merchant.shop), shop_len + 1)
        self.assertNotIn(item, self.merchant.goods_to_buy)
        self.assertEqual(item.price, item.item.base_price + 2)


class TestTraderGetItemByText(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = Scribe(self.game, MagicMock())

    def test_sell_mode_by_index(self):
        item = self.merchant.shop[0]
        result = self.merchant.get_item_by_text(str(item.index), 'sell')
        self.assertIs(result, item)

    def test_sell_mode_by_name(self):
        item = self.merchant.shop[0]
        result = self.merchant.get_item_by_text('книга', 'sell')
        self.assertIs(result, item)

    def test_buy_mode(self):
        hero = make_hero(self.game, 100)
        book = make_book(self.game)
        hero.backpack.append(book)
        self.merchant.evaluate_items(hero.backpack)
        item = self.merchant.goods_to_buy[0]
        result = self.merchant.get_item_by_text(str(item.index), 'buy')
        self.assertIs(result, item)

    def test_invalid_mode(self):
        self.assertIsNone(self.merchant.get_item_by_text('1', 'invalid'))


class TestTraderRandomTrader(unittest.TestCase):

    @patch('src.class_allies.randomitem', return_value=Scribe)
    def test_returns_subclass_instance(self, mock_randomitem):
        game = make_game()
        trader = Trader.random_trader(game, MagicMock())
        self.assertIsInstance(trader, Trader)
        self.assertIsInstance(trader, Scribe)


class TestTraderGenerateMoney(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.min_original = Trader._minimum_money
        self.max_original = Trader._maximum_money
        Trader._minimum_money = 10
        Trader._maximum_money = 20

    def tearDown(self):
        Trader._minimum_money = self.min_original
        Trader._maximum_money = self.max_original

    @patch('src.class_allies.roll', return_value=1)
    def test_generate_money_min_bound(self, mock_roll):
        trader = Trader(self.game, MagicMock())
        self.assertEqual(trader.money.get_sum(), 10)

    @patch('src.class_allies.roll', return_value=11)
    def test_generate_money_max_bound(self, mock_roll):
        trader = Trader(self.game, MagicMock())
        self.assertEqual(trader.money.get_sum(), 20)

    @patch('src.class_allies.roll', return_value=5)
    def test_generate_money_middle(self, mock_roll):
        trader = Trader(self.game, MagicMock())
        self.assertEqual(trader.money.get_sum(), 14)


class TestTraderShowThroughKeyHole(unittest.TestCase):

    def test_returns_description(self):
        game = make_game()
        trader = Scribe(game, MagicMock())
        self.assertEqual(
            trader.show_through_key_hole(),
            'Видно кусок витрины, наполненной разноцветными непонятными вещицами.')


class TestTraderGetPrices(unittest.TestCase):

    def test_get_prices(self):
        game = make_game()
        trader = Scribe(game, MagicMock())
        hero = make_hero(game, 100)
        message = trader.get_prices(hero.backpack)
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)
        self.assertEqual(message[-1], 'Книжник не хочет ничего покупать у героя.')


class TestTraderUpdateIndex(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.trader = Trader(self.game, MagicMock(), name='Торговец')

    def test_update_index(self):
        items = [Trader.ItemInShop(item=object(), price=1, index=None) for _ in range(3)]
        self.assertTrue(self.trader.update_index(items))
        self.assertEqual([item.index for item in items], [1, 2, 3])

    def test_update_indexes(self):
        self.trader.shop = [Trader.ItemInShop(item=object(), price=1) for _ in range(2)]
        self.trader.goods_to_buy = [Trader.ItemInShop(item=object(), price=1)]
        self.trader.update_indexes()
        self.assertEqual([item.index for item in self.trader.shop], [1, 2])
        self.assertEqual([item.index for item in self.trader.goods_to_buy], [1])


class TestScribeMethods(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.scribe = Scribe(self.game, MagicMock())

    @patch('src.class_allies.roll', return_value=3)
    def test_get_goods(self, mock_roll):
        self.scribe.get_goods()
        self.assertEqual(len(self.scribe.shop), 3)
        self.assertEqual([item.index for item in self.scribe.shop], [1, 2, 3])

    @patch('src.class_allies.roll', return_value=2)
    def test_evaluate(self, mock_roll):
        book = self.game.books_controller.get_random_object_by_filters()
        self.assertEqual(self.scribe.evaluate(book), book.base_price + 2)

    def test_generate_selling_text_with_items(self):
        message = self.scribe.generate_selling_text()
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)

    def test_generate_selling_text_empty(self):
        self.scribe.shop = []
        self.assertEqual(
            self.scribe.generate_selling_text(),
            ['На полках торговца пусто. Ему нечего предложить на продажу.'])

    def test_generate_buying_text_with_items(self):
        hero = make_hero(self.game, 100)
        book = make_book(self.game)
        hero.backpack.append(book)
        self.scribe.evaluate_items(hero.backpack)
        message = self.scribe.generate_buying_text()
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)

    def test_generate_buying_text_empty(self):
        self.assertEqual(
            self.scribe.generate_buying_text(),
            ['Книжник не хочет ничего покупать у героя.'])

    def test_evaluate_items_with_books(self):
        hero = make_hero(self.game, 100)
        book = make_book(self.game)
        hero.backpack.append(book)
        result = self.scribe.evaluate_items(hero.backpack)
        self.assertTrue(result)
        self.assertEqual(len(self.scribe.goods_to_buy), 1)
        self.assertEqual(self.scribe.goods_to_buy[0].index, 1)

    def test_evaluate_items_without_books(self):
        hero = make_hero(self.game, 100)
        result = self.scribe.evaluate_items(hero.backpack)
        self.assertFalse(result)
        self.assertEqual(self.scribe.goods_to_buy, [])

    def test_show(self):
        self.assertEqual(
            self.scribe.show(),
            'У стены, под лампой среди пыльных томов сидит торговец книгами.')

    def test_init_with_explicit_name_and_lexemes(self):
        lexemes = {'nom': 'Василий', 'gen': 'Василия'}
        scribe = Scribe(self.game, MagicMock(), name='Василий', lexemes=lexemes)
        self.assertEqual(scribe.name, 'Василий')
        self.assertEqual(scribe.lexemes, lexemes)


class TestRuneMerchantMethods(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = RuneMerchant(self.game, MagicMock())

    @patch('src.class_allies.roll', return_value=3)
    def test_get_goods(self, mock_roll):
        self.merchant.get_goods()
        self.assertEqual(len(self.merchant.shop), 3)
        self.assertEqual([item.index for item in self.merchant.shop], [1, 2, 3])

    @patch('src.class_allies.roll', return_value=2)
    def test_evaluate(self, mock_roll):
        rune = make_rune(self.game)
        self.assertEqual(self.merchant.evaluate(rune), rune.base_price + 2)

    def test_generate_selling_text_with_items(self):
        message = self.merchant.generate_selling_text()
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)

    def test_generate_selling_text_empty(self):
        self.merchant.shop = []
        self.assertEqual(
            self.merchant.generate_selling_text(),
            ['В сундуках торговца пусто. Ему нечего предложить на продажу.'])

    def test_generate_buying_text_with_items(self):
        hero = make_hero(self.game, 100)
        rune = make_rune(self.game)
        hero.backpack.append(rune)
        self.merchant.evaluate_items(hero.backpack)
        message = self.merchant.generate_buying_text()
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)

    def test_generate_buying_text_empty(self):
        self.assertEqual(
            self.merchant.generate_buying_text(),
            ['Торговец рунами не хочет ничего покупать у героя.'])

    def test_evaluate_items_with_runes(self):
        hero = make_hero(self.game, 100)
        rune = make_rune(self.game)
        hero.backpack.append(rune)
        result = self.merchant.evaluate_items(hero.backpack)
        self.assertTrue(result)
        self.assertEqual(len(self.merchant.goods_to_buy), 1)
        self.assertEqual(self.merchant.goods_to_buy[0].index, 1)

    def test_evaluate_items_without_runes(self):
        hero = make_hero(self.game, 100)
        result = self.merchant.evaluate_items(hero.backpack)
        self.assertFalse(result)
        self.assertEqual(self.merchant.goods_to_buy, [])

    def test_show(self):
        self.assertEqual(
            self.merchant.show(),
            'Посреди комнаты стоит прилавок торговца рунами. Сам он суетится вокруг.')

    def test_init_with_explicit_name_and_lexemes(self):
        lexemes = {'nom': 'Руноторг', 'gen': 'Руноторга'}
        merchant = RuneMerchant(self.game, MagicMock(), name='Руноторг', lexemes=lexemes)
        self.assertEqual(merchant.name, 'Руноторг')
        self.assertEqual(merchant.lexemes, lexemes)


class TestPotionsMerchantMethods(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.merchant = PotionsMerchant(self.game, MagicMock())

    @patch('src.class_allies.roll', return_value=3)
    def test_get_goods(self, mock_roll):
        self.merchant.get_goods()
        self.assertEqual(len(self.merchant.shop), 3)
        self.assertEqual([item.index for item in self.merchant.shop], [1, 2, 3])

    @patch('src.class_allies.roll', return_value=2)
    def test_evaluate(self, mock_roll):
        potion = make_potion(self.game)
        self.assertEqual(self.merchant.evaluate(potion), potion.base_price + 2)

    def test_generate_selling_text_with_items(self):
        message = self.merchant.generate_selling_text()
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)

    def test_generate_selling_text_empty(self):
        self.merchant.shop = []
        self.assertEqual(
            self.merchant.generate_selling_text(),
            ['В сундуках торговца пусто. Ему нечего предложить на продажу.'])

    def test_generate_buying_text_with_items(self):
        hero = make_hero(self.game, 100)
        potion = make_potion(self.game)
        hero.backpack.append(potion)
        self.merchant.evaluate_items(hero.backpack)
        message = self.merchant.generate_buying_text()
        self.assertIsInstance(message, list)
        self.assertGreater(len(message), 1)

    def test_generate_buying_text_empty(self):
        self.assertEqual(
            self.merchant.generate_buying_text(),
            ['Торговец зельями не хочет ничего покупать у героя.'])

    def test_evaluate_items_with_potions(self):
        hero = make_hero(self.game, 100)
        potion = make_potion(self.game)
        hero.backpack.append(potion)
        result = self.merchant.evaluate_items(hero.backpack)
        self.assertTrue(result)
        self.assertEqual(len(self.merchant.goods_to_buy), 1)
        self.assertEqual(self.merchant.goods_to_buy[0].index, 1)

    def test_evaluate_items_without_potions(self):
        hero = make_hero(self.game, 100)
        result = self.merchant.evaluate_items(hero.backpack)
        self.assertFalse(result)
        self.assertEqual(self.merchant.goods_to_buy, [])

    def test_show(self):
        self.assertEqual(
            self.merchant.show(),
            'Посреди комнаты стоит прилавок торговца зельями. '
            'Торговец занимается приготовлением какой-то микстуры.')

    def test_init_with_explicit_name_and_lexemes(self):
        lexemes = {'nom': 'Алхимик', 'gen': 'Алхимика'}
        merchant = PotionsMerchant(self.game, MagicMock(), name='Алхимик', lexemes=lexemes)
        self.assertEqual(merchant.name, 'Алхимик')
        self.assertEqual(merchant.lexemes, lexemes)


if __name__ == '__main__':
    unittest.main()