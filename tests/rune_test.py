import unittest
from unittest.mock import MagicMock

from src.class_rune import Rune
from src.controllers.controller_runes import RunesController


def make_game():
    game = MagicMock()
    game.player = MagicMock()
    return game


def make_hero(name='Герой', no_backpack=False, gender=0):
    hero = MagicMock()
    hero.name = name
    hero.gender = gender
    hero.g = lambda m, f: m if hero.gender == 0 else f
    hero.backpack = MagicMock()
    hero.backpack.no_backpack = no_backpack
    hero.current_position = MagicMock()
    hero.action_controller = MagicMock()
    return hero


def make_rune(game=None, element=1, name='руна', damage=2, defence=1,
              description='руна огня', poison=False, base_price=15):
    if game is None:
        game = make_game()
    rune = Rune(game)
    rune.element = element
    rune.name = name
    rune.damage = damage
    rune.defence = defence
    rune.description = description
    rune.poison = poison
    rune.base_price = base_price
    rune.lexemes = {
        'nom': 'руна огня',
        'accus': 'руну огня',
        'gen': 'руны огня',
        'dat': 'руне огня',
        'prep': 'руне огня',
        'inst': 'руной огня',
    }
    return rune


class TestRuneInit(unittest.TestCase):

    def test_init_sets_game(self):
        game = make_game()
        rune = Rune(game)
        self.assertIs(rune.game, game)

    def test_init_empty_is_false(self):
        rune = Rune(make_game())
        self.assertFalse(rune.empty)

    def test_hero_actions_keys(self):
        rune = Rune(make_game())
        expected = {'бросить', 'выбросить', 'оставить', 'осмотреть', 'изучить'}
        self.assertEqual(set(rune.hero_actions.keys()), expected)

    def test_room_actions_keys(self):
        rune = Rune(make_game())
        expected = {'взять', 'брать', 'собрать'}
        self.assertEqual(set(rune.room_actions.keys()), expected)

    def test_drop_actions_method(self):
        rune = Rune(make_game())
        for key in ['бросить', 'выбросить', 'оставить']:
            self.assertEqual(rune.hero_actions[key]['method'], 'drop')

    def test_show_actions_method(self):
        rune = Rune(make_game())
        for key in ['осмотреть', 'изучить']:
            self.assertEqual(rune.hero_actions[key]['method'], 'show')

    def test_room_actions_all_take(self):
        rune = Rune(make_game())
        for key in rune.room_actions:
            self.assertEqual(rune.room_actions[key]['method'], 'take')

    def test_drop_actions_allow_darkness(self):
        rune = Rune(make_game())
        for key in ['бросить', 'выбросить', 'оставить']:
            self.assertTrue(rune.hero_actions[key]['in_darkness'])

    def test_show_actions_not_in_combat(self):
        rune = Rune(make_game())
        for key in ['осмотреть', 'изучить']:
            self.assertFalse(rune.hero_actions[key]['in_combat'])


class TestRuneStr(unittest.TestCase):

    def test_str_known_element(self):
        rune = make_rune(element=1)
        result = str(rune)
        self.assertIn('руна', result)
        self.assertIn('огня', result)
        self.assertIn('урон + 2', result)
        self.assertIn('защита + 1', result)

    def test_str_unknown_element(self):
        rune = make_rune(element=999)
        result = str(rune)
        self.assertIn('руна', result)
        self.assertIn('  - ', result)

    def test_str_all_known_elements(self):
        for elem, name in Rune._elements_dictionary.items():
            rune = make_rune(element=elem)
            result = str(rune)
            self.assertIn(name, result, f"Element {elem} should produce '{name}'")


class TestRuneFormat(unittest.TestCase):

    def test_format_known_cases(self):
        rune = make_rune()
        self.assertEqual(f'{rune:accus}', 'руну огня')
        self.assertEqual(f'{rune:nom}', 'руна огня')
        self.assertEqual(f'{rune:gen}', 'руны огня')
        self.assertEqual(f'{rune:dat}', 'руне огня')
        self.assertEqual(f'{rune:prep}', 'руне огня')
        self.assertEqual(f'{rune:inst}', 'руной огня')

    def test_format_unknown_case(self):
        rune = make_rune()
        self.assertEqual(f'{rune:unknown}', '')


class TestRuneCheckName(unittest.TestCase):

    def test_check_name_nom(self):
        rune = make_rune()
        self.assertTrue(rune.check_name('руна'))

    def test_check_name_accus(self):
        rune = make_rune()
        self.assertTrue(rune.check_name('руну'))

    def test_check_name_with_element(self):
        rune = make_rune()
        self.assertTrue(rune.check_name('руна огня'))

    def test_check_name_wrong(self):
        rune = make_rune()
        self.assertFalse(rune.check_name('меч'))

    def test_check_name_case_insensitive(self):
        rune = make_rune()
        self.assertTrue(rune.check_name('РУНА'))


class TestRuneGetNamesList(unittest.TestCase):

    def test_returns_base_names(self):
        rune = make_rune()
        names = rune.get_names_list(['nom', 'accus'])
        self.assertIn('руна', names)
        self.assertIn('руну', names)

    def test_appends_lexemes(self):
        rune = make_rune()
        names = rune.get_names_list(['nom'])
        self.assertIn('руна огня', names)

    def test_unknown_case_appends_empty(self):
        rune = make_rune()
        names = rune.get_names_list(['unknown'])
        self.assertIn('', names)
        self.assertIn('руна', names)


class TestRuneOnCreate(unittest.TestCase):

    def test_returns_true(self):
        rune = Rune(make_game())
        self.assertTrue(rune.on_create())


class TestRunePlaceInRoom(unittest.TestCase):

    def test_place_in_secret(self):
        game = make_game()
        rune = make_rune(game)
        room = MagicMock()
        secret = MagicMock()
        game.secret_places_controller.get_random_secret_by_room.return_value = secret
        result = rune.place_in_room(room)
        self.assertTrue(result)
        secret.loot.add.assert_called_once_with(rune)

    def test_place_in_furniture(self):
        game = make_game()
        rune = make_rune(game)
        room = MagicMock()
        furniture = MagicMock()
        room.furniture = [furniture]
        game.secret_places_controller.get_random_secret_by_room.return_value = None
        result = rune.place_in_room(room)
        self.assertTrue(result)
        furniture.add.assert_called_once_with(rune)

    def test_place_on_floor(self):
        game = make_game()
        rune = make_rune(game)
        room = MagicMock()
        room.furniture = []
        game.secret_places_controller.get_random_secret_by_room.return_value = None
        result = rune.place_in_room(room)
        self.assertTrue(result)
        room.add.assert_called_once_with(rune)
        room.action_controller.add_actions.assert_called_once_with(rune)

    def test_place_no_action_controller(self):
        game = make_game()
        rune = make_rune(game)
        room = MagicMock()
        room.furniture = []
        room.action_controller = None
        game.secret_places_controller.get_random_secret_by_room.return_value = None
        result = rune.place_in_room(room)
        self.assertTrue(result)
        room.add.assert_called_once_with(rune)

    def test_place_no_furniture_attr(self):
        game = make_game()
        rune = make_rune(game)
        room = MagicMock(spec=[])
        room.add = MagicMock()
        game.secret_places_controller.get_random_secret_by_room.return_value = None
        result = rune.place_in_room(room)
        self.assertTrue(result)
        room.add.assert_called_once_with(rune)


class TestRunePlace(unittest.TestCase):

    def test_place_with_secret_on_floor(self):
        game = make_game()
        rune = make_rune(game)
        floor = MagicMock()
        secret = MagicMock()
        game.secret_places_controller.get_random_secret_by_floor.return_value = secret
        result = rune.place(floor)
        self.assertTrue(result)
        secret.loot.add.assert_called_once_with(rune)

    def test_place_with_explicit_room(self):
        game = make_game()
        rune = make_rune(game)
        floor = MagicMock()
        room = MagicMock()
        room.furniture = []
        game.secret_places_controller.get_random_secret_by_room.return_value = None
        result = rune.place(floor, place=room)
        self.assertTrue(result)
        room.add.assert_called_once_with(rune)

    def test_place_no_secret_falls_to_random_room(self):
        game = make_game()
        rune = make_rune(game)
        floor = MagicMock()
        room = MagicMock()
        room.furniture = []
        floor.plan = [room]
        game.secret_places_controller.get_random_secret_by_floor.return_value = None
        game.secret_places_controller.get_random_secret_by_room.return_value = None
        result = rune.place(floor)
        self.assertTrue(result)
        room.add.assert_called_once_with(rune)


class TestRuneTake(unittest.TestCase):

    def test_take_no_backpack(self):
        hero = make_hero(no_backpack=True)
        rune = make_rune()
        result = rune.take(hero)
        self.assertIn('не может взять', result)
        hero.put_in_backpack.assert_not_called()

    def test_take_with_backpack(self):
        hero = make_hero()
        rune = make_rune()
        result = rune.take(hero)
        self.assertIn('забирает', result)
        hero.put_in_backpack.assert_called_once_with(rune)

    def test_take_female_no_backpack(self):
        hero = make_hero(no_backpack=True, gender=1)
        rune = make_rune()
        result = rune.take(hero)
        self.assertIn('ей', result)


class TestRuneShow(unittest.TestCase):

    def test_show_basic(self):
        rune = make_rune(description='руна огня', damage=3, defence=2)
        result = rune.show()
        self.assertEqual(result, 'Руна огня - урон + 3 или защита + 2')

    def test_show_poisoned(self):
        rune = make_rune(description='ядовитая руна воды', damage=1, defence=4, poison=True)
        result = rune.show()
        self.assertEqual(result, 'Ядовитая руна воды - урон + 1 или защита + 4')


class TestRuneDrop(unittest.TestCase):

    def test_drop_adds_to_room_loot(self):
        hero = make_hero()
        rune = make_rune()
        result = rune.drop(hero)
        hero.current_position.loot.add.assert_called_once_with(rune)

    def test_drop_removes_from_backpack(self):
        hero = make_hero()
        rune = make_rune()
        result = rune.drop(hero)
        hero.backpack.remove.assert_called_once_with(
            item=rune, place=hero.current_position
        )

    def test_drop_registers_room_actions(self):
        hero = make_hero()
        rune = make_rune()
        result = rune.drop(hero)
        hero.current_position.action_controller.add_actions.assert_called_once_with(rune)

    def test_drop_removes_hero_actions(self):
        hero = make_hero()
        rune = make_rune()
        result = rune.drop(hero)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(rune)

    def test_drop_returns_message(self):
        hero = make_hero()
        rune = make_rune()
        result = rune.drop(hero)
        self.assertIn('бросает', result)


class TestRuneController(unittest.TestCase):

    def test_controller_generates_rune(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertIsInstance(rune, Rune)

    def test_controller_sets_element(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertIn(rune.element, RunesController._elements)

    def test_controller_sets_damage(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertGreaterEqual(rune.damage, 1)
        self.assertLessEqual(rune.damage, 4)

    def test_controller_sets_defence(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertGreaterEqual(rune.defence, 1)
        self.assertLessEqual(rune.defence, 3)

    def test_controller_sets_description(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertIn(rune.name, rune.description)

    def test_controller_sets_lexemes(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertIn('nom', rune.lexemes)
        self.assertIn('accus', rune.lexemes)

    def test_controller_sets_base_price_above_15(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertGreaterEqual(rune.base_price, 16)

    def test_controller_poison_probability(self):
        game = make_game()
        controller = RunesController(game)
        has_poison = False
        for _ in range(200):
            rune = controller.get_random_object_by_filters()
            if rune.poison:
                has_poison = True
                self.assertIn('ядовитая', rune.description)
                break
        self.assertTrue(has_poison)

    def test_controller_rune_is_enchantable_false(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertFalse(rune.enchantable)

    def test_controller_rune_can_use_in_fight_false(self):
        game = make_game()
        controller = RunesController(game)
        rune = controller.get_random_object_by_filters()
        self.assertFalse(rune.can_use_in_fight)

    def test_controller_creates_unique_runes(self):
        game = make_game()
        controller = RunesController(game)
        rune1 = controller.get_random_object_by_filters()
        rune2 = controller.get_random_object_by_filters()
        self.assertIsNot(rune1, rune2)

    def test_controller_elements_dictionary_matches_rune(self):
        for key in RunesController._lexemes:
            self.assertIn(key, {'nom', 'accus', 'gen', 'dat', 'prep', 'inst'})
