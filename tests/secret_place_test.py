import unittest
from unittest.mock import MagicMock

from src.class_secret_place import SecretPlace
from src.controllers.controller_secret_places import SecretPlacesController


def make_game():
    game = MagicMock()
    game.player = MagicMock()
    return game


def make_secret(name='унитаз', nom='унитаз', accus='унитаз',
                empty_text='пуст', revealed=False):
    game = make_game()
    secret = SecretPlace(game)
    secret.name = name
    secret.empty_text = empty_text
    secret.revealed = revealed
    secret.lexemes = {
        'nom': nom,
        'accus': accus,
        'gen': f'{nom}а',
        'dat': f'{nom}у',
        'prep': f'{nom}е',
        'inst': f'{nom}ом',
    }
    secret.loot = MagicMock()
    secret.loot.__eq__ = lambda self, other: other == 0 if isinstance(other, int) else False
    return secret


def make_hero(name='Герой', no_backpack=False):
    hero = MagicMock()
    hero.name = name
    hero.current_position = MagicMock()
    return hero


class TestSecretPlaceInit(unittest.TestCase):

    def test_init_sets_game(self):
        game = make_game()
        secret = SecretPlace(game)
        self.assertIs(secret.game, game)

    def test_init_defaults(self):
        secret = SecretPlace(make_game())
        self.assertIsNone(secret.name)
        self.assertIsNone(secret.lexemes)
        self.assertIsNone(secret.room)
        self.assertIsNone(secret.floor)
        self.assertIsNone(secret.loot)
        self.assertIsNone(secret.trap)
        self.assertFalse(secret.revealed)

    def test_room_actions_keys(self):
        secret = SecretPlace(make_game())
        self.assertIn('обыскать', secret.room_actions)

    def test_search_action_method(self):
        secret = SecretPlace(make_game())
        self.assertEqual(secret.room_actions['обыскать']['method'], 'search')

    def test_search_action_hidden(self):
        secret = SecretPlace(make_game())
        self.assertEqual(secret.room_actions['обыскать']['hidden'], 'is_not_revealed')

    def test_search_action_duration(self):
        secret = SecretPlace(make_game())
        self.assertEqual(secret.room_actions['обыскать']['duration'], 2)

    def test_search_action_not_in_combat(self):
        secret = SecretPlace(make_game())
        self.assertFalse(secret.room_actions['обыскать']['in_combat'])

    def test_search_action_not_in_darkness(self):
        secret = SecretPlace(make_game())
        self.assertFalse(secret.room_actions['обыскать']['in_darkness'])

    def test_search_action_not_bulk(self):
        secret = SecretPlace(make_game())
        self.assertFalse(secret.room_actions['обыскать']['bulk'])


class TestSecretPlaceFormat(unittest.TestCase):

    def test_format_known_case(self):
        secret = make_secret()
        self.assertEqual(f'{secret:nom}', 'унитаз')

    def test_format_accus(self):
        secret = make_secret()
        self.assertEqual(f'{secret:accus}', 'унитаз')

    def test_format_gen(self):
        secret = make_secret()
        self.assertEqual(f'{secret:gen}', 'унитаза')

    def test_format_unknown_case(self):
        secret = make_secret()
        self.assertEqual(f'{secret:unknown}', '')


class TestSecretPlaceIsNotRevealed(unittest.TestCase):

    def test_not_revealed(self):
        secret = make_secret(revealed=False)
        self.assertTrue(secret.is_not_revealed())

    def test_revealed(self):
        secret = make_secret(revealed=True)
        self.assertFalse(secret.is_not_revealed())


class TestSecretPlaceCheckName(unittest.TestCase):

    def test_check_name_nom(self):
        secret = make_secret()
        self.assertTrue(secret.check_name('унитаз'))

    def test_check_name_wrong(self):
        secret = make_secret()
        self.assertFalse(secret.check_name('стол'))

    def test_check_name_case_insensitive(self):
        secret = make_secret()
        self.assertTrue(secret.check_name('УНИТАЗ'))


class TestSecretPlaceGetNamesList(unittest.TestCase):

    def test_returns_lexemes(self):
        secret = make_secret()
        names = secret.get_names_list(['nom', 'accus'])
        self.assertIn('унитаз', names)
        self.assertIn('унитаз', names)

    def test_empty_cases(self):
        secret = make_secret()
        names = secret.get_names_list([])
        self.assertEqual(names, [])


class TestSecretPlaceSearch(unittest.TestCase):

    def test_search_empty_loot(self):
        secret = make_secret(name='унитаз', empty_text='пуст')
        secret.loot.__eq__ = lambda self, other: True if isinstance(other, int) and other == 0 else False
        hero = make_hero()
        result = secret.search(hero)
        self.assertIsInstance(result, str)
        self.assertIn('Унитаз', result)
        self.assertIn('пуст', result)

    def test_search_with_loot(self):
        secret = make_secret()
        item = MagicMock()
        item.name = 'руна'
        secret.loot.pile = [item]
        secret.loot.__eq__ = lambda self, other: False
        secret.loot.show_sorted = MagicMock(return_value=['Руна'])
        secret.loot.reveal = MagicMock()
        hero = make_hero()
        result = secret.search(hero)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 3)
        self.assertIn('Руна', result)
        self.assertTrue(secret.revealed)
        secret.loot.reveal.assert_called_once_with(hero.current_position)

    def test_search_sets_revealed(self):
        secret = make_secret()
        secret.loot.pile = [MagicMock(name='p')]
        secret.loot.__eq__ = lambda self, other: False
        secret.loot.show_sorted = MagicMock(return_value=[])
        secret.loot.reveal = MagicMock()
        hero = make_hero()
        self.assertFalse(secret.revealed)
        secret.search(hero)
        self.assertTrue(secret.revealed)

    def test_search_empty_loot_does_not_reveal(self):
        secret = make_secret()
        secret.loot.__eq__ = lambda self, other: True if isinstance(other, int) and other == 0 else False
        hero = make_hero()
        secret.search(hero)
        self.assertFalse(secret.revealed)


class TestSecretPlacePlace(unittest.TestCase):

    def test_place_sets_room_and_floor(self):
        secret = make_secret()
        room = MagicMock()
        room.floor = MagicMock()
        secret.place(room)
        self.assertIs(secret.room, room)
        self.assertIs(secret.floor, room.floor)

    def test_place_appends_to_room_secrets(self):
        secret = make_secret()
        room = MagicMock()
        room.floor = MagicMock()
        room.secrets = []
        secret.place(room)
        self.assertIn(secret, room.secrets)

    def test_place_registers_action(self):
        secret = make_secret()
        room = MagicMock()
        room.floor = MagicMock()
        room.secrets = []
        secret.place(room)
        room.action_controller.add_actions.assert_called_once_with(secret)


class TestSecretPlacesControllerInit(unittest.TestCase):

    def test_init_sets_game(self):
        game = make_game()
        controller = SecretPlacesController(game)
        self.assertIs(controller.game, game)

    def test_init_how_many_zero(self):
        controller = SecretPlacesController(make_game())
        self.assertEqual(controller.how_many, 0)

    def test_init_templates_loaded(self):
        controller = SecretPlacesController(make_game())
        self.assertGreater(len(controller.templates), 0)

    def test_init_all_objects_empty(self):
        controller = SecretPlacesController(make_game())
        self.assertEqual(len(controller.all_objects), 0)


class TestSecretPlacesControllerAdditionalActions(unittest.TestCase):

    def test_additional_actions_adds_loot(self):
        game = make_game()
        controller = SecretPlacesController(game)
        secret = SecretPlace(game)
        secret.loot = None
        result = controller.additional_actions(secret)
        self.assertTrue(result)
        self.assertIsNotNone(secret.loot)


class TestSecretPlacesControllerAddLoot(unittest.TestCase):

    def test_add_loot_creates_loot(self):
        game = make_game()
        controller = SecretPlacesController(game)
        secret = SecretPlace(game)
        controller.add_loot(secret)
        from src.class_basic import Loot
        self.assertIsInstance(secret.loot, Loot)


class TestSecretPlacesControllerAddTrap(unittest.TestCase):

    def test_add_trap_sets_trap(self):
        game = make_game()
        controller = SecretPlacesController(game)
        secret = SecretPlace(game)
        trap_mock = MagicMock()
        game.traps_controller.get_random_object_by_filters.return_value = trap_mock
        controller.add_trap(secret)
        self.assertIs(secret.trap, trap_mock)


class TestSecretPlacesControllerGetRandomSecretByFloor(unittest.TestCase):

    def test_returns_secret_on_floor(self):
        game = make_game()
        controller = SecretPlacesController(game)
        floor = MagicMock()
        secret = MagicMock()
        secret.floor = floor
        controller.all_objects = [secret]
        result = controller.get_random_secret_by_floor(floor)
        self.assertIs(result, secret)

    def test_returns_none_when_empty(self):
        game = make_game()
        controller = SecretPlacesController(game)
        floor = MagicMock()
        result = controller.get_random_secret_by_floor(floor)
        self.assertIsNone(result)


class TestSecretPlacesControllerGetRandomSecretByRoom(unittest.TestCase):

    def test_returns_secret_in_room(self):
        game = make_game()
        controller = SecretPlacesController(game)
        room = MagicMock()
        secret = MagicMock()
        secret.room = room
        controller.all_objects = [secret]
        result = controller.get_random_secret_by_room(room)
        self.assertIs(result, secret)

    def test_returns_none_when_empty(self):
        game = make_game()
        controller = SecretPlacesController(game)
        room = MagicMock()
        result = controller.get_random_secret_by_room(room)
        self.assertIsNone(result)


class TestSecretPlacesControllerCreateObject(unittest.TestCase):

    def test_creates_secret_from_template(self):
        game = make_game()
        controller = SecretPlacesController(game)
        secret = controller.create_object_by_name('унитаз')
        self.assertIsInstance(secret, SecretPlace)
        self.assertEqual(secret.name, 'унитаз')
        self.assertIsNotNone(secret.loot)

    def test_creates_all_template_types(self):
        game = make_game()
        controller = SecretPlacesController(game)
        names = ['унитаз', 'клетка', 'аквариум', 'стойка', 'стол',
                 'раковина', 'бак', 'хлам', 'диван', 'фонтан',
                 'камин', 'ведро', 'игрушки', 'шкура', 'кадка']
        for name in names:
            secret = controller.create_object_by_name(name)
            self.assertIsInstance(secret, SecretPlace)
            self.assertEqual(secret.name, name)
            self.assertIsNotNone(secret.lexemes)
            self.assertIsNotNone(secret.empty_text)
