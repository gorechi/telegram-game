import unittest
from unittest.mock import MagicMock, patch

from src.class_furniture import Furniture
from src.class_game import Game

Game.__del__ = lambda self: None


def make_game():
    return Game(chat_id='test', bot=MagicMock())


def make_furniture(game=None):
    if game is None:
        game = make_game()
    f = Furniture(game)
    f.name = '\u0448\u043a\u0430\u0444'
    f.lexemes = {
        'nom': '\u0448\u043a\u0430\u0444',
        'accus': '\u0448\u043a\u0430\u0444',
        'gen': '\u0448\u043a\u0430\u0444\u0430',
        'dat': '\u0448\u043a\u0430\u0444\u0443',
        'prep': '\u0448\u043a\u0430\u0444\u0443',
        'inst': '\u0448\u043a\u0430\u0444\u043e\u043c',
    }
    f.basic_lexemes = ['\u0448\u043a\u0430\u0444']
    f.furniture_type = 2
    f.lockable = True
    f.empty_text = '\u043f\u0443\u0441\u0442'
    f.where = '\u0432 \u0443\u0433\u043b\u0443'
    f.state = '\u0441\u0442\u0430\u0440\u044b\u0439'
    f.trap = None
    f.loot = MagicMock()
    f.loot.pile = []
    f.room = MagicMock()
    f.room.furniture_types.return_value = []
    f.room.furniture = []
    f.room.action_controller = MagicMock()
    return f


def make_hero(game=None):
    if game is None:
        game = make_game()
    hero = MagicMock()
    hero.name = '\u0413\u0435\u0440\u043e\u0439'
    hero.__format__ = lambda self, fmt: hero.name
    hero.backpack = MagicMock()
    hero.detect_trap.return_value = False
    hero.current_position = MagicMock()
    return hero


class TestInit(unittest.TestCase):
    def test_defaults(self):
        f = Furniture(make_game())
        self.assertFalse(f.locked)
        self.assertTrue(f.opened)
        self.assertFalse(f.empty)
        self.assertIsNone(f.room)

    def test_room_actions_keys(self):
        f = Furniture(make_game())
        self.assertIn('\u043e\u0442\u043f\u0435\u0440\u0435\u0442\u044c', f.room_actions)
        self.assertIn('\u043e\u0431\u044b\u0441\u043a\u0430\u0442\u044c', f.room_actions)
        self.assertIn('\u043e\u0441\u043c\u043e\u0442\u0440\u0435\u0442\u044c', f.room_actions)

    def test_room_actions_unlock_condition(self):
        f = Furniture(make_game())
        self.assertEqual(f.room_actions['\u043e\u0442\u043f\u0435\u0440\u0435\u0442\u044c']['condition'], 'is_locked')


class TestStr(unittest.TestCase):
    def test_returns_where_state_name(self):
        f = make_furniture()
        result = str(f)
        self.assertEqual(result, '\u0432 \u0443\u0433\u043b\u0443 \u0441\u0442\u0430\u0440\u044b\u0439 \u0448\u043a\u0430\u0444')


class TestFormat(unittest.TestCase):
    def test_returns_lexeme(self):
        f = make_furniture()
        self.assertEqual(f'{f:accus}', '\u0448\u043a\u0430\u0444')

    def test_returns_lexeme_dat(self):
        f = make_furniture()
        self.assertEqual(f'{f:dat}', '\u0448\u043a\u0430\u0444\u0443')

    def test_returns_empty_string_for_missing(self):
        f = make_furniture()
        self.assertEqual(f'{f:instrumental}', '')


class TestIsLocked(unittest.TestCase):
    def test_not_locked(self):
        f = make_furniture()
        self.assertFalse(f.is_locked())

    def test_locked(self):
        f = make_furniture()
        f.locked = True
        self.assertTrue(f.is_locked())


class TestCheckTrap(unittest.TestCase):
    def test_no_trap(self):
        f = make_furniture()
        f.trap = None
        self.assertFalse(f.check_trap())

    def test_trap_not_activated(self):
        f = make_furniture()
        f.trap = MagicMock()
        f.trap.activated = False
        self.assertFalse(f.check_trap())

    def test_trap_activated(self):
        f = make_furniture()
        f.trap = MagicMock()
        f.trap.activated = True
        self.assertTrue(f.check_trap())


class TestMonsterInAmbush(unittest.TestCase):
    def test_no_monsters(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        self.assertIsNone(f.monster_in_ambush())

    def test_no_monster_hiding_here(self):
        f = make_furniture()
        other = MagicMock()
        other.hiding_place = MagicMock()
        f.room.monsters.return_value = [other]
        self.assertIsNone(f.monster_in_ambush())

    def test_monster_hiding_here(self):
        f = make_furniture()
        monster = MagicMock()
        monster.hiding_place = f
        f.room.monsters.return_value = [monster]
        self.assertIs(monster, f.monster_in_ambush())


class TestGetNamesList(unittest.TestCase):
    def test_returns_basic_lexemes_only(self):
        f = make_furniture()
        result = f.get_names_list()
        self.assertEqual(result, f.basic_lexemes)

    def test_does_not_mutate_basic_lexemes(self):
        f = make_furniture()
        original = f.basic_lexemes.copy()
        f.get_names_list(['nom', 'accus'])
        self.assertEqual(f.basic_lexemes, original)

    def test_adds_requested_cases(self):
        f = make_furniture()
        result = f.get_names_list(['nom', 'accus'])
        self.assertIn('\u0448\u043a\u0430\u0444', result)
        self.assertEqual(len(result), 3)

    def test_none_cases(self):
        f = make_furniture()
        result = f.get_names_list(None)
        self.assertEqual(result, f.basic_lexemes)

    def test_non_list_cases(self):
        f = make_furniture()
        result = f.get_names_list('nom')
        self.assertEqual(result, f.basic_lexemes)


class TestCheckName(unittest.TestCase):
    def test_matches_nom(self):
        f = make_furniture()
        self.assertTrue(f.check_name('\u0448\u043a\u0430\u0444'))

    def test_matches_accus(self):
        f = make_furniture()
        self.assertTrue(f.check_name('\u0448\u043a\u0430\u0444'))

    def test_case_insensitive(self):
        f = make_furniture()
        self.assertTrue(f.check_name('\u0428\u041a\u0410\u0424'))

    def test_no_match(self):
        f = make_furniture()
        self.assertFalse(f.check_name('\u0441\u0442\u043e\u043b'))


class TestOnCreate(unittest.TestCase):
    def test_returns_true(self):
        f = make_furniture()
        self.assertTrue(f.on_create())


class TestAfterUnlock(unittest.TestCase):
    def test_returns_none(self):
        f = make_furniture()
        self.assertIsNone(f.after_unlock(make_hero()))


class TestAfterSearch(unittest.TestCase):
    def test_returns_none(self):
        f = make_furniture()
        self.assertIsNone(f.after_search(make_hero()))


class TestUnlock(unittest.TestCase):
    def test_not_locked_message(self):
        f = make_furniture()
        result = f.unlock(make_hero())
        self.assertIn('\u043d\u0435 \u0437\u0430\u043f\u0435\u0440\u0442\u043e', result)

    def test_locked_no_key(self):
        f = make_furniture()
        f.locked = True
        hero = make_hero()
        hero.backpack.get_first_item_by_class.return_value = None
        result = f.unlock(hero)
        self.assertIn('\u043d\u0435\u0442 \u043f\u043e\u0434\u0445\u043e\u0434\u044f\u0449\u0435\u0433\u043e \u043a\u043b\u044e\u0447\u0430', result)

    def test_locked_with_key(self):
        f = make_furniture()
        f.locked = True
        hero = make_hero()
        key = MagicMock()
        hero.backpack.get_first_item_by_class.return_value = key
        result = f.unlock(hero)
        self.assertIn('\u043e\u0442\u043f\u0438\u0440\u0430\u0435\u0442', result)
        self.assertFalse(f.locked)
        hero.backpack.remove.assert_called_once_with(key)


class TestAdd(unittest.TestCase):
    def test_adds_to_loot(self):
        f = make_furniture()
        item = MagicMock()
        f.add(item)
        f.loot.add.assert_called_once_with(item)


class TestShow(unittest.TestCase):
    def test_basic_description(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        result = f.show()
        self.assertEqual(len(result), 1)
        self.assertIn('\u0448\u043a\u0430\u0444', result[0])

    def test_with_monster_ambush(self):
        f = make_furniture()
        monster = MagicMock()
        monster.hiding_place = f
        f.room.monsters.return_value = [monster]
        result = f.show()
        self.assertEqual(len(result), 2)
        self.assertIn('\u0432\u043e\u0437\u043d\u044f', result[1])


class TestPlace(unittest.TestCase):
    @patch.object(Furniture, '_lock_dice', MagicMock(return_value=2))
    def test_specific_room(self):
        f = make_furniture()
        room = MagicMock()
        room.furniture_types.return_value = []
        result = f.place(room_to_place=room)
        self.assertTrue(result)
        self.assertIs(f.room, room)

    def test_specific_room_type_conflict(self):
        f = make_furniture()
        room = MagicMock()
        room.furniture_types.return_value = [2]
        result = f.place(room_to_place=room)
        self.assertFalse(result)

    def test_random_room(self):
        f = make_furniture()
        floor = MagicMock()
        room = MagicMock()
        room.furniture_types.return_value = []
        floor.get_room_to_place_furniture.return_value = room
        result = f.place(floor=floor)
        self.assertTrue(result)
        self.assertIs(f.room, room)

    def test_no_room_available(self):
        f = make_furniture()
        floor = MagicMock()
        floor.get_room_to_place_furniture.return_value = None
        result = f.place(floor=floor)
        self.assertFalse(result)

    @patch.object(Furniture, '_lock_dice')
    def test_lockable_locks(self, mock_dice):
        mock_dice.roll.return_value = 1
        f = make_furniture()
        f.lockable = True
        floor = MagicMock()
        room = MagicMock()
        room.furniture_types.return_value = []
        floor.get_room_to_place_furniture.return_value = room
        result = f.place(floor=floor)
        self.assertTrue(result)
        self.assertTrue(f.locked)

    @patch.object(Furniture, '_lock_dice')
    def test_lockable_not_locked(self, mock_dice):
        mock_dice.roll.return_value = 2
        f = make_furniture()
        f.lockable = True
        floor = MagicMock()
        room = MagicMock()
        room.furniture_types.return_value = []
        floor.get_room_to_place_furniture.return_value = room
        result = f.place(floor=floor)
        self.assertTrue(result)
        self.assertFalse(f.locked)

    @patch.object(Furniture, '_lock_dice')
    def test_not_lockable(self, mock_dice):
        mock_dice.roll.return_value = 1
        f = make_furniture()
        f.lockable = False
        floor = MagicMock()
        room = MagicMock()
        room.furniture_types.return_value = []
        floor.get_room_to_place_furniture.return_value = room
        result = f.place(floor=floor)
        self.assertTrue(result)
        self.assertFalse(f.locked)


class TestSearch(unittest.TestCase):
    def test_locked(self):
        f = make_furniture()
        f.locked = True
        result = f.search(make_hero())
        self.assertIn('\u0437\u0430\u043f\u0435\u0440\u0442\u043e', result)

    def test_monster_ambush(self):
        f = make_furniture()
        monster = MagicMock()
        monster.hiding_place = f
        f.room.monsters.return_value = [monster]
        result = f.search(make_hero())
        self.assertEqual(result, '')

    def test_empty_loot(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        f.loot.__eq__ = lambda self, other: other == 0
        result = f.search(make_hero())
        self.assertIn('\u043f\u0443\u0441\u0442', result)

    def test_with_loot(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        f.loot.__eq__ = lambda self, other: False
        f.loot.show_sorted.return_value = ['\u043c\u0435\u0447']
        result = f.search(make_hero())
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 2)


class TestExamine(unittest.TestCase):
    def test_basic(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        f.trap = None
        hero = make_hero()
        result = f.examine(hero)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 1)

    def test_trap_not_detected(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        f.trap = MagicMock()
        f.trap.activated = True
        hero = make_hero()
        hero.detect_trap.return_value = False
        result = f.examine(hero)
        self.assertEqual(len(result), 1)

    def test_trap_detected(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        f.trap = MagicMock()
        f.trap.activated = True
        f.trap.get_detection_text.return_value = '\u041b\u043e\u0432\u0443\u0448\u043a\u0430!'
        hero = make_hero()
        hero.detect_trap.return_value = True
        result = f.examine(hero)
        self.assertEqual(len(result), 2)
        self.assertIn('\u041b\u043e\u0432\u0443\u0448\u043a\u0430!', result)

    def test_no_trap_attribute(self):
        f = make_furniture()
        f.room.monsters.return_value = []
        f.trap = None
        hero = make_hero()
        result = f.examine(hero)
        self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()
