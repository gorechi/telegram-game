import unittest
from unittest.mock import MagicMock

from src.class_basic import Loot, Money


class FakeItem:
    """Минимальная вещь, умеющая сравнивать своё имя."""

    def __init__(self, name='вещь'):
        self.name = name

    def check_name(self, message):
        return self.name.lower() == message.lower()


class BaseItem:
    pass


class Sword(BaseItem):
    pass


class TestLootInit(unittest.TestCase):
    """Тесты инициализации лута."""

    def test_init(self):
        game = MagicMock()
        loot = Loot(game)
        self.assertIs(loot.game, game)
        self.assertEqual(loot.pile, [])
        self.assertFalse(loot.empty)


class TestLootStr(unittest.TestCase):
    """Тесты строкового представления лута."""

    def test_str(self):
        self.assertEqual(str(Loot(None)), 'loot')


class TestLootAddDunder(unittest.TestCase):
    """Тесты метода Loot.__add__."""

    def setUp(self):
        self.loot = Loot(None)

    def test_merges_other_loot_and_returns_self(self):
        other = Loot(None)
        other.pile = [object()]
        result = self.loot + other
        self.assertIs(result, self.loot)
        self.assertEqual(self.loot.pile, other.pile)

    def test_returns_false_for_non_loot(self):
        result = self.loot + [object()]
        self.assertIs(result, False)
        self.assertEqual(self.loot.pile, [])


class TestLootAdd(unittest.TestCase):
    """Тесты метода Loot.add."""

    def test_add_appends_item(self):
        loot = Loot(None)
        item = object()
        loot.add(item)
        self.assertEqual(loot.pile, [item])


class TestLootRemove(unittest.TestCase):
    """Тесты метода Loot.remove."""

    def setUp(self):
        self.loot = Loot(None)
        self.item = object()
        self.loot.pile = [self.item]

    def test_remove_existing_item(self):
        self.loot.remove(self.item)
        self.assertEqual(self.loot.pile, [])

    def test_remove_absent_item_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.loot.remove(object())


class TestLootEq(unittest.TestCase):
    """Тесты сравнения лута с числом по количеству предметов."""

    def setUp(self):
        self.loot = Loot(None)
        self.loot.pile = [object(), object()]

    def test_eq_with_matching_count(self):
        self.assertTrue(self.loot == 2)

    def test_eq_with_different_count(self):
        self.assertFalse(self.loot == 3)

    def test_eq_with_non_int(self):
        self.assertFalse(self.loot == '2')


class TestLootIsItemInLoot(unittest.TestCase):
    """Тесты метода Loot.is_item_in_loot."""

    def setUp(self):
        self.loot = Loot(None)
        self.item = object()
        self.loot.pile = [self.item]

    def test_item_in_loot(self):
        self.assertTrue(self.loot.is_item_in_loot(self.item))

    def test_item_not_in_loot(self):
        self.assertFalse(self.loot.is_item_in_loot(object()))


class TestLootReveal(unittest.TestCase):
    """Тесты метода Loot.reveal."""

    def setUp(self):
        self.loot = Loot(None)
        self.item_1 = object()
        self.item_2 = object()
        self.loot.pile = [self.item_1, self.item_2]
        self.room = MagicMock()
        self.room.loot = Loot(None)

    def test_moves_items_to_room_and_adds_actions(self):
        result = self.loot.reveal(self.room)
        self.assertIs(result, True)
        self.assertEqual(self.room.loot.pile, [self.item_1, self.item_2])
        self.assertEqual(self.room.action_controller.add_actions.call_count, 2)

    def test_clears_loot_after_reveal(self):
        self.loot.reveal(self.room)
        self.assertEqual(self.loot.pile, [])


class TestLootClear(unittest.TestCase):
    """Тесты метода Loot.clear."""

    def test_clear_empties_pile(self):
        loot = Loot(None)
        loot.pile = [object()]
        loot.clear()
        self.assertEqual(loot.pile, [])


class TestLootTransfer(unittest.TestCase):
    """Тесты метода Loot.transfer."""

    def setUp(self):
        self.loot = Loot(None)
        self.items = [object(), object()]
        self.loot.pile = list(self.items)

    def test_transfer_to_loot(self):
        other = Loot(None)
        result = self.loot.transfer(other)
        self.assertIs(result, True)
        self.assertEqual(other.pile, self.items)
        self.assertEqual(self.loot.pile, [])

    def test_transfer_to_non_loot_returns_false(self):
        result = self.loot.transfer(MagicMock())
        self.assertIs(result, False)
        self.assertEqual(self.loot.pile, self.items)


class TestLootGetFirstItemByName(unittest.TestCase):
    """Тесты метода Loot.get_first_item_by_name."""

    def setUp(self):
        self.loot = Loot(None)
        self.axe = FakeItem('топор')
        self.rune = FakeItem('руна')
        self.loot.pile = [self.axe, self.rune]

    def test_returns_first_matching_item(self):
        self.assertIs(self.loot.get_first_item_by_name('топор'), self.axe)

    def test_returns_first_of_several_matches(self):
        self.loot.pile = [self.axe, FakeItem('топор')]
        self.assertIs(self.loot.get_first_item_by_name('топор'), self.axe)

    def test_returns_none_when_absent(self):
        self.assertIsNone(self.loot.get_first_item_by_name('руна2'))

    def test_returns_none_when_loot_empty(self):
        self.assertIsNone(Loot(None).get_first_item_by_name('топор'))


class TestLootGetAllItemsByName(unittest.TestCase):
    """Тесты метода Loot.get_all_items_by_name."""

    def setUp(self):
        self.loot = Loot(None)
        self.axe_1 = FakeItem('топор')
        self.axe_2 = FakeItem('топор')
        self.rune = FakeItem('руна')
        self.loot.pile = [self.axe_1, self.rune, self.axe_2]

    def test_returns_all_matching_items(self):
        result = self.loot.get_all_items_by_name('топор')
        self.assertEqual(result, [self.axe_1, self.axe_2])

    def test_returns_empty_list_when_absent(self):
        self.assertEqual(self.loot.get_all_items_by_name('нет'), [])

    def test_returns_empty_list_when_loot_empty(self):
        self.assertEqual(Loot(None).get_all_items_by_name('топор'), [])


class TestLootGetItemsByClass(unittest.TestCase):
    """Тесты метода Loot.get_items_by_class."""

    def setUp(self):
        self.loot = Loot(None)

    def test_returns_items_of_exact_class(self):
        item = Money(None, 10)
        self.loot.pile = [item]
        self.assertEqual(self.loot.get_items_by_class('Money'), [item])

    def test_returns_items_of_base_class_by_mro(self):
        sword = Sword()
        self.loot.pile = [sword]
        self.assertEqual(self.loot.get_items_by_class('BaseItem'), [sword])

    def test_returns_empty_list_when_absent(self):
        self.loot.pile = [object()]
        self.assertEqual(self.loot.get_items_by_class('Money'), [])


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

    def test_finds_item_by_base_class_name_via_mro(self):
        sword = Sword()
        self.loot.pile = [sword]
        self.assertIs(self.loot.get_first_item_by_class('BaseItem'), sword)

    def test_returns_none_when_class_absent(self):
        self.loot.pile = [object()]
        self.assertIsNone(self.loot.get_first_item_by_class('Money'))

    def test_returns_none_when_loot_empty(self):
        self.assertIsNone(self.loot.get_first_item_by_class('Money'))


class TestLootShowSorted(unittest.TestCase):
    """Тесты метода Loot.show_sorted."""

    def test_single_items_show_capitalized(self):
        loot = Loot(None)
        loot.pile = [FakeItem('руна'), FakeItem('топор')]
        self.assertEqual(loot.show_sorted(), ['Руна', 'Топор'])

    def test_duplicates_show_quantity_singular(self):
        loot = Loot(None)
        loot.pile = [FakeItem('топор'), FakeItem('топор')]
        self.assertEqual(loot.show_sorted(), ['Топор (2 штуки)'])

    def test_duplicates_show_quantity_plural(self):
        loot = Loot(None)
        loot.pile = [FakeItem('топор')] * 5
        self.assertEqual(loot.show_sorted(), ['Топор (5 штук)'])

    def test_items_without_name_are_skipped(self):
        loot = Loot(None)
        loot.pile = [FakeItem('топор'), object()]
        self.assertEqual(loot.show_sorted(), ['Топор'])

    def test_empty_loot(self):
        self.assertEqual(Loot(None).show_sorted(), [])


class TestLootAddMoney(unittest.TestCase):
    """Тесты добавления денег в лут."""

    def test_add_non_money_returns_false(self):
        loot = Loot(None)
        self.assertFalse(loot.add_money(FakeItem('вещь')))
        self.assertEqual(loot.pile, [])

    def test_add_money_to_empty_loot(self):
        loot = Loot(None)
        self.assertTrue(loot.add_money(Money(None, 5)))
        self.assertEqual(len(loot.pile), 1)
        self.assertIsInstance(loot.pile[0], Money)

    def test_add_money_merges_with_existing(self):
        loot = Loot(None)
        loot.add_money(Money(None, 5))
        loot.add_money(Money(None, 3))
        self.assertEqual(loot.pile[0].how_much_money, 8)


if __name__ == '__main__':
    unittest.main()
