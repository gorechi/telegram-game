import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.class_allies import Trader
from src.class_book import Book
from src.class_castle import Floor
from src.class_game import Game
from src.class_items import Map, Matches
from src.class_monsters import Monster
from src.class_potions import Potion
from src.class_protection import Armor, Shield
from src.class_room import Ladder
from src.class_rune import Rune
from src.class_weapon import Weapon

Game.__del__ = lambda self: None


def make_game():
    return Game(chat_id='test', bot=MagicMock())


def make_floor(game, template_index=0):
    controller = game.floors_controller
    return controller.create_object_from_template(controller.templates[template_index])


def make_small_floor(game):
    Template = game.floors_controller.Template
    template = Template(
        class_name='Floor',
        floor_number=99,
        rows=1,
        rooms=1,
        traps_difficulty=4,
        how_many={'монстры': 1, 'спички': 1, 'оружие': 1, 'щит': 1, 'доспех': 1,
                  'зелье': 1, 'мебель': 1, 'книга': 1, 'очаг': 1, 'руна': 1,
                  'торговец': 1, 'лестницы': 1, 'ловушка': 1},
        how_many_dark_rooms=0,
        how_many_locked_rooms=0,
        money_in_locked_rooms={'dice': True, 'value': 40},
        boss=False,
    )
    return game.floors_controller.create_object_from_template(template)


def find_placed_items(floor, *classes):
    found = []
    for room in floor.plan:
        for loot in (room.loot, room.secret_loot):
            found.extend(i for i in loot.pile if isinstance(i, classes))
        for furniture in room.furniture:
            found.extend(i for i in furniture.loot.pile if isinstance(i, classes))
        for secret in room.secrets:
            found.extend(i for i in secret.loot.pile if isinstance(i, classes))
        for monster in floor.monsters_in_rooms.get(room, []):
            found.extend(i for i in monster.loot.pile if isinstance(i, classes))
            for slot in (monster.weapon, monster.armor, monster.shield):
                if isinstance(slot, classes) and not slot.empty:
                    found.append(slot)
    return found


class TestFloorInit(unittest.TestCase):
    def test_init(self):
        game = make_game()
        floor = Floor(game)
        self.assertIs(floor.game, game)
        self.assertEqual(floor.monsters_in_rooms, {})


class TestFloorOnCreate(unittest.TestCase):
    def test_on_create(self):
        floor = Floor(make_game())
        self.assertIs(floor.on_create(), True)


class TestCreateLadders(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_floor(self.game, 0)
        self.next_floor = make_floor(self.game, 1)

    def test_creates_ladders_and_enter_points(self):
        result = self.floor.create_ladders(next_floor=self.next_floor)
        self.assertIs(result, True)
        ladder_up_rooms = [room for room in self.floor.plan if room.ladder_up]
        ladder_down_rooms = [room for room in self.next_floor.plan if room.ladder_down]
        self.assertEqual(len(ladder_up_rooms), self.floor.how_many['лестницы'])
        self.assertEqual(len(ladder_down_rooms), self.floor.how_many['лестницы'])
        for room in ladder_up_rooms:
            self.assertIsInstance(room.ladder_up, Ladder)
        for room in ladder_down_rooms:
            self.assertIsInstance(room.ladder_down, Ladder)
            self.assertTrue(room.enter_point)

    def test_returns_false_when_ladder_up_rooms_exhausted(self):
        self.floor.how_many['лестницы'] = 2
        result = self.floor.create_ladders(next_floor=make_small_floor(self.game))
        self.assertIs(result, False)
        self.assertEqual(sum(1 for room in self.floor.plan if room.ladder_up), 1)

    def test_returns_false_when_ladder_down_room_missing(self):
        self.next_floor.get_room_to_place_ladder_down = lambda: None
        result = self.floor.create_ladders(next_floor=self.next_floor)
        self.assertIs(result, False)
        self.assertEqual(sum(1 for room in self.floor.plan if room.ladder_up), 0)


class TestGetRoomToPlaceLadderUp(unittest.TestCase):
    def setUp(self):
        self.floor = make_floor(make_game(), 0)

    def test_returns_room_from_plan(self):
        room = self.floor.get_room_to_place_ladder_up()
        self.assertIn(room, self.floor.plan)
        self.assertFalse(room.ladder_up)

    def test_returns_none_when_all_rooms_have_ladder(self):
        for room in self.floor.plan:
            room.ladder_up = object()
        self.assertIsNone(self.floor.get_room_to_place_ladder_up())


class TestGetRoomToPlaceLadderDown(unittest.TestCase):
    def setUp(self):
        self.floor = make_floor(make_game(), 0)

    def test_returns_room_from_plan(self):
        room = self.floor.get_room_to_place_ladder_down()
        self.assertIn(room, self.floor.plan)
        self.assertFalse(room.ladder_down)

    def test_returns_none_when_all_rooms_have_ladder(self):
        for room in self.floor.plan:
            room.ladder_down = object()
        self.assertIsNone(self.floor.get_room_to_place_ladder_down())


class TestPlaceMatches(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_matches()
        self.assertEqual(len(find_placed_items(floor, Matches)), floor.how_many['спички'])


class TestPlaceTraders(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_traders()
        traders_rooms = [room for room in floor.plan if room.trader]
        self.assertEqual(len(traders_rooms), floor.how_many['торговец'])
        for room in traders_rooms:
            self.assertIsInstance(room.trader, Trader)


class TestPlaceMap(unittest.TestCase):
    def test_places_one_map(self):
        floor = make_floor(make_game(), 0)
        floor.place_map()
        self.assertEqual(len(find_placed_items(floor, Map)), 1)


class TestPlaceBooks(unittest.TestCase):
    def test_places_exact_count_in_furniture(self):
        floor = make_floor(make_game(), 0)
        floor.place_furniture()
        floor.place_books()
        self.assertEqual(len(find_placed_items(floor, Book)), floor.how_many['книга'])


class TestPlaceRunes(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_runes()
        self.assertEqual(len(find_placed_items(floor, Rune)), floor.how_many['руна'])


class TestPlacePotions(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_potions()
        self.assertEqual(len(floor.all_potions), floor.how_many['зелье'])
        self.assertEqual(len(find_placed_items(floor, Potion)), floor.how_many['зелье'])


class TestPlaceArmor(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_armor()
        self.assertEqual(len(floor.all_armor), floor.how_many['доспех'])
        self.assertEqual(len(find_placed_items(floor, Armor)), floor.how_many['доспех'])


class TestPlaceShields(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_shields()
        self.assertEqual(len(floor.all_shields), floor.how_many['щит'])
        self.assertEqual(len(find_placed_items(floor, Shield)), floor.how_many['щит'])


class TestPlaceWeapons(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_weapons()
        self.assertEqual(len(floor.all_weapon), floor.how_many['оружие'])
        placed = [w for w in find_placed_items(floor, Weapon) if w in floor.all_weapon]
        self.assertEqual(len(placed), floor.how_many['оружие'])


class TestPlaceMonsters(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_monsters()
        self.assertEqual(len(floor.all_monsters), floor.how_many['монстры'])
        total = sum(len(monsters) for monsters in floor.monsters_in_rooms.values())
        self.assertEqual(total, floor.how_many['монстры'])
        for monsters in floor.monsters_in_rooms.values():
            self.assertLessEqual(len(monsters), 1)
        for monster in floor.all_monsters:
            self.assertIsInstance(monster, Monster)
            self.assertIs(monster.floor, floor)


class TestPlaceRestPlaces(unittest.TestCase):
    def test_places_exact_count_on_plain_floor(self):
        floor = make_floor(make_game(), 0)
        floor.place_rest_places()
        rest_places = [f for room in floor.plan for f in room.furniture if f.can_rest]
        self.assertEqual(len(rest_places), floor.how_many['очаг'])

    def test_places_rest_place_on_enter_point(self):
        floor = make_floor(make_game(), 0)
        floor.how_many['очаг'] = 1
        floor.plan[0].enter_point = True
        floor.place_rest_places()
        self.assertTrue(any(f.can_rest for f in floor.plan[0].furniture))


class TestPlaceFurniture(unittest.TestCase):
    def test_places_exact_count(self):
        floor = make_floor(make_game(), 0)
        floor.place_furniture()
        furniture = [f for room in floor.plan for f in room.furniture if not f.can_rest]
        self.assertEqual(len(furniture), floor.how_many['мебель'])


class TestInhabit(unittest.TestCase):
    def setUp(self):
        self.floor = make_floor(make_game(), 0)
        self.floor.inhabit()

    def test_populates_collections(self):
        self.assertEqual(len(self.floor.all_monsters), self.floor.how_many['монстры'])
        self.assertEqual(len(self.floor.all_weapon), self.floor.how_many['оружие'])
        self.assertEqual(len(self.floor.all_shields), self.floor.how_many['щит'])
        self.assertEqual(len(self.floor.all_armor), self.floor.how_many['доспех'])
        self.assertEqual(len(self.floor.all_potions), self.floor.how_many['зелье'])

    def test_places_all_items(self):
        self.assertEqual(len(find_placed_items(self.floor, Book)), self.floor.how_many['книга'])
        self.assertEqual(len(find_placed_items(self.floor, Rune)), self.floor.how_many['руна'])
        self.assertEqual(len(find_placed_items(self.floor, Matches)), self.floor.how_many['спички'])
        self.assertEqual(len(find_placed_items(self.floor, Map)), 1)
        self.assertLessEqual(len(find_placed_items(self.floor, Shield)), self.floor.how_many['щит'])
        self.assertLessEqual(len(find_placed_items(self.floor, Armor)), self.floor.how_many['доспех'])
        self.assertEqual(len(find_placed_items(self.floor, Potion)), self.floor.how_many['зелье'])
        placed_weapons = [w for w in find_placed_items(self.floor, Weapon) if w in self.floor.all_weapon]
        self.assertLessEqual(len(placed_weapons), self.floor.how_many['оружие'])

    def test_places_actors(self):
        self.assertEqual(sum(1 for room in self.floor.plan if room.trader), self.floor.how_many['торговец'])
        rest_places = sum(1 for room in self.floor.plan for f in room.furniture if f.can_rest)
        self.assertGreaterEqual(rest_places, self.floor.how_many['очаг'])
        self.assertLessEqual(rest_places, self.floor.how_many['очаг'] + self.floor.how_many['торговец'])
        self.assertEqual(sum(len(m) for m in self.floor.monsters_in_rooms.values()),
                         self.floor.how_many['монстры'])


class TestInhabitBossFloor(unittest.TestCase):
    def test_creates_boss(self):
        floor = make_floor(make_game(), 3)
        floor.inhabit()
        self.assertEqual(len(floor.all_monsters), floor.how_many['монстры'] + 1)


class TestActivateTraps(unittest.TestCase):
    def make_trap_furniture(self, activated=False):
        trap = MagicMock()
        trap.activated = activated
        return SimpleNamespace(can_contain_trap=True, trap=trap)

    def setUp(self):
        self.floor = make_floor(make_game(), 0)

    def test_activates_exact_count(self):
        self.floor.all_furniture = [self.make_trap_furniture() for _ in range(5)]
        self.floor.activate_traps()
        activated = [f.trap for f in self.floor.all_furniture if f.trap.activate.called]
        self.assertEqual(len(activated), self.floor.how_many['ловушка'])
        for trap in activated:
            trap.set_difficulty.assert_called_with(self.floor.traps_difficulty)

    def test_skips_already_activated_traps(self):
        self.floor.all_furniture = [self.make_trap_furniture() for _ in range(5)]
        for f in self.floor.all_furniture[:2]:
            f.trap.activated = True
        self.floor.activate_traps()
        activated = [f.trap for f in self.floor.all_furniture if f.trap.activate.called]
        self.assertEqual(len(activated), self.floor.how_many['ловушка'])

    def test_raises_when_not_enough_furniture(self):
        self.floor.all_furniture = [self.make_trap_furniture() for _ in range(2)]
        with self.assertRaises(ValueError):
            self.floor.activate_traps()

    def test_raises_when_no_furniture(self):
        self.floor.all_furniture = []
        with self.assertRaises(ValueError):
            self.floor.activate_traps()


class TestSecretRooms(unittest.TestCase):
    def setUp(self):
        self.floor = make_floor(make_game(), 0)
        for room in self.floor.plan:
            room.has_secrets = False

    def test_returns_only_rooms_with_secrets(self):
        self.floor.plan[1].has_secrets = True
        self.floor.plan[3].has_secrets = True
        self.assertEqual(self.floor.secret_rooms(), [self.floor.plan[1], self.floor.plan[3]])

    def test_returns_empty_list(self):
        self.assertEqual(self.floor.secret_rooms(), [])


class TestStinkMap(unittest.TestCase):
    def test_does_not_crash(self):
        floor = make_floor(make_game(), 0)
        floor.plan[0].stink = 2
        self.assertIsNone(floor.stink_map())


class TestGetRandomRoomWithFurniture(unittest.TestCase):
    def test_returns_none_without_furniture(self):
        floor = make_floor(make_game(), 0)
        self.assertIsNone(floor.get_random_room_with_furniture())

    def test_returns_room_with_furniture(self):
        floor = make_floor(make_game(), 0)
        floor.place_furniture()
        room = floor.get_random_room_with_furniture()
        self.assertIn(room, floor.plan)
        self.assertTrue(room.furniture)


class TestGetRandomUnlockedRoom(unittest.TestCase):
    def test_returns_unlocked_room(self):
        floor = make_floor(make_game(), 0)
        room = floor.get_random_unlocked_room()
        self.assertIn(room, floor.plan)
        self.assertFalse(room.locked)

    def test_returns_none_when_all_locked(self):
        floor = make_floor(make_game(), 0)
        for room in floor.plan:
            room.locked = True
        self.assertIsNone(floor.get_random_unlocked_room())


class TestGetEnterPoints(unittest.TestCase):
    def test_returns_empty_list_by_default(self):
        floor = make_floor(make_game(), 0)
        self.assertEqual(floor.get_enter_points(), [])

    def test_returns_rooms_with_enter_point(self):
        floor = make_floor(make_game(), 0)
        floor.plan[0].enter_point = True
        floor.plan[2].enter_point = True
        self.assertEqual(floor.get_enter_points(), [floor.plan[0], floor.plan[2]])


class TestGetRoomToPlaceFurniture(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.floor = make_floor(self.game, 0)

    def test_returns_room_without_that_furniture_type(self):
        for room in self.floor.plan:
            room.furniture.clear()
        result = self.floor.get_room_to_place_furniture(1)
        self.assertIsNotNone(result)
        self.assertNotIn(1, result.furniture_types())

    def test_returns_none_when_all_rooms_have_that_type(self):
        for room in self.floor.plan:
            mock_furniture = MagicMock()
            mock_furniture.furniture_type = 1
            room.furniture = [mock_furniture]
        result = self.floor.get_room_to_place_furniture(1)
        self.assertIsNone(result)

    def test_returns_any_available_room(self):
        for room in self.floor.plan:
            room.furniture.clear()
        results = {self.floor.get_room_to_place_furniture(1) for _ in range(20)}
        self.assertTrue(len(results) > 1, "Должен возвращать разные комнаты")


if __name__ == '__main__':
    unittest.main()
