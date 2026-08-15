import unittest
from unittest.mock import MagicMock

from src.class_basic import Loot, Money


class TestMoneyInit(unittest.TestCase):
    """Тесты инициализации денег."""

    def test_init(self):
        game = MagicMock()
        money = Money(game, 5)
        self.assertIs(money.game, game)
        self.assertEqual(money.how_much_money, 5)
        self.assertFalse(money.empty)
        self.assertEqual(money.name, 'несколько монет')
        self.assertEqual(money.hero_actions, {})
        self.assertEqual(money.room_actions['взять']['method'], 'take')
        self.assertEqual(money.room_actions['брать']['method'], 'take')
        self.assertEqual(money.room_actions['собрать']['method'], 'take')


class TestMoneyGenerateName(unittest.TestCase):
    """Тесты выбора имени кучи в зависимости от количества."""

    def test_amount_0_to_10(self):
        for amount in (0, 5, 10):
            self.assertEqual(Money(None, amount).name, 'несколько монет')

    def test_amount_11_to_20(self):
        for amount in (11, 15, 20):
            self.assertEqual(Money(None, amount).name, 'кучка монет')

    def test_amount_21_to_30(self):
        for amount in (21, 25, 30):
            self.assertEqual(Money(None, amount).name, 'груда монет')

    def test_amount_more_than_30(self):
        for amount in (31, 50, 100):
            self.assertEqual(Money(None, amount).name, 'много монет')

    def test_negative_amount(self):
        for amount in (-1, -100):
            self.assertEqual(Money(None, amount).name, 'деньги')


class TestMoneyCheckName(unittest.TestCase):
    """Тесты метода Money.check_name."""

    def setUp(self):
        self.money = Money(None, 5)

    def test_accepts_generic_word(self):
        self.assertTrue(self.money.check_name('деньги'))
        self.assertTrue(self.money.check_name('ДЕНЬГИ'))

    def test_accepts_lexemes(self):
        self.assertTrue(self.money.check_name('несколько монет'))

    def test_rejects_other_words(self):
        self.assertFalse(self.money.check_name('монеты'))
        self.assertFalse(self.money.check_name('золото'))


class TestMoneyFormat(unittest.TestCase):
    """Тесты форматирования денег в падежах."""

    def test_known_case(self):
        money = Money(None, 5)
        self.assertEqual(format(money, 'nom'), 'несколько монет')
        self.assertEqual(format(money, 'gen'), 'нескольких монет')

    def test_unknown_case_returns_empty_string(self):
        self.assertEqual(format(Money(None, 5), 'zzz'), '')


class TestMoneyRepr(unittest.TestCase):
    """Тесты строкового представления денег."""

    def test_repr(self):
        self.assertEqual(repr(Money(None, 5)), '5')


class TestMoneyInt(unittest.TestCase):
    """Тесты приведения денег к целому числу."""

    def test_int(self):
        self.assertEqual(int(Money(None, 5)), 5)


class TestMoneyEq(unittest.TestCase):
    """Тесты сравнения денег."""

    def setUp(self):
        self.money = Money(None, 5)

    def test_eq_with_int(self):
        self.assertTrue(self.money == 5)
        self.assertFalse(self.money == 6)

    def test_eq_with_money(self):
        self.assertTrue(self.money == Money(None, 5))
        self.assertFalse(self.money == Money(None, 6))

    def test_eq_with_non_int_returns_none(self):
        self.assertIsNone(self.money == '5')
        self.assertIsNone(self.money == 5.0)


class TestMoneyComparisons(unittest.TestCase):
    """Тесты операторов сравнения с числом и объектом Money."""

    def setUp(self):
        self.money = Money(None, 5)

    def test_ge(self):
        self.assertTrue(self.money >= 5)
        self.assertTrue(self.money >= Money(None, 5))
        self.assertFalse(self.money >= 6)
        self.assertIsNone(self.money >= '5')

    def test_gt(self):
        self.assertTrue(self.money > 4)
        self.assertTrue(self.money > Money(None, 4))
        self.assertFalse(self.money > 5)
        self.assertIsNone(self.money > '5')

    def test_le(self):
        self.assertTrue(self.money <= 5)
        self.assertTrue(self.money <= Money(None, 5))
        self.assertFalse(self.money <= 4)
        self.assertIsNone(self.money <= '5')

    def test_lt(self):
        self.assertTrue(self.money < 6)
        self.assertTrue(self.money < Money(None, 6))
        self.assertFalse(self.money < 5)
        self.assertIsNone(self.money < '5')


class TestMoneyAdd(unittest.TestCase):
    """Тесты сложения денег."""

    def test_add_int(self):
        money = Money(None, 5)
        result = money + 3
        self.assertIs(result, money)
        self.assertEqual(money.how_much_money, 8)
        self.assertEqual(money.name, 'несколько монет')

    def test_add_money(self):
        money = Money(None, 5)
        result = money + Money(None, 10)
        self.assertIs(result, money)
        self.assertEqual(money.how_much_money, 15)
        self.assertEqual(money.name, 'кучка монет')


class TestMoneySub(unittest.TestCase):
    """Тесты вычитания денег."""

    def test_sub_int(self):
        money = Money(None, 20)
        result = money - 5
        self.assertIs(result, money)
        self.assertEqual(money.how_much_money, 15)
        self.assertEqual(money.name, 'кучка монет')

    def test_sub_money(self):
        money = Money(None, 20)
        result = money - Money(None, 15)
        self.assertIs(result, money)
        self.assertEqual(money.how_much_money, 5)
        self.assertEqual(money.name, 'несколько монет')


class TestMoneyTake(unittest.TestCase):
    """Тесты метода Money.take."""

    def test_take(self):
        money = Money(None, 5)
        who = MagicMock()
        who.name = 'Герой'
        who.g = MagicMock(return_value='забрал')
        room = MagicMock()
        room.loot = Loot(None)
        room.loot.add(money)
        who.money = Money(None, 3)
        who.current_position = room
        result = money.take(who)
        self.assertEqual(who.money.how_much_money, 8)
        self.assertEqual(room.loot.pile, [])
        self.assertEqual(result, 'Герой забрал 5 монет')


class TestMoneyShow(unittest.TestCase):
    """Тесты метода Money.show."""

    def test_show_positive(self):
        self.assertEqual(Money(None, 1).show(), '1 монета')
        self.assertEqual(Money(None, 2).show(), '2 монеты')
        self.assertEqual(Money(None, 5).show(), '5 монет')
        self.assertEqual(Money(None, 21).show(), '21 монета')

    def test_show_zero(self):
        self.assertEqual(Money(None, 0).show(), 'Денег нет')

    def test_show_negative(self):
        self.assertEqual(Money(None, -5).show(), 'Денег нет')


class TestMoneyGetSum(unittest.TestCase):
    """Тесты метода Money.get_sum."""

    def test_get_sum(self):
        self.assertEqual(Money(None, 42).get_sum(), 42)


class TestMoneyGetNamesList(unittest.TestCase):
    """Тесты метода Money.get_names_list."""

    def setUp(self):
        self.money = Money(None, 5)

    def test_default_names(self):
        self.assertEqual(self.money.get_names_list(), ['деньги', 'монеты'])

    def test_with_cases(self):
        names = self.money.get_names_list(['nom', 'gen'])
        self.assertEqual(
            names,
            ['деньги', 'монеты', 'несколько монет', 'нескольких монет']
        )

    def test_without_cases_argument(self):
        self.assertEqual(self.money.get_names_list(None), ['деньги', 'монеты'])

    def test_cases_not_a_list(self):
        self.assertEqual(self.money.get_names_list('nom'), ['деньги', 'монеты'])


if __name__ == '__main__':
    unittest.main()
