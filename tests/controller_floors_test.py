import json
import unittest
from unittest.mock import MagicMock

from src.class_basic import Money
from src.class_castle import Floor
from src.class_dice import Dice
from src.class_game import Game
from src.class_items import Key
from src.class_room import Room
from src.controllers.controller_floors import FloorsController

Game.__del__ = lambda self: None


def load_templates():
    with open('json/floors.json', encoding='utf-8') as f:
        return json.load(f)


def make_game():
    return Game(chat_id='test', bot=MagicMock())


def make_floor(game, template_index=0):
    controller = game.floors_controller
    return controller.create_object_from_template(controller.templates[template_index])


def make_bare_floor(game, rows=5, rooms=5):
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


class TestFloorsControllerInit(unittest.TestCase):
    def test_init(self):
        game = MagicMock()
        controller = FloorsController(game)
        self.assertIs(controller.game, game)
        self.assertEqual(controller.how_many, 0)
        self.assertEqual(controller.all_objects, [])
        self.assertEqual(len(controller.templates), len(load_templates()))


class TestFloorsControllerTemplate(unittest.TestCase):
    def test_template_fields(self):
        template = FloorsController.Template(
            class_name='Floor',
            floor_number=1,
            rows=5,
            rooms=5,
            traps_difficulty=4,
            how_many={'монстры': 10},
            how_many_dark_rooms=4,
            how_many_locked_rooms=3,
            money_in_locked_rooms={'dice': True, 'value': 40},
            boss=False,
        )
        self.assertEqual(template.class_name, 'Floor')
        self.assertEqual(template.floor_number, 1)
        self.assertEqual(template.rows, 5)
        self.assertEqual(template.rooms, 5)
        self.assertEqual(template.traps_difficulty, 4)
        self.assertEqual(template.how_many, {'монстры': 10})
        self.assertEqual(template.how_many_dark_rooms, 4)
        self.assertEqual(template.how_many_locked_rooms, 3)
        self.assertEqual(template.money_in_locked_rooms, {'dice': True, 'value': 40})
        self.assertFalse(template.boss)

    def test_templates_loaded_from_json(self):
        controller = FloorsController(make_game())
        for template_data in load_templates():
            template = [t for t in controller.templates if t.floor_number == template_data['floor_number']][0]
            self.assertEqual(template.class_name, template_data['class_name'])
            self.assertEqual(template.rows, template_data['rows'])
            self.assertEqual(template.rooms, template_data['rooms'])
            self.assertEqual(template.how_many, template_data['how_many'])
            self.assertEqual(template.boss, template_data['boss'])


class TestCreateObjectFromTemplate(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller

    def test_creates_floor_from_first_template(self):
        floor = self.controller.create_object_from_template(self.controller.templates[0])
        self.assertIsInstance(floor, Floor)
        self.assertEqual(floor.rows, 5)
        self.assertEqual(floor.rooms, 5)
        self.assertEqual(floor.how_many_locked_rooms, 3)
        self.assertIsInstance(floor.money_in_locked_rooms, Dice)
        self.assertEqual(len(floor.plan), 25)
        self.assertEqual(sum(1 for room in floor.plan if room.locked), 3)
        self.assertEqual(sum(1 for room in floor.plan if not room.light), 4)
        self.assertIsNotNone(floor.directions_dict)

    def test_how_many_increments(self):
        before = self.controller.how_many
        self.controller.create_object_from_template(self.controller.templates[0])
        self.assertEqual(self.controller.how_many, before + 1)
        self.assertEqual(len(self.controller.all_objects), before + 1)


class TestAdditionalActions(unittest.TestCase):
    def test_additional_actions(self):
        game = make_game()
        controller = game.floors_controller
        floor = Floor(game)
        floor.rows = 5
        floor.rooms = 5
        floor.how_many_locked_rooms = 0
        floor.money_in_locked_rooms = Dice([40])
        floor.how_many_dark_rooms = 0
        result = controller.additional_actions(floor)
        self.assertIs(result, True)
        self.assertEqual(len(floor.plan), 25)
        self.assertIsNotNone(floor.directions_dict)


class TestCreateRooms(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller

    def test_creates_rooms_with_positions(self):
        floor = Floor(self.game)
        floor.rows = 5
        floor.rooms = 5
        self.controller.create_rooms(floor)
        self.assertEqual(len(floor.plan), 25)
        for index, room in enumerate(floor.plan):
            self.assertIsInstance(room, Room)
            self.assertEqual(room.position, index)
        for room in floor.plan:
            self.assertIn(room, floor.monsters_in_rooms)
            self.assertEqual(floor.monsters_in_rooms[room], [])


class TestCreateDoors(unittest.TestCase):
    def setUp(self):
        self.controller = FloorsController(make_game())

    def test_returns_four_doors_per_room(self):
        all_doors = self.controller.create_doors(5, 5)
        self.assertEqual(len(all_doors), 25)
        for doors in all_doors:
            self.assertEqual(len(doors), 4)

    def test_every_room_has_at_least_two_active_doors(self):
        all_doors = self.controller.create_doors(5, 5)
        for doors in all_doors:
            self.assertGreaterEqual(sum(not door.empty for door in doors), 2)

    def test_neighbours_share_empty_state(self):
        all_doors = self.controller.create_doors(5, 5)
        for index in range(len(all_doors) - 1):
            left = all_doors[index][1]
            right = all_doors[index + 1][3]
            self.assertEqual(left.empty, right.empty)

    def test_single_room_has_no_active_doors(self):
        all_doors = self.controller.create_doors(1, 1)
        self.assertEqual(len(all_doors), 1)
        self.assertTrue(all(door.empty for door in all_doors[0]))

    def test_single_row_has_no_active_doors(self):
        all_doors = self.controller.create_doors(1, 5)
        self.assertEqual(len(all_doors), 5)
        for doors in all_doors:
            self.assertTrue(all(door.empty for door in doors))

    def test_single_column_has_no_active_doors(self):
        all_doors = self.controller.create_doors(3, 1)
        self.assertEqual(len(all_doors), 3)
        for doors in all_doors:
            self.assertTrue(all(door.empty for door in doors))


class TestCreateRoomsPlan(unittest.TestCase):
    def setUp(self):
        self.controller = FloorsController(make_game())

    def test_5x5_plan(self):
        plan = self.controller.create_rooms_plan(5, 5)
        self.assertEqual(plan, [2] * 5 + [2, 3, 3, 3, 2] * 3 + [2] * 5)

    def test_3x3_plan(self):
        plan = self.controller.create_rooms_plan(3, 3)
        self.assertEqual(plan, [2, 2, 2, 2, 3, 2, 2, 2, 2])

    def test_1x3_plan(self):
        plan = self.controller.create_rooms_plan(1, 3)
        self.assertEqual(plan, [2, 2, 2])

    def test_2x4_plan(self):
        plan = self.controller.create_rooms_plan(2, 4)
        self.assertEqual(plan, [2, 2, 2, 2, 2, 2, 2, 2])


class TestLockDoors(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller
        self.floor = make_bare_floor(self.game)

    def test_locks_exact_count_and_places_money_and_keys(self):
        money_dice = MagicMock()
        money_dice.roll.return_value = 40
        self.floor.money_in_locked_rooms = money_dice
        self.floor.how_many_locked_rooms = 3
        result = self.controller.lock_doors(self.floor)
        self.assertIs(result, True)
        locked_rooms = [room for room in self.floor.plan if room.locked]
        self.assertEqual(len(locked_rooms), 3)
        self.assertFalse(self.floor.plan[0].locked)
        for room in locked_rooms:
            money = [item for item in room.loot.pile if isinstance(item, Money)]
            self.assertEqual(len(money), 1)
            self.assertEqual(money[0].how_much_money, 40)
        self.assertEqual(len(find_placed_items(self.floor, Key)), 3)

    def test_locks_nothing_when_zero(self):
        result = self.controller.lock_doors(self.floor)
        self.assertIs(result, True)
        self.assertEqual(sum(1 for room in self.floor.plan if room.locked), 0)
        self.assertEqual(len(find_placed_items(self.floor, Key)), 0)

    def test_raises_when_too_many_rooms(self):
        self.floor.how_many_locked_rooms = len(self.floor.plan)
        with self.assertRaises(ValueError):
            self.controller.lock_doors(self.floor)


class TestLightsOff(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller
        self.floor = make_bare_floor(self.game)

    def test_darkens_exact_count(self):
        self.floor.how_many_dark_rooms = 4
        self.controller.lights_off(self.floor)
        self.assertEqual(sum(1 for room in self.floor.plan if not room.light), 4)

    def test_darkens_single_room(self):
        self.floor.how_many_dark_rooms = 1
        self.controller.lights_off(self.floor)
        self.assertEqual(sum(1 for room in self.floor.plan if not room.light), 1)

    def test_darkens_nothing_when_zero(self):
        self.controller.lights_off(self.floor)
        self.assertEqual(sum(1 for room in self.floor.plan if not room.light), 0)


class TestGenerateDirections(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller

    def test_directions_values(self):
        floor = Floor(self.game)
        floor.rooms = 5
        self.controller.generate_directions(floor)
        self.assertEqual(floor.directions_dict[0], -5)
        self.assertEqual(floor.directions_dict[1], 1)
        self.assertEqual(floor.directions_dict[2], 5)
        self.assertEqual(floor.directions_dict[3], -1)
        self.assertEqual(floor.directions_dict['наверх'], -5)
        self.assertEqual(floor.directions_dict['вверх'], -5)
        self.assertEqual(floor.directions_dict['верх'], -5)
        self.assertEqual(floor.directions_dict['вниз'], 5)
        self.assertEqual(floor.directions_dict['низ'], 5)
        self.assertEqual(floor.directions_dict['направо'], 1)
        self.assertEqual(floor.directions_dict['вправо'], 1)
        self.assertEqual(floor.directions_dict['право'], 1)
        self.assertEqual(floor.directions_dict['налево'], -1)
        self.assertEqual(floor.directions_dict['влево'], -1)
        self.assertEqual(floor.directions_dict['лево'], -1)

    def test_single_room_floor(self):
        floor = Floor(self.game)
        floor.rooms = 1
        self.controller.generate_directions(floor)
        self.assertEqual(floor.directions_dict[0], -1)
        self.assertEqual(floor.directions_dict[2], 1)


class TestCreateCastle(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller

    def test_creates_four_floors(self):
        floors = self.controller.create_castle()
        self.assertEqual(len(floors), 4)
        self.assertEqual([floor.floor_number for floor in floors], [1, 2, 3, 4])

    def test_entry_point_on_first_floor(self):
        floors = self.controller.create_castle()
        self.assertTrue(floors[0].plan[0].enter_point)

    def test_ladders_connect_floors(self):
        floors = self.controller.create_castle()
        self.assertEqual(sum(1 for room in floors[0].plan if room.ladder_up), 2)
        self.assertEqual(sum(1 for room in floors[1].plan if room.ladder_down), 2)
        self.assertEqual(sum(1 for room in floors[3].plan if room.ladder_up), 0)

    def test_inhabits_floors(self):
        floors = self.controller.create_castle()
        self.assertEqual(len(floors[0].all_monsters), floors[0].how_many['монстры'])
        self.assertEqual(len(floors[3].all_monsters), floors[3].how_many['монстры'] + 1)
        for floor in floors:
            self.assertEqual(len(floor.all_weapon), floor.how_many['оружие'])


class TestCreateLadders(unittest.TestCase):
    def setUp(self):
        self.game = make_game()
        self.controller = self.game.floors_controller
        self.floor = make_floor(self.game, 0)
        self.next_floor = make_floor(self.game, 1)
        self.controller.floors = [self.floor, self.next_floor]

    def test_creates_ladders_and_entry_point(self):
        result = self.controller.create_ladders()
        self.assertIs(result, True)
        self.assertTrue(self.floor.plan[0].enter_point)
        self.assertEqual(sum(1 for room in self.floor.plan if room.ladder_up), self.floor.how_many['лестницы'])
        self.assertEqual(sum(1 for room in self.next_floor.plan if room.ladder_down),
                         self.floor.how_many['лестницы'])


class TestInhabitFloors(unittest.TestCase):
    def test_inhabits_all_floors(self):
        game = make_game()
        controller = game.floors_controller
        controller.floors = [make_floor(game, 0), make_floor(game, 1)]
        result = controller.inhabit_floors()
        self.assertIs(result, True)
        for floor in controller.floors:
            self.assertEqual(len(floor.all_monsters), floor.how_many['монстры'])
            self.assertEqual(len(floor.all_weapon), floor.how_many['оружие'])


if __name__ == '__main__':
    unittest.main()
