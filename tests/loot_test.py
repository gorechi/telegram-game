import unittest
from src.class_basic import Loot, Money


class TestLootGetFirstItemByClass(unittest.TestCase):
    """Тесты метода Loot.get_first_item_by_class."""

    def setUp(self):
        self.loot = Loot(game=None)

    def test_returns_first_item_of_class(self):
        item_1 = Money(game=None, how_much_money=10)
        item_2 = Money(game=None, how_much_money=20)
        not_money = object()
        self.loot.pile = [item_1, not_money, item_2]
        result = self.loot.get_first_item_by_class('Money')
        self.assertIs(result, item_1)

    def test_returns_first_of_several_items_of_class(self):
        item_1 = Money(game=None, how_much_money=10)
        item_2 = Money(game=None, how_much_money=20)
        self.loot.pile = [item_1, item_2]
        result = self.loot.get_first_item_by_class('Money')
        self.assertIs(result, item_1)

    def test_returns_none_when_class_absent(self):
        self.loot.pile = [object()]
        self.assertIsNone(self.loot.get_first_item_by_class('Money'))

    def test_returns_none_when_loot_empty(self):
        self.assertIsNone(self.loot.get_first_item_by_class('Money'))


if __name__ == '__main__':
    unittest.main()
