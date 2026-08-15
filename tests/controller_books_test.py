import json
import unittest
from unittest.mock import MagicMock

from src.class_book import ThrustingWeaponBook
from src.class_dice import Dice
from src.controllers.controller_books import BooksController


def load_templates():
    with open('json/books.json', encoding='utf-8') as f:
        return json.load(f)


class TestBooksControllerInit(unittest.TestCase):
    """Тесты инициализации контроллера книг."""

    def test_init(self):
        game = MagicMock()
        controller = BooksController(game)
        self.assertIs(controller.game, game)
        self.assertEqual(controller.how_many, 0)
        self.assertEqual(controller.all_objects, [])
        self.assertEqual(len(controller.templates), len(load_templates()))


class TestBooksControllerCreateObject(unittest.TestCase):
    """Тесты создания книг из шаблонов."""

    def setUp(self):
        self.controller = BooksController(game=MagicMock())
        self.templates = load_templates()

    def test_all_json_classes_are_created(self):
        for template_data in self.templates:
            template = [t for t in self.controller.templates if t.class_name == template_data['class_name']][0]
            book = self.controller.create_object_from_template(template)
            self.assertEqual(type(book).__name__, template_data['class_name'])
            self.assertIsNotNone(book.name)
            self.assertIn(book.text, template_data['texts'])
            self.assertEqual(book.examine_text, template_data['examine_text'])

    def test_create_decorates_lexemes(self):
        template = [t for t in self.controller.templates if t.class_name == 'ThrustingWeaponBook'][0]
        book = self.controller.create_object_from_template(template)
        self.assertEqual(book.name, book.lexemes['nom'])
        for lexeme in ('nom', 'accus', 'gen', 'dat', 'prep', 'inst'):
            self.assertIn('книг', book.lexemes[lexeme])
            self.assertIn(template.decoration, book.lexemes[lexeme])

    def test_create_defines_price(self):
        template = [t for t in self.controller.templates if t.class_name == 'ThrustingWeaponBook'][0]
        book = self.controller.create_object_from_template(template)
        self.assertGreater(book.base_price, template.base_price)

    def test_how_many_increments(self):
        template = [t for t in self.controller.templates if t.class_name == 'ThrustingWeaponBook'][0]
        self.controller.create_object_from_template(template)
        self.assertEqual(self.controller.how_many, 1)
        self.assertEqual(len(self.controller.all_objects), 1)

    def test_get_random_object_by_filters(self):
        book = self.controller.get_random_object_by_filters()
        self.assertIn(type(book).__name__, [t['class_name'] for t in self.templates])


class TestBooksControllerDecorate(unittest.TestCase):
    """Тесты метода decorate."""

    def setUp(self):
        self.controller = BooksController(game=MagicMock())

    def test_decorate(self):
        book = ThrustingWeaponBook(game=None)
        book.decoration = 'о мушкетерах'
        book.texts = ['Текст 1', 'Текст 2']
        result = self.controller.decorate(book)
        self.assertIs(result, True)
        self.assertEqual(book.name, book.lexemes['nom'])
        self.assertIn('о мушкетерах', book.name)
        self.assertIn(book.text, book.texts)


class TestBooksControllerDefinePrice(unittest.TestCase):
    """Тесты метода define_price."""

    def setUp(self):
        self.controller = BooksController(game=MagicMock())

    def test_define_price(self):
        book = ThrustingWeaponBook(game=None)
        book.base_price = 7
        book.price_dice = Dice([8])
        self.controller.define_price(book)
        self.assertGreater(book.base_price, 7)
        self.assertLessEqual(book.base_price, 15)


class TestBooksControllerAdditionalActions(unittest.TestCase):
    """Тесты метода additional_actions."""

    def test_additional_actions(self):
        controller = BooksController(game=MagicMock())
        book = ThrustingWeaponBook(game=None)
        book.decoration = 'о мушкетерах'
        book.texts = ['Текст']
        book.base_price = 7
        book.price_dice = Dice([8])
        result = controller.additional_actions(book)
        self.assertIs(result, True)
        self.assertIsNotNone(book.name)
        self.assertGreater(book.base_price, 7)
        self.assertLessEqual(book.base_price, 15)


if __name__ == '__main__':
    unittest.main()
