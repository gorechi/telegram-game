import unittest
from unittest.mock import MagicMock

from src.class_book import (
    Book,
    ThrustingWeaponBook,
    CuttingWeaponBook,
    BluntWeaponBook,
    TrapsBook,
    WisdomBook,
    ShieldsBook,
    ArmorBook,
)
from src.class_backpack import Backpack


def make_lexemes():
    return {
        'nom': 'Старая книга о мушкетерах',
        'accus': 'Старую книгу о мушкетерах',
        'gen': 'Старой книги о мушкетерах',
    }


class FakeWho:
    """Заглушка героя с минимальным набором атрибутов."""

    def __init__(self, mastery=None):
        self.name = 'Герой'
        self.mastery = mastery or {}
        self.gender = 0
        self.g = MagicMock(side_effect=lambda m, f: m)
        self.current_position = MagicMock()
        self.current_position.loot = MagicMock()
        self.current_position.action_controller = MagicMock()
        self.backpack = MagicMock()
        self.backpack.no_backpack = False
        self.action_controller = MagicMock()
        self.trap_mastery = 0
        self.intel = MagicMock()
        self.start_intel = MagicMock()
        self.put_in_backpack = MagicMock()

    def __format__(self, fmt):
        return 'он' if fmt == 'pronoun' else ''


def make_book(cls=Book, game=None, **attrs):
    book = cls(game)
    book.lexemes = make_lexemes()
    book.name = book.lexemes['nom']
    book.text = 'Текст книги.'
    book.examine_text = 'Полезная книга.'
    for key, value in attrs.items():
        setattr(book, key, value)
    return book


class TestBookInit(unittest.TestCase):
    """Тесты инициализации книги."""

    def setUp(self):
        self.book = Book(game=None)

    def test_init(self):
        self.assertIsNone(self.book.game)
        self.assertFalse(self.book.empty)

    def test_hero_actions_use(self):
        for action in ('читать', 'прочитать', 'почитать'):
            self.assertEqual(self.book.hero_actions[action]['method'], 'use')

    def test_hero_actions_drop(self):
        for action in ('бросить', 'выбросить', 'оставить'):
            self.assertEqual(self.book.hero_actions[action]['method'], 'drop')

    def test_hero_actions_examine(self):
        for action in ('осмотреть', 'оглядеть'):
            self.assertEqual(self.book.hero_actions[action]['method'], 'examine')

    def test_room_actions_take(self):
        for action in ('взять', 'брать', 'собрать'):
            self.assertEqual(self.book.room_actions[action]['method'], 'take')


class TestBookFormat(unittest.TestCase):
    """Тесты форматирования книги в падежах."""

    def setUp(self):
        self.book = make_book()

    def test_known_case(self):
        self.assertEqual(format(self.book, 'accus'), 'Старую книгу о мушкетерах')

    def test_unknown_case_returns_empty_string(self):
        self.assertEqual(format(self.book, 'zzz'), '')


class TestBookStr(unittest.TestCase):
    """Тесты строкового представления книги."""

    def test_str(self):
        book = make_book()
        self.assertEqual(str(book), book.name)


class TestBookOnCreate(unittest.TestCase):
    """Тесты метода Book.on_create."""

    def test_on_create(self):
        self.assertIs(Book(None).on_create(), True)


class TestBookDrop(unittest.TestCase):
    """Тесты метода Book.drop."""

    def setUp(self):
        self.book = make_book()
        self.who = FakeWho()

    def test_drop(self):
        result = self.book.drop(self.who)
        room = self.who.current_position
        room.loot.add.assert_called_once_with(self.book)
        self.who.backpack.remove.assert_called_once_with(item=self.book, place=room)
        room.action_controller.add_actions.assert_called_once_with(self.book)
        self.who.action_controller.delete_actions_by_item.assert_called_once_with(self.book)
        self.assertEqual(result, f'{self.who.name} аккуратно кладет {self.book.name} в укромное местечко.')


class TestBookCheckName(unittest.TestCase):
    """Тесты метода Book.check_name."""

    def setUp(self):
        self.book = make_book()

    def test_matches_generic_words(self):
        self.assertTrue(self.book.check_name('книга'))
        self.assertTrue(self.book.check_name('книжку'))
        self.assertTrue(self.book.check_name('КНИГА'))

    def test_matches_lexemes(self):
        self.assertTrue(self.book.check_name('Старую книгу о мушкетерах'))

    def test_rejects_other_words(self):
        self.assertFalse(self.book.check_name('топор'))


class TestBookGetNamesList(unittest.TestCase):
    """Тесты метода Book.get_names_list."""

    def setUp(self):
        self.book = make_book()

    def test_default_names(self):
        self.assertEqual(self.book.get_names_list(), ['книга', 'книгу', 'книжка', 'книжку'])

    def test_with_cases(self):
        names = self.book.get_names_list(['nom', 'accus'])
        self.assertEqual(
            names,
            ['книга', 'книгу', 'книжка', 'книжку',
             'старая книга о мушкетерах', 'старую книгу о мушкетерах']
        )

    def test_cases_none_does_not_crash(self):
        self.assertEqual(self.book.get_names_list(None), ['книга', 'книгу', 'книжка', 'книжку'])

    def test_cases_not_a_list(self):
        self.assertEqual(self.book.get_names_list('nom'), ['книга', 'книгу', 'книжка', 'книжку'])


class TestBookPlace(unittest.TestCase):
    """Тесты метода Book.place."""

    def test_place_in_explicit_place(self):
        book = make_book()
        place = MagicMock()
        result = book.place(floor=MagicMock(), place=place)
        place.add.assert_called_once_with(book)
        self.assertIs(result, True)

    def test_place_random_picks_furniture(self):
        book = make_book()
        floor = MagicMock()
        furniture = MagicMock()
        room = MagicMock()
        room.furniture = [furniture]
        floor.get_random_room_with_furniture.return_value = room
        result = book.place(floor)
        furniture.add.assert_called_once_with(book)
        self.assertIs(result, True)

    def test_place_random_returns_false_without_furniture_rooms(self):
        book = make_book()
        floor = MagicMock()
        floor.get_random_room_with_furniture.return_value = None
        result = book.place(floor)
        self.assertIs(result, False)


class TestBookExamine(unittest.TestCase):
    """Тесты метода Book.examine."""

    def test_can_examine_returns_list_with_text(self):
        book = make_book()
        who = FakeWho()
        who.check_if_can_examine = MagicMock(return_value=(True, []))
        result = book.examine(who)
        self.assertEqual(result, [f'{who.name} держит в руках {book:accus}. {book.examine_text}'])

    def test_cannot_examine_returns_message(self):
        book = make_book()
        who = FakeWho()
        who.check_if_can_examine = MagicMock(return_value=(False, 'Не до осмотра.'))
        result = book.examine(who)
        self.assertEqual(result, 'Не до осмотра.')


class TestBookShow(unittest.TestCase):
    """Тесты метода Book.show."""

    def test_show_returns_nominative_lexeme(self):
        book = make_book()
        self.assertEqual(book.show(), 'Старая книга о мушкетерах')


class TestBookUse(unittest.TestCase):
    """Тесты метода Book.use."""

    def test_can_read(self):
        book = make_book()
        book.increase_mastery = MagicMock(return_value='Рост мастерства.')
        who = FakeWho()
        who.check_if_can_read = MagicMock(return_value=(True, []))
        result = book.use(who)
        self.assertEqual(result[0], f'{who.name} читает {book:accus}.')
        self.assertIn('Текст книги.', result)
        self.assertIn('Рост мастерства.', result)
        who.backpack.remove.assert_called_once_with(book)
        who.action_controller.delete_actions_by_item.assert_called_once_with(book)

    def test_cannot_read_returns_message(self):
        book = make_book()
        who = FakeWho()
        who.check_if_can_read = MagicMock(return_value=(False, 'Темно.'))
        result = book.use(who)
        self.assertEqual(result, 'Темно.')


class TestBookTake(unittest.TestCase):
    """Тесты метода Book.take."""

    def test_take_with_backpack(self):
        book = make_book()
        who = FakeWho()
        result = book.take(who)
        who.put_in_backpack.assert_called_once_with(book)
        self.assertEqual(result, f'{who.name} забирает {book:accus} себе.')

    def test_take_without_backpack(self):
        book = make_book()
        who = FakeWho()
        who.backpack.no_backpack = True
        who.g = MagicMock(return_value='ему')
        result = book.take(who)
        who.put_in_backpack.assert_not_called()
        self.assertIn('не может взять книгу', result)


def mastery_book_test(book_cls, key):
    class TestBook(unittest.TestCase):
        """Параметризованный тест книги мастерства."""

        def setUp(self):
            self.book = book_cls(None)
            self.who = FakeWho(mastery={key: {'level': 1, 'max_level': 5}})

        def test_increases_level(self):
            self.book.increase_mastery(self.who)
            self.assertEqual(self.who.mastery[key]['level'], 2)

        def test_max_level_message(self):
            self.who.mastery[key]['level'] = 5
            result = self.book.increase_mastery(self.who)
            self.assertEqual(self.who.mastery[key]['level'], 5)
            self.assertIsInstance(result, str)
            self.assertTrue(result)

        def test_returns_string(self):
            result = self.book.increase_mastery(self.who)
            self.assertIsInstance(result, str)
    return TestBook


class TestThrustingWeaponBook(mastery_book_test(ThrustingWeaponBook, 'колющее')):
    pass


class TestCuttingWeaponBook(mastery_book_test(CuttingWeaponBook, 'рубящее')):
    pass


class TestBluntWeaponBook(mastery_book_test(BluntWeaponBook, 'ударное')):
    pass


class TestShieldsBook(mastery_book_test(ShieldsBook, 'щиты')):
    pass


class TestArmorBook(mastery_book_test(ArmorBook, 'доспехи')):
    pass


class TestTrapsBook(unittest.TestCase):
    """Тесты книги о ловушках."""

    def setUp(self):
        self.book = TrapsBook(None)
        self.who = FakeWho()

    def test_increases_trap_mastery(self):
        result = self.book.increase_mastery(self.who)
        self.assertEqual(self.who.trap_mastery, 1)
        self.assertIsInstance(result, str)


class TestWisdomBook(unittest.TestCase):
    """Тесты книги об интеллекте."""

    def test_increases_intel_and_start_intel(self):
        book = WisdomBook(None)
        who = FakeWho()
        who.g = MagicMock(return_value='стал')
        result = book.increase_mastery(who)
        who.intel.increase_modifier.assert_called_once_with(1)
        who.start_intel.increase_modifier.assert_called_once_with(1)
        self.assertTrue(result.endswith('.'))


if __name__ == '__main__':
    unittest.main()
