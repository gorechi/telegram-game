import unittest
from mock import MagicMock, patch
from src.class_items import Matches
from src.class_basic import Money
from src.class_allies import Trader
from src.controller_books import BooksController
from src.controller_runes import RunesController
from src.controller_potions import PotionsController
from src.functions.functions import howmany

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
        

if __name__ == '__main__':
    unittest.main()