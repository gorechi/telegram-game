import os
import json
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock

from src.class_controller import Controller
from src.class_dice import Dice
from src.class_game import Game

Game.__del__ = lambda self: None


class FakeObject:
    def __init__(self, game):
        self.game = game
        self.on_create_called = False
        self.name = None
        self.value = None
        self.class_name = None

    def on_create(self):
        self.on_create_called = True


@dataclass
class FakeTemplate:
    class_name: str = 'Thing'
    name: str = ''
    value: int = 0


class FakeController(Controller):
    Template = FakeTemplate
    _classes = {'Thing': FakeObject}

    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.all_objects = []
        self.templates = []

    def load_templates(self, path='json/things.json'):
        return super().load_templates(path)


def make_game():
    return Game(chat_id='test', bot=MagicMock())


def make_controller(game=None):
    if game is None:
        game = make_game()
    ctrl = FakeController(game)
    ctrl.templates = [
        FakeTemplate(class_name='Thing', name='alpha', value=10),
        FakeTemplate(class_name='Thing', name='beta', value=20),
        FakeTemplate(class_name='Thing', name='gamma', value=30),
    ]
    return ctrl


class TestLoadTemplates(unittest.TestCase):
    def test_loads_templates_from_file(self):
        data = [{'class_name': 'Thing', 'name': 't1', 'value': 1},
                {'class_name': 'Thing', 'name': 't2', 'value': 2}]
        path = os.path.join(os.path.dirname(__file__), '_test_templates.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            ctrl = make_controller()
            templates = ctrl.load_templates(path)
            self.assertEqual(len(templates), 2)
            self.assertIsInstance(templates[0], FakeTemplate)
            self.assertEqual(templates[0].class_name, 'Thing')
            self.assertEqual(templates[0].name, 't1')
            self.assertEqual(templates[0].value, 1)
        finally:
            os.remove(path)

    def test_raises_on_empty_json(self):
        path = os.path.join(os.path.dirname(__file__), '_test_empty_templates.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            ctrl = make_controller()
            with self.assertRaises(FileExistsError):
                ctrl.load_templates(path)
        finally:
            os.remove(path)

    def test_raises_on_missing_file(self):
        ctrl = make_controller()
        with self.assertRaises(FileNotFoundError):
            ctrl.load_templates('json/nonexistent_file.json')


class TestGetTemplatesByClassName(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_returns_matching_templates(self):
        result = self.ctrl.get_templates_by_class_name('Thing')
        self.assertEqual(len(result), 3)

    def test_returns_empty_list_for_no_match(self):
        result = self.ctrl.get_templates_by_class_name('Nonexistent')
        self.assertEqual(result, [])

    def test_raises_on_non_string(self):
        with self.assertRaises(TypeError):
            self.ctrl.get_templates_by_class_name(123)


class TestGetTemplateByName(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_returns_matching_template(self):
        template = self.ctrl.get_template_by_name('beta')
        self.assertEqual(template.name, 'beta')
        self.assertEqual(template.value, 20)

    def test_raises_when_not_found(self):
        with self.assertRaises(ValueError):
            self.ctrl.get_template_by_name('nonexistent')

    def test_raises_on_non_string(self):
        with self.assertRaises(TypeError):
            self.ctrl.get_template_by_name(123)


class TestCreateObjectFromTemplate(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()
        self.template = FakeTemplate(class_name='Thing', name='alpha', value=42)

    def test_creates_correct_type(self):
        obj = self.ctrl.create_object_from_template(self.template)
        self.assertIsInstance(obj, FakeObject)

    def test_calls_on_create(self):
        obj = self.ctrl.create_object_from_template(self.template)
        self.assertTrue(obj.on_create_called)

    def test_sets_template_attributes_on_object(self):
        obj = self.ctrl.create_object_from_template(self.template)
        self.assertEqual(obj.name, 'alpha')
        self.assertEqual(obj.value, 42)

    def test_increments_how_many(self):
        self.assertEqual(self.ctrl.how_many, 0)
        self.ctrl.create_object_from_template(self.template)
        self.assertEqual(self.ctrl.how_many, 1)
        self.ctrl.create_object_from_template(self.template)
        self.assertEqual(self.ctrl.how_many, 2)

    def test_appends_to_all_objects(self):
        self.ctrl.create_object_from_template(self.template)
        self.assertEqual(len(self.ctrl.all_objects), 1)
        self.assertIsInstance(self.ctrl.all_objects[0], FakeObject)

    def test_raises_on_wrong_template_type(self):
        with self.assertRaises(TypeError):
            self.ctrl.create_object_from_template("not a template")

    def test_raises_on_wrong_template_dataclass(self):
        @dataclass
        class OtherTemplate:
            class_name: str = 'Thing'
        with self.assertRaises(TypeError):
            self.ctrl.create_object_from_template(OtherTemplate())

    def test_raises_on_invalid_class_name(self):
        bad_template = FakeTemplate(class_name='Nonexistent', name='x', value=1)
        with self.assertRaises(KeyError):
            self.ctrl.create_object_from_template(bad_template)

    def test_calls_additional_actions(self):
        self.ctrl.additional_actions = MagicMock(return_value=True)
        obj = self.ctrl.create_object_from_template(self.template)
        self.ctrl.additional_actions.assert_called_once_with(obj)


class TestGenerateValue(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_returns_data_as_is_for_non_dict(self):
        self.assertEqual(self.ctrl.generate_value(42), 42)
        self.assertEqual(self.ctrl.generate_value('hello'), 'hello')
        self.assertIsNone(self.ctrl.generate_value(None))

    def test_returns_dict_as_is_when_no_random_or_dice(self):
        data = {'some_key': 'some_value'}
        self.assertEqual(self.ctrl.generate_value(data), data)

    def test_returns_random_int(self):
        data = {'random': True, 'value': [10, 50]}
        for _ in range(50):
            result = self.ctrl.generate_value(data)
            self.assertIsInstance(result, int)
            self.assertGreaterEqual(result, 10)
            self.assertLessEqual(result, 50)

    def test_returns_dice_when_dice_true(self):
        data = {'dice': True, 'value': 6}
        result = self.ctrl.generate_value(data)
        self.assertIsInstance(result, Dice)
        self.assertEqual(result.base_die(), 6)

    def test_returns_dice_with_random_value(self):
        data = {'random': True, 'dice': True, 'value': [10, 50]}
        for _ in range(50):
            result = self.ctrl.generate_value(data)
            self.assertIsInstance(result, Dice)
            self.assertGreaterEqual(result.base_die(), 10)
            self.assertLessEqual(result.base_die(), 50)


class TestCreateObjectByName(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_creates_object_by_name(self):
        obj = self.ctrl.create_object_by_name('alpha')
        self.assertIsInstance(obj, FakeObject)
        self.assertEqual(obj.name, 'alpha')
        self.assertEqual(obj.value, 10)

    def test_raises_when_not_found(self):
        with self.assertRaises(ValueError):
            self.ctrl.create_object_by_name('nonexistent')


class TestCheckEndgame(unittest.TestCase):
    def test_returns_false(self):
        ctrl = make_controller()
        self.assertFalse(ctrl.check_endgame())


class TestGetEmptyObjectByClassName(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_returns_empty_object(self):
        obj = self.ctrl.get_empty_object_by_class_name('Thing')
        self.assertIsInstance(obj, FakeObject)
        self.assertTrue(obj.empty)

    def test_raises_on_invalid_class_name(self):
        with self.assertRaises(ValueError):
            self.ctrl.get_empty_object_by_class_name('Nonexistent')


class TestGetRandomObjectByFilters(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_returns_matching_object(self):
        obj = self.ctrl.get_random_object_by_filters(name='alpha')
        self.assertIsInstance(obj, FakeObject)
        self.assertEqual(obj.name, 'alpha')

    def test_raises_when_no_match(self):
        with self.assertRaises(ValueError):
            self.ctrl.get_random_object_by_filters(name='nonexistent')


class TestGetRandomTemplateByFilters(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_returns_filtered_template(self):
        template = self.ctrl.get_random_template_by_filters({'name': 'beta'})
        self.assertEqual(template.name, 'beta')
        self.assertEqual(template.value, 20)

    def test_raises_when_no_match(self):
        with self.assertRaises(ValueError):
            self.ctrl.get_random_template_by_filters({'name': 'nonexistent'})

    def test_multiple_filters(self):
        template = self.ctrl.get_random_template_by_filters({'name': 'gamma', 'value': 30})
        self.assertEqual(template.name, 'gamma')

    def test_raises_when_partial_match(self):
        with self.assertRaises(ValueError):
            self.ctrl.get_random_template_by_filters({'name': 'alpha', 'value': 999})


class TestGetRandomObjectsByClassName(unittest.TestCase):
    def setUp(self):
        self.ctrl = make_controller()

    def test_creates_multiple_objects(self):
        objects = self.ctrl.get_random_objects_by_class_name('Thing', how_many=5)
        self.assertEqual(len(objects), 5)
        for obj in objects:
            self.assertIsInstance(obj, FakeObject)
        self.assertEqual(self.ctrl.how_many, 5)

    def test_creates_one_by_default(self):
        objects = self.ctrl.get_random_objects_by_class_name('Thing')
        self.assertEqual(len(objects), 1)
        self.assertEqual(self.ctrl.how_many, 1)

    def test_raises_when_no_templates(self):
        with self.assertRaises(ValueError):
            self.ctrl.get_random_objects_by_class_name('Nonexistent', how_many=3)


if __name__ == '__main__':
    unittest.main()
