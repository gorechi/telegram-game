import contextlib
import gc
import io
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.class_castle import Floor
from src.class_game import Game
from src.class_room import Door, Ladder, Room
from src.class_basic import Loot
from src.class_dice import Dice
from src.enums import state_enum

Game.__del__ = lambda self: None


def make_game():
    with contextlib.redirect_stdout(io.StringIO()):
        return Game(chat_id='test', bot=MagicMock())


class FakeHero:
    """Minimal hero stand-in that supports :gen format."""
    def __init__(self, name='Герой', gen='героя'):
        self.name = name
        self.gen = gen
    def __format__(self, format_spec):
        if format_spec == 'gen':
            return self.gen
        return self.name


def make_bare_floor(game, rows=3, rooms=3):
    controller = game.floors_controller
    floor = Floor(game)
    floor.rows = rows
    floor.rooms = rooms
    floor.how_many = {'монстры': 0, 'спички': 0, 'оружие': 0, 'щит': 0, 'доспех': 0,
                      'зелье': 0, 'мебель': 0, 'книга': 0, 'очаг': 0, 'руна': 0,
                      'торговец': 0, 'лестницы': 0, 'ловушка': 0}
    floor.traps_difficulty = 4
    floor.how_many_dark_rooms = 0
    floor.how_many_locked_rooms = 0
    floor.money_in_locked_rooms = Dice([40])
    floor.boss = False
    floor.floor_number = 1
    controller.create_rooms(floor)
    return floor


def make_room(game=None, floor=None):
    if game is None:
        game = make_game()
    if floor is None:
        floor = make_bare_floor(game)
    return floor.plan[0]


# ---------------------------------------------------------------------------
# Ladder Tests
# ---------------------------------------------------------------------------

class TestLadderInit(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]

    def test_creates_with_valid_rooms(self):
        ladder = Ladder(self.game, self.room_down, self.room_up)
        self.assertIs(ladder.room_down, self.room_down)
        self.assertIs(ladder.room_up, self.room_up)
        self.assertFalse(ladder.locked)
        self.assertEqual(ladder.name, 'лестница')
        self.assertIsInstance(ladder.loot, Loot)

    def test_creates_without_room_up_raises(self):
        with self.assertRaises(NotImplementedError):
            Ladder(self.game, self.room_down)

    def test_raises_with_invalid_room_down(self):
        with self.assertRaises(TypeError):
            Ladder(self.game, "not a room", self.room_up)


class TestLadderDirection(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)

    def test_going_down_from_room_up(self):
        self.assertTrue(self.ladder.going_down(self.room_up))

    def test_going_up_from_room_down(self):
        self.assertTrue(self.ladder.going_up(self.room_down))

    def test_not_going_down_from_room_down(self):
        self.assertFalse(self.ladder.going_down(self.room_down))

    def test_not_going_up_from_room_up(self):
        self.assertFalse(self.ladder.going_up(self.room_up))

    def test_get_direction_from_room_down(self):
        self.assertEqual(self.ladder.get_direction(self.room_down), 'вверх')

    def test_get_direction_from_room_up(self):
        self.assertEqual(self.ladder.get_direction(self.room_up), 'вниз')

    def test_get_direction_from_unknown_room(self):
        other = self.floor.plan[2]
        self.assertEqual(self.ladder.get_direction(other), '')


class TestLadderIsLocked(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)

    def test_not_locked(self):
        self.assertFalse(self.ladder.is_locked())

    def test_locked(self):
        self.ladder.locked = True
        self.assertTrue(self.ladder.is_locked())


class TestLadderGo(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)

    def test_go_down_with_light_on(self):
        who = MagicMock()
        who.check_light.return_value = True
        self.ladder.go_down(who)
        who.go_down_with_light_on.assert_called_once()

    def test_go_down_with_light_off(self):
        who = MagicMock()
        who.check_light.return_value = False
        self.ladder.go_down(who)
        who.go_down_with_light_off.assert_called_once()

    def test_go_up_with_light_on(self):
        who = MagicMock()
        who.check_light.return_value = True
        self.ladder.go_up(who)
        who.go_up_with_light_on.assert_called_once()

    def test_go_up_with_light_off(self):
        who = MagicMock()
        who.check_light.return_value = False
        self.ladder.go_up(who)
        who.go_up_with_light_off.assert_called_once()


class TestLadderShowForGo(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)

    def test_show_from_room_down(self):
        who = MagicMock()
        who.current_position = self.room_down
        result = self.ladder.show_for_go(who)
        self.assertIn('вверх', result)

    def test_show_from_room_up(self):
        who = MagicMock()
        who.current_position = self.room_up
        result = self.ladder.show_for_go(who)
        self.assertIn('вниз', result)


class TestLadderShowForUnlock(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)

    def test_show_from_room_down(self):
        who = MagicMock()
        who.current_position = self.room_down
        result = self.ladder.show_for_unlock(who)
        self.assertIn('потолке', result)

    def test_show_from_room_up(self):
        who = MagicMock()
        who.current_position = self.room_up
        result = self.ladder.show_for_unlock(who)
        self.assertIn('полу', result)

    def test_show_from_unknown_room(self):
        who = MagicMock()
        who.current_position = self.floor.plan[2]
        result = self.ladder.show_for_unlock(who)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestLadderUnlock(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)
        self.who = MagicMock()
        self.who.current_position = self.room_down
        self.who.name = 'Герой'

    def _make_who(self):
        who = FakeHero()
        who.current_position = self.room_down
        who.gen = 'героя'
        who.backpack = MagicMock()
        return who

    def test_unlock_when_not_locked(self):
        self.ladder.locked = False
        who = self._make_who()
        result = self.ladder.unlock(who)
        self.assertIn('не заперта', result)

    def test_unlock_without_key(self):
        self.ladder.locked = True
        who = self._make_who()
        who.backpack.get_first_item_by_class.return_value = None
        result = self.ladder.unlock(who)
        self.assertIn('нет подходящего ключа', result)

    def test_unlock_with_key(self):
        self.ladder.locked = True
        who = self._make_who()
        key = MagicMock()
        who.backpack.get_first_item_by_class.return_value = key
        result = self.ladder.unlock(who)
        self.assertFalse(self.ladder.locked)
        who.backpack.remove.assert_called_once_with(key)
        self.assertIn('отпирает', result)


class TestLadderShowInRoom(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room_down = self.floor.plan[0]
        self.room_up = self.floor.plan[1]
        self.ladder = Ladder(self.game, self.room_down, self.room_up)

    def test_show_as_ladder_down_not_locked(self):
        result = self.ladder.show_in_room_as_ladder_down()
        self.assertIn('спускается', result)

    def test_show_as_ladder_down_locked(self):
        self.ladder.locked = True
        result = self.ladder.show_in_room_as_ladder_down()
        self.assertIn('квадратный люк', result)

    def test_show_as_ladder_up_not_locked(self):
        result = self.ladder.show_in_room_as_ladder_up()
        self.assertIn('ведет', result)

    def test_show_as_ladder_up_locked(self):
        self.ladder.locked = True
        result = self.ladder.show_in_room_as_ladder_up()
        self.assertIn('потолке', result)


class TestLadderDecorate(unittest.TestCase):
    def test_decorate_generates_lexemes(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        for case in ('nom', 'accus', 'gen', 'dat', 'prep', 'inst'):
            self.assertIn(case, ladder.lexemes)
            self.assertTrue(len(ladder.lexemes[case]) > 0)

    def test_decorate_contains_base_word(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        self.assertIn('лестниц', ladder.lexemes['nom'])


class TestLadderFormat(unittest.TestCase):
    def test_format_known_lexeme(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        result = f'{ladder:nom}'
        self.assertIn('лестниц', result)

    def test_format_unknown_lexeme_returns_empty(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        result = f'{ladder:unknown}'
        self.assertEqual(result, '')


class TestLadderGetNamesList(unittest.TestCase):
    def test_returns_standard_names(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        names = ladder.get_names_list()
        self.assertIn('лестница', names)
        self.assertIn('лестницу', names)


class TestLadderGetRandomRoomUp(unittest.TestCase):
    def test_raises_not_implemented(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        with self.assertRaises(NotImplementedError):
            ladder.get_random_room_up()


class TestLadderAdd(unittest.TestCase):
    def test_add_item_to_loot(self):
        game = make_game()
        floor = make_bare_floor(game)
        room_down = floor.plan[0]
        room_up = floor.plan[1]
        ladder = Ladder(game, room_down, room_up)
        item = MagicMock()
        ladder.add(item)
        self.assertIn(item, ladder.loot.pile)


# ---------------------------------------------------------------------------
# Door Tests
# ---------------------------------------------------------------------------

class TestDoorInit(unittest.TestCase):
    def test_init_defaults(self):
        game = make_game()
        door = Door(game)
        self.assertFalse(door.locked)
        self.assertTrue(door.empty)
        self.assertTrue(door.closed)
        self.assertEqual(door.name, 'дверь')
        self.assertEqual(door.rooms, [])


class TestDoorBool(unittest.TestCase):
    def test_empty_door_is_false(self):
        door = Door(make_game())
        self.assertFalse(bool(door))

    def test_non_empty_door_is_true(self):
        door = Door(make_game())
        door.empty = False
        self.assertTrue(bool(door))


class TestDoorFormat(unittest.TestCase):
    def setUp(self):
        self.game = make_game()

    def test_horizontal_empty(self):
        door = Door(self.game)
        door.empty = True
        self.assertEqual(f'{door:horizontal}', '=')

    def test_horizontal_locked(self):
        door = Door(self.game)
        door.empty = False
        door.locked = True
        self.assertEqual(f'{door:horizontal}', '-')

    def test_horizontal_open(self):
        door = Door(self.game)
        door.empty = False
        door.locked = False
        self.assertEqual(f'{door:horizontal}', ' ')

    def test_vertical_empty(self):
        door = Door(self.game)
        door.empty = True
        self.assertEqual(f'{door:vertical}', '║')

    def test_vertical_locked(self):
        door = Door(self.game)
        door.empty = False
        door.locked = True
        self.assertEqual(f'{door:vertical}', '|')

    def test_vertical_open(self):
        door = Door(self.game)
        door.empty = False
        door.locked = False
        self.assertEqual(f'{door:vertical}', ' ')

    def test_unknown_format(self):
        door = Door(self.game)
        self.assertEqual(f'{door:blah}', '?')

    def test_empty_format(self):
        door = Door(self.game)
        self.assertEqual(f'{door:}', '?')


class TestDoorGetAnotherRoom(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room1 = self.floor.plan[0]
        self.room2 = self.floor.plan[1]

    def test_returns_other_room(self):
        door = self.room1.doors[0]
        if door.empty:
            door.empty = False
            door.rooms = [self.room1, self.room2]
        other = door.get_another_room(self.room1)
        self.assertIs(other, self.room2)

    def test_returns_none_for_unknown_room(self):
        door = Door(self.game)
        other = door.get_another_room(self.room1)
        self.assertIsNone(other)

    def test_returns_none_with_one_room(self):
        door = Door(self.game)
        door.rooms = [self.room1]
        other = door.get_another_room(self.room1)
        self.assertIsNone(other)


class TestDoorGetDirectionIndex(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_returns_correct_index(self):
        door = self.room.doors[1]
        index = door.get_direction_index(self.room)
        self.assertEqual(index, 1)

    def test_returns_none_for_unknown_room(self):
        door = Door(self.game)
        index = door.get_direction_index(self.room)
        self.assertIsNone(index)


class TestDoorShowForUnlock(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_returns_direction_text(self):
        door = self.room.doors[0]
        if door.empty:
            door.empty = False
        who = MagicMock()
        who.current_position = self.room
        result = door.show_for_unlock(who)
        if result:
            self.assertIsInstance(result, str)


class TestDoorUnlock(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.door = self.room.doors[0]
        self.door.empty = False

    def _make_who(self):
        who = FakeHero()
        who.current_position = self.room
        who.gen = 'героя'
        who.backpack = MagicMock()
        return who

    def test_unlock_when_not_locked(self):
        self.door.locked = False
        who = self._make_who()
        result = self.door.unlock(who)
        self.assertIn('не заперта', result)

    def test_unlock_without_key(self):
        self.door.locked = True
        who = self._make_who()
        who.backpack.get_first_item_by_class.return_value = None
        result = self.door.unlock(who)
        self.assertIn('нет подходящего ключа', result)

    def test_unlock_with_key(self):
        self.door.locked = True
        who = self._make_who()
        key = MagicMock()
        who.backpack.get_first_item_by_class.return_value = key
        result = self.door.unlock(who)
        self.assertFalse(self.door.locked)
        who.backpack.remove.assert_called_once_with(key)


class TestDoorGetNamesList(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_default_names(self):
        door = Door(self.game)
        names = door.get_names_list()
        self.assertIn('дверь', names)

    def test_with_room_adds_direction(self):
        door = self.room.doors[0]
        if door.empty:
            door.empty = False
        names = door.get_names_list(room=self.room)
        self.assertIn('дверь', names)


class TestDoorIsLocked(unittest.TestCase):
    def test_not_locked(self):
        door = Door(make_game())
        self.assertFalse(door.is_locked())

    def test_locked(self):
        door = Door(make_game())
        door.locked = True
        self.assertTrue(door.is_locked())


class TestDoorActivate(unittest.TestCase):
    def test_activate_sets_attributes(self):
        door = Door(make_game())
        door.activate()
        self.assertFalse(door.empty)
        self.assertFalse(door.locked)
        self.assertTrue(door.closed)


class TestDoorExamine(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.door = self.room.doors[0]

    def test_examine_empty_wall(self):
        self.door.empty = True
        who = MagicMock()
        who.current_position = self.room
        result = self.door.examine(who)
        self.assertIn('стену', result)

    def test_examine_with_fear(self):
        self.door.empty = False
        who = MagicMock()
        who.current_position = self.room
        who.check_fear.return_value = True
        result = self.door.examine(who)
        self.assertIn('не может заставить себя', result)

    def test_examine_without_monster(self):
        self.door.empty = False
        self.door.rooms = [self.room, self.floor.plan[1]]
        who = MagicMock()
        who.current_position = self.room
        who.check_fear.return_value = False
        result = self.door.examine(who)
        self.assertIsInstance(result, list)


class TestDoorGo(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.hero = MagicMock()
        self.hero.current_position = self.room

    def test_go_with_light_on(self):
        door = None
        go_dir = None
        for index, d in enumerate(self.room.doors):
            if not d.empty and not d.locked:
                door = d
                go_dir = index
                break
        if door is None:
            self.skipTest('No open door in room')
        self.hero.check_light.return_value = True
        result = door.go(self.hero)
        self.hero.go_with_light_on.assert_called_once_with(go_dir)

    def test_go_with_light_off(self):
        door = None
        go_dir = None
        for index, d in enumerate(self.room.doors):
            if not d.empty and not d.locked:
                door = d
                go_dir = index
                break
        if door is None:
            self.skipTest('No open door in room')
        self.hero.check_light.return_value = False
        result = door.go(self.hero)
        self.hero.go_with_light_off.assert_called_once_with(go_dir)


class TestDoorCheckDisturbedMonsters(unittest.TestCase):
    def test_calls_who_method(self):
        door = Door(make_game())
        who = MagicMock()
        door.check_disturbed_monsters(who)
        who.check_disturbed_monsters.assert_called_once_with(who)


# ---------------------------------------------------------------------------
# Room Tests
# ---------------------------------------------------------------------------

class TestRoomSearch(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_search_empty_room(self):
        who = MagicMock()
        who.check_monster_in_ambush.return_value = False
        result = self.room.search(who)
        self.assertTrue(any('нет ничего интересного' in line for line in result))

    def test_search_with_ambush_returns_empty(self):
        who = MagicMock()
        who.check_monster_in_ambush.return_value = True
        result = self.room.search(who)
        self.assertEqual(result, '')

    def test_search_with_loot(self):
        who = MagicMock()
        who.check_monster_in_ambush.return_value = False
        item = MagicMock()
        item.name = 'меч'
        self.room.loot.add(item)
        result = self.room.search(who)
        self.assertIn('В комнате есть:', result)

    def test_search_with_corpse(self):
        who = MagicMock()
        who.check_monster_in_ambush.return_value = False
        corpse = MagicMock()
        corpse.description = 'Труп орка'
        self.room.morgue.append(corpse)
        result = self.room.search(who)
        self.assertIn('Труп орка', result)

    def test_search_with_furniture(self):
        who = MagicMock()
        who.check_monster_in_ambush.return_value = False
        furniture = MagicMock()
        furniture.__str__ = lambda self: 'Стол'
        self.room.furniture.append(furniture)
        result = self.room.search(who)
        self.assertIn('Стол', result)


class TestRoomGetSymbolForMap(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_unvisited_returns_space(self):
        self.room.visited = False
        self.assertEqual(self.room.get_symbol_for_map(), ' ')

    def test_player_in_room_returns_name(self):
        self.room.visited = True
        self.game.player.current_position = self.room
        result = self.room.get_symbol_for_map()
        self.assertEqual(result, self.game.player.name[0])

    def test_trader_returns_ruble(self):
        self.room.visited = True
        self.room.trader = MagicMock()
        self.game.player.current_position = self.floor.plan[1]
        result = self.room.get_symbol_for_map()
        self.assertEqual(result, '₽')

    def test_rest_place_returns_diamond(self):
        self.room.visited = True
        self.game.player.current_position = self.floor.plan[1]
        self.room.trader = None
        furniture = SimpleNamespace(can_rest=True, locked=False, where='у стены', state='стоит', lexemes={'nom': 'кровать'})
        self.room.furniture.append(furniture)
        result = self.room.get_symbol_for_map()
        self.assertEqual(result, '◊')

    def test_default_returns_plus(self):
        self.room.visited = True
        self.game.player.current_position = self.floor.plan[1]
        self.room.trader = None
        self.room.light = False
        self.room.stink = 0
        result = self.room.get_symbol_for_map()
        self.assertEqual(result, '+')


class TestRoomSetTorch(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_returns_false_when_no_light(self):
        self.room.light = False
        self.assertFalse(self.room.set_torch())

    def test_returns_true_when_roll_succeeds(self):
        self.room.light = True
        with patch('src.class_room.roll', return_value=Room._torch_die):
            result = self.room.set_torch()
            self.assertTrue(result)

    def test_returns_false_when_roll_fails(self):
        self.room.light = True
        with patch('src.class_room.roll', return_value=1):
            result = self.room.set_torch()
            self.assertFalse(result)


class TestRoomHasCorpse(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_corpse(self):
        self.assertFalse(self.room.has_a_corpse())

    def test_with_corpse(self):
        self.room.morgue.append(MagicMock())
        self.assertTrue(self.room.has_a_corpse())


class TestRoomShowCorpses(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_empty_morgue(self):
        self.assertEqual(self.room.show_corpses(), [])

    def test_with_corpses(self):
        c1 = MagicMock()
        c1.description = 'Труп 1'
        c2 = MagicMock()
        c2.description = 'Труп 2'
        self.room.morgue = [c1, c2]
        result = self.room.show_corpses()
        self.assertEqual(result, ['Труп 1', 'Труп 2'])


class TestRoomGetTrap(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_trap(self):
        self.assertIsNone(self.room.get_trap())

    def test_trap_not_activated(self):
        trap = MagicMock()
        trap.activated = False
        self.room.last_seen_trap = trap
        self.assertIsNone(self.room.get_trap())

    def test_trap_activated(self):
        trap = MagicMock()
        trap.activated = True
        self.room.last_seen_trap = trap
        self.assertIs(self.room.get_trap(), trap)


class TestRoomHasFurniture(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_furniture(self):
        self.assertFalse(self.room.has_furniture())

    def test_with_furniture(self):
        self.room.furniture.append(MagicMock())
        self.assertTrue(self.room.has_furniture())


class TestRoomShowFurniture(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_empty(self):
        self.assertEqual(self.room.show_furniture(), [])

    def test_with_furniture(self):
        f = SimpleNamespace(where='у стены', state='стоит', lexemes={'nom': 'стол'})
        self.room.furniture.append(f)
        result = self.room.show_furniture()
        self.assertEqual(len(result), 1)
        self.assertIn('у стены', result[0])
        self.assertIn('стоит', result[0])
        self.assertIn('стол', result[0])


class TestRoomGetAvailableDirections(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_all_empty(self):
        for d in self.room.doors:
            d.empty = True
        dirs = self.room.get_available_directions()
        self.assertEqual(dirs, [])

    def test_one_open(self):
        for d in self.room.doors:
            d.empty = True
        self.room.doors[2].empty = False
        self.room.doors[2].locked = False
        dirs = self.room.get_available_directions()
        self.assertEqual(dirs, [2])

    def test_locked_door_excluded(self):
        for d in self.room.doors:
            d.empty = True
        self.room.doors[0].empty = False
        self.room.doors[0].locked = True
        dirs = self.room.get_available_directions()
        self.assertEqual(dirs, [])

    def test_mixed_doors(self):
        for d in self.room.doors:
            d.empty = True
        self.room.doors[0].empty = False
        self.room.doors[0].locked = False
        self.room.doors[1].empty = False
        self.room.doors[1].locked = False
        self.room.doors[2].empty = False
        self.room.doors[2].locked = True
        dirs = self.room.get_available_directions()
        self.assertEqual(dirs, [0, 1])


class TestRoomCanRest(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_can_rest_perfect_room(self):
        furniture = SimpleNamespace(can_rest=True)
        self.room.furniture.append(furniture)
        result, place = self.room.can_rest(mode='full')
        self.assertEqual(result, [])
        self.assertIs(place, furniture)

    def test_simple_mode_returns_bool(self):
        furniture = SimpleNamespace(can_rest=True)
        self.room.furniture.append(furniture)
        self.assertTrue(self.room.can_rest(mode='simple'))

    def test_cant_rest_because_monster(self):
        furniture = SimpleNamespace(can_rest=True)
        self.room.furniture.append(furniture)
        monster = MagicMock()
        self.floor.monsters_in_rooms[self.room] = [monster]
        reasons, _ = self.room.can_rest(mode='full')
        self.assertTrue(any('Враг' in r for r in reasons))

    def test_cant_rest_because_stink(self):
        furniture = SimpleNamespace(can_rest=True)
        self.room.furniture.append(furniture)
        self.room.stink = 2
        reasons, _ = self.room.can_rest(mode='full')
        self.assertTrue(any('воняет' in r for r in reasons))

    def test_cant_rest_because_dark(self):
        furniture = SimpleNamespace(can_rest=True)
        self.room.furniture.append(furniture)
        self.room.light = False
        reasons, _ = self.room.can_rest(mode='full')
        self.assertTrue(any('темно' in r for r in reasons))

    def test_cant_rest_because_no_place(self):
        reasons, place = self.room.can_rest(mode='full')
        self.assertFalse(place)
        self.assertTrue(any('нет места' in r for r in reasons))

    def test_simple_mode_false_when_cant_rest(self):
        self.room.light = False
        self.assertFalse(self.room.can_rest(mode='simple'))


class TestRoomNoise(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room1 = self.floor.plan[0]
        self.room2 = self.floor.plan[1]
        self.floor.monsters_in_rooms[self.room1] = []
        self.floor.monsters_in_rooms[self.room2] = []

    def test_noise_level_1_stays_local(self):
        result = self.room1.noise(1)
        self.assertTrue(result)

    def test_noise_spreads(self):
        with patch.object(Room, 'noise_trigger') as mock_trigger:
            self.room1.noise(2)
            self.assertTrue(mock_trigger.called)


class TestRoomSetStink(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_sets_stink(self):
        self.room.set_stink(2)
        self.assertEqual(self.room.stink, 2)

    def test_doesnt_decrease_stink(self):
        self.room.stink = 3
        self.room.set_stink(1)
        self.assertEqual(self.room.stink, 3)

    def test_increases_stink(self):
        self.room.stink = 1
        self.room.set_stink(3)
        self.assertEqual(self.room.stink, 3)


class TestRoomGetRoomsAround(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_no_open_doors(self):
        for d in self.room.doors:
            d.empty = True
        rooms = self.room.get_rooms_around()
        self.assertEqual(rooms, [])


class TestRoomMonsters(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_empty_returns_empty_list(self):
        self.assertEqual(self.room.monsters(), [])

    def test_first_mode(self):
        m = MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m]
        self.assertIs(self.room.monsters('first'), m)

    def test_random_mode(self):
        m1, m2 = MagicMock(), MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m1, m2]
        result = self.room.monsters('random')
        self.assertIn(result, [m1, m2])

    def test_default_returns_all(self):
        m1, m2 = MagicMock(), MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m1, m2]
        result = self.room.monsters()
        self.assertEqual(result, [m1, m2])


class TestRoomHasAMonster(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_monsters(self):
        self.floor.monsters_in_rooms[self.room] = []
        self.assertFalse(self.room.has_a_monster())

    def test_with_monsters(self):
        self.floor.monsters_in_rooms[self.room] = [MagicMock()]
        self.assertTrue(self.room.has_a_monster())


class TestRoomMonsterInAmbush(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_monsters(self):
        self.floor.monsters_in_rooms[self.room] = []
        self.assertIsNone(self.room.monster_in_ambush())

    def test_no_ambush(self):
        m = MagicMock()
        m.hiding_place = MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m]
        self.assertIsNone(self.room.monster_in_ambush())

    def test_ambush_found(self):
        m = MagicMock()
        m.hiding_place = self.room
        self.floor.monsters_in_rooms[self.room] = [m]
        self.assertIs(self.room.monster_in_ambush(), m)


class TestRoomLock(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_locks_room_and_doors(self):
        for d in self.room.doors:
            d.empty = True
        self.room.doors[0].empty = False
        self.room.lock()
        self.assertTrue(self.room.locked)
        self.assertTrue(self.room.doors[0].locked)


class TestRoomFurnitureTypes(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_empty(self):
        self.assertEqual(self.room.furniture_types(), [])

    def test_unique_types(self):
        f1 = SimpleNamespace(furniture_type='стол')
        f2 = SimpleNamespace(furniture_type='стул')
        f3 = SimpleNamespace(furniture_type='стол')
        self.room.furniture = [f1, f2, f3]
        types = self.room.furniture_types()
        self.assertEqual(types, ['стол', 'стул'])


class TestRoomGetRandomUnlockedFurniture(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_empty_returns_none(self):
        self.assertIsNone(self.room.get_random_unlocked_furniture())

    def test_returns_unlocked(self):
        locked = SimpleNamespace(locked=True)
        unlocked = SimpleNamespace(locked=False)
        self.room.furniture = [locked, unlocked]
        result = self.room.get_random_unlocked_furniture()
        self.assertIs(result, unlocked)

    def test_all_locked_returns_none(self):
        self.room.furniture = [SimpleNamespace(locked=True), SimpleNamespace(locked=True)]
        self.assertIsNone(self.room.get_random_unlocked_furniture())


class TestRoomGetStinkText(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_stink(self):
        self.assertIsNone(self.room.get_stink_text())

    def test_stink_level_1(self):
        self.room.stink = 1
        result = self.room.get_stink_text()
        self.assertIn('Немного', result)

    def test_stink_level_2(self):
        self.room.stink = 2
        result = self.room.get_stink_text()
        self.assertIn('Сильно', result)

    def test_stink_level_3(self):
        self.room.stink = 3
        result = self.room.get_stink_text()
        self.assertIn('Невыносимо', result)


class TestRoomGetDecorationForShow(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_torch(self):
        self.room.torch = False
        result = self.room.get_decoration_for_show()
        self.assertEqual(result, self.room.decoration1)

    def test_with_torch(self):
        self.room.torch = MagicMock()
        result = self.room.get_decoration_for_show()
        self.assertIn('факелом', result)


class TestRoomGetLaddersText(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_ladders(self):
        result = self.room.get_ladders_text()
        self.assertEqual(result, [])

    def test_with_ladder_down(self):
        ladder = MagicMock()
        ladder.show_in_room_as_ladder_down.return_value = 'Лестница вниз'
        self.room.ladder_down = ladder
        result = self.room.get_ladders_text()
        self.assertIn('Лестница вниз', result)

    def test_with_ladder_up(self):
        ladder = MagicMock()
        ladder.show_in_room_as_ladder_up.return_value = 'Лестница вверх'
        self.room.ladder_up = ladder
        result = self.room.get_ladders_text()
        self.assertIn('Лестница вверх', result)


class TestRoomGetMonsterTextForShow(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_no_monsters(self):
        result = self.room.get_monster_text_for_show()
        self.assertEqual(result, ['Не видно ничего интересного.'])

    def test_with_monster(self):
        m = MagicMock()
        m.state = 'сидит'
        m.name = 'Гоблин'
        self.floor.monsters_in_rooms[self.room] = [m]
        result = self.room.get_monster_text_for_show()
        self.assertTrue(len(result) > 0)
        self.assertTrue(any('Гоблин' in line for line in result))


class TestRoomShowWithLightOff(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_dark_room_no_monster(self):
        result = self.room.show_with_light_off()
        self.assertTrue(any('нет ни одного источника света' in line for line in result))

    def test_dark_room_with_monster(self):
        m = MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m]
        result = self.room.show_with_light_off()
        self.assertTrue(any('кто-то шумно дышит' in line for line in result))

    def test_dark_room_with_stink(self):
        self.room.stink = 2
        result = self.room.show_with_light_off()
        self.assertTrue(any('воняет' in line for line in result))


class TestRoomShowWithLightOn(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_basic_room(self):
        player = MagicMock()
        player.name = 'Герой'
        result = self.room.show_with_light_on(player)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_room_with_trader(self):
        player = MagicMock()
        player.name = 'Герой'
        self.room.trader = MagicMock()
        self.room.trader.show.return_value = 'Торговец'
        result = self.room.show_with_light_on(player)
        self.assertIn('Торговец', result)

    def test_room_with_corpse(self):
        player = MagicMock()
        player.name = 'Герой'
        c = MagicMock()
        c.description = 'Труп'
        self.room.morgue = [c]
        result = self.room.show_with_light_on(player)
        self.assertIn('Труп', result)

    def test_room_with_monster(self):
        player = MagicMock()
        player.name = 'Герой'
        m = MagicMock()
        m.state = 'стоит'
        m.name = 'Орк'
        self.floor.monsters_in_rooms[self.room] = [m]
        result = self.room.show_with_light_on(player)
        self.assertTrue(any('Орк' in line for line in result))

    def test_room_with_stink(self):
        player = MagicMock()
        player.name = 'Герой'
        self.room.stink = 1
        result = self.room.show_with_light_on(player)
        self.assertTrue(any('воняет' in line for line in result))


class TestRoomShowThroughKeyHole(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []
        self.who = MagicMock()
        self.who.name = 'Герой'

    def test_with_trader(self):
        self.room.trader = MagicMock()
        self.room.trader.show_through_key_hole.return_value = 'Торговец за дверью'
        result = self.room.show_through_key_hole(self.who)
        self.assertIn('Торговец за дверью', result)

    def test_no_monster(self):
        result = self.room.show_through_key_hole(self.who)
        self.assertTrue(any('не может ничего толком разглядеть' in line for line in result))

    def test_with_monster(self):
        m = MagicMock()
        m.key_hole = 'видит что-то ужасное'
        self.floor.monsters_in_rooms[self.room] = [m]
        result = self.room.show_through_key_hole(self.who)
        self.assertTrue(any('видит что-то ужасное' in line for line in result))

    def test_with_stink(self):
        self.room.stink = 2
        result = self.room.show_through_key_hole(self.who)
        self.assertTrue(any('воняет' in line for line in result))


class TestRoomExamine(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_examine_light_on(self):
        who = MagicMock()
        self.room.light = True
        result = self.room.examine(who)
        self.assertIsInstance(result, list)

    def test_examine_light_off(self):
        who = MagicMock()
        self.room.light = False
        result = self.room.examine(who)
        self.assertIsInstance(result, list)


class TestRoomMap(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_map_dark_returns_false(self):
        self.room.light = False
        self.assertFalse(self.room.map())

    def test_map_light_returns_true(self):
        with patch('src.class_room.pprint'):
            self.assertTrue(self.room.map())


class TestRoomGetSymbolForPlan(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_no_monster_no_trader(self):
        self.room.trader = None
        self.assertEqual(self.room.get_symbol_for_plan(), ' ')

    def test_with_trader(self):
        self.room.trader = MagicMock()
        self.assertEqual(self.room.get_symbol_for_plan(), '₽')

    def test_with_single_monster(self):
        m = MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m]
        self.assertEqual(self.room.get_symbol_for_plan(), '~')

    def test_with_multiple_monsters(self):
        self.floor.monsters_in_rooms[self.room] = [MagicMock(), MagicMock()]
        self.assertEqual(self.room.get_symbol_for_plan(), '≈')


class TestRoomGetMonstersSymbol(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_single_monster(self):
        self.floor.monsters_in_rooms[self.room] = [MagicMock()]
        self.assertEqual(self.room.get_monsters_symbol(), '~')

    def test_multiple_monsters(self):
        self.floor.monsters_in_rooms[self.room] = [MagicMock(), MagicMock()]
        self.assertEqual(self.room.get_monsters_symbol(), '≈')


class TestRoomGetNumberOfMonsters(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_zero(self):
        self.floor.monsters_in_rooms[self.room] = []
        self.assertEqual(self.room.get_number_of_monsters(), 0)

    def test_three(self):
        self.floor.monsters_in_rooms[self.room] = [MagicMock(), MagicMock(), MagicMock()]
        self.assertEqual(self.room.get_number_of_monsters(), 3)


class TestRoomPlanLines(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_second_line_no_ladder_up(self):
        self.room.ladder_up = self.game.empty_thing
        result = self.room.get_second_line_for_plan()
        self.assertEqual(result, '║   ║')

    def test_second_line_with_ladder_up(self):
        self.room.ladder_up = MagicMock()
        result = self.room.get_second_line_for_plan()
        self.assertIn('#', result)

    def test_fourth_line_no_ladder_down(self):
        self.room.ladder_down = self.game.empty_thing
        result = self.room.get_fourth_line_for_plan()
        self.assertEqual(result, '║   ║')

    def test_fourth_line_with_ladder_down(self):
        self.room.ladder_down = MagicMock()
        result = self.room.get_fourth_line_for_plan()
        self.assertIn('#', result)


class TestRoomTurnOnLight(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_turns_on_light(self):
        who = MagicMock()
        who.name = 'Герой'
        self.room.light = False
        result = self.room.turn_on_light(who)
        self.assertTrue(self.room.light)
        self.assertIsInstance(result, list)

    def test_frightening_monster_increases_fear(self):
        who = MagicMock()
        who.name = 'Герой'
        who.fear = 0
        self.room.light = False
        m = MagicMock()
        m.frightening = True
        self.floor.monsters_in_rooms[self.room] = [m]
        self.room.turn_on_light(who)
        self.assertGreater(who.fear, 0)

    def test_non_frightening_monster_no_fear(self):
        who = MagicMock()
        who.name = 'Герой'
        who.fear = 0
        self.room.light = False
        m = MagicMock()
        m.frightening = False
        self.floor.monsters_in_rooms[self.room] = [m]
        self.room.turn_on_light(who)
        self.assertEqual(who.fear, 0)


class TestRoomGetNamesList(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_returns_room_names(self):
        names = self.room.get_names_list()
        self.assertIn('комната', names)
        self.assertIn('комнату', names)


class TestRoomClearFromMonsters(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_clears_monsters(self):
        m1 = MagicMock()
        m2 = MagicMock()
        self.floor.monsters_in_rooms[self.room] = [m1, m2]
        self.room.clear_from_monsters()
        m1.place.assert_called_once_with(self.room.floor, old_place=self.room)
        m2.place.assert_called_once_with(self.room.floor, old_place=self.room)


class TestRoomShow(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_show_light_on(self):
        self.room.light = True
        player = MagicMock()
        player.name = 'Герой'
        with patch('src.class_room.tprint'):
            self.room.show(player)

    def test_show_light_off(self):
        self.room.light = False
        player = MagicMock()
        player.name = 'Герой'
        with patch('src.class_room.tprint'):
            self.room.show(player)


class TestRoomAdd(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_add_item_to_room(self):
        item = MagicMock()
        self.room.add(item)
        self.assertIn(item, self.room.loot.pile)


class TestRoomGetRandomUnlockFurniture(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_no_furniture_returns_none(self):
        self.assertIsNone(self.room.get_random_unlocked_furniture())

    def test_all_locked_returns_none(self):
        self.room.furniture = [SimpleNamespace(locked=True)]
        self.assertIsNone(self.room.get_random_unlocked_furniture())

    def test_returns_unlocked(self):
        unlocked = SimpleNamespace(locked=False)
        self.room.furniture = [unlocked]
        self.assertIs(self.room.get_random_unlocked_furniture(), unlocked)


class TestRoomMapForExamine(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]
        self.floor.monsters_in_rooms[self.room] = []

    def test_calls_map(self):
        who = MagicMock()
        with patch.object(Room, 'map') as mock_map:
            self.room.map_for_examine(who)
            mock_map.assert_called_once()


class TestRoomDecorate(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_decorate_sets_attributes(self):
        self.room.decorate()
        self.assertTrue(hasattr(self.room, 'decoration1'))
        self.assertTrue(hasattr(self.room, 'decoration2'))
        self.assertTrue(hasattr(self.room, 'decoration3'))
        self.assertTrue(hasattr(self.room, 'decoration4'))
        self.assertTrue(hasattr(self.room, 'description'))


class TestRoomGenerateSecrets(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_bare_floor(self.game)
        self.room = self.floor.plan[0]

    def test_empty_secrets(self):
        self.room.secrets = []
        self.room.has_secrets = False
        self.room.generate_secrets([])
        self.assertFalse(self.room.has_secrets)


if __name__ == '__main__':
    unittest.main()
