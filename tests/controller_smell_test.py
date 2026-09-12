import contextlib
import io
import unittest
from unittest.mock import MagicMock

from src.controllers.controller_smell import SmellController


def make_controller():
    return SmellController(game=MagicMock())


def make_room(*neighbors):
    room = MagicMock()
    room.get_rooms_around.return_value = list(neighbors)
    return room


def make_chain():
    """Строит цепочку комнат A -> B -> C, где A связана с B, а B - с C."""
    a = make_room()
    b = make_room(a)
    c = make_room(b)
    a.get_rooms_around.return_value = [b]
    b.get_rooms_around.return_value = [a, c]
    c.get_rooms_around.return_value = [b]
    return a, b, c


class TestSmellControllerInit(unittest.TestCase):
    def test_stores_game(self):
        game = MagicMock()
        controller = SmellController(game)
        self.assertIs(controller.game, game)

    def test_no_smells_at_start(self):
        self.assertEqual(make_controller().smells, [])


class TestCreateSmellSource(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.room = make_room()

    def test_creates_source(self):
        self.controller.create_smell_source(
            room=self.room, source='зомби', intensity=3, smell_type='monster')
        self.assertEqual(len(self.controller.smells), 1)
        source = self.controller.smells[0]
        self.assertEqual(source.source, 'зомби')
        self.assertEqual(source.smell_type, 'monster')
        self.assertIs(source.rooms[self.room]['source_room'], None)

    def test_unknown_smell_type_raises(self):
        with self.assertRaises(ValueError):
            self.controller.create_smell_source(
                room=self.room, source='x', intensity=1, smell_type='garbage')


class TestSpreadSmell(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.a, self.b, self.c = make_chain()

    def test_spreads_with_decreasing_intensity(self):
        rooms = self.controller.distribute_smell(self.a, 3)
        self.assertEqual(rooms[self.a]['intensity'], 3)
        self.assertEqual(rooms[self.b]['intensity'], 2)
        self.assertEqual(rooms[self.c]['intensity'], 1)

    def test_tracks_source_room(self):
        rooms = self.controller.distribute_smell(self.a, 2)
        self.assertIsNone(rooms[self.a]['source_room'])
        self.assertIs(rooms[self.b]['source_room'], self.a)

    def test_no_spread_from_intensity_one(self):
        rooms = self.controller.distribute_smell(self.a, 1)
        self.assertEqual(set(rooms.keys()), {self.a})

    def test_keeps_maximum_intensity(self):
        rooms = self.controller.distribute_smell(self.a, 3)
        self.controller.add_room(rooms, self.a, 1, None)
        self.assertEqual(rooms[self.a]['intensity'], 3)


class TestDecreaseIntensity(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.a, self.b, self.c = make_chain()
        self.source = SmellController.Source(
            source='x',
            smell_type='dead',
            rooms=self.controller.distribute_smell(self.a, 3)
        )

    def test_decreases_intensity(self):
        self.controller.decrease_intensity(self.source, 1)
        self.assertEqual(self.source.rooms[self.a]['intensity'], 2)
        self.assertEqual(self.source.rooms[self.b]['intensity'], 1)

    def test_removes_rooms_below_one(self):
        self.controller.decrease_intensity(self.source, 2)
        self.assertEqual(self.source.rooms[self.a]['intensity'], 1)
        self.assertNotIn(self.b, self.source.rooms)
        self.assertNotIn(self.c, self.source.rooms)

    def test_non_int_delta_raises(self):
        with self.assertRaises(TypeError):
            self.controller.decrease_intensity(self.source, 'a')


class TestIncreaseIntensity(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.a, self.b, self.c = make_chain()
        self.source = SmellController.Source(
            source='x',
            smell_type='monster',
            rooms=self.controller.distribute_smell(self.a, 2)
        )

    def test_increases_intensity(self):
        self.controller.increase_intensity(self.source, 1)
        self.assertEqual(self.source.rooms[self.a]['intensity'], 3)
        self.assertEqual(self.source.rooms[self.b]['intensity'], 2)

    def test_spreads_to_new_rooms(self):
        self.controller.increase_intensity(self.source, 1)
        self.assertEqual(self.source.rooms[self.c]['intensity'], 1)

    def test_non_int_delta_raises(self):
        with self.assertRaises(TypeError):
            self.controller.increase_intensity(self.source, 'a')


class TestSmellQueries(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.room = make_room()

    def test_get_smell_by_smell_type_zero_without_smell(self):
        self.assertEqual(
            self.controller.get_smell_by_smell_type(self.room, 'monster'), 0)

    def test_get_smell_by_smell_type_max_among_sources(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=2, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=1, smell_type='monster')
        self.assertEqual(
            self.controller.get_smell_by_smell_type(self.room, 'monster'), 2)

    def test_get_smell_by_smell_type_ignores_other_types(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='dead')
        self.assertEqual(
            self.controller.get_smell_by_smell_type(self.room, 'monster'), 0)
        self.assertEqual(
            self.controller.get_smell_by_smell_type(self.room, 'dead'), 3)

    def test_get_max_smells_empty(self):
        self.assertEqual(self.controller.get_max_smells(self.room), {})

    def test_get_max_smells_by_type(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=2, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=4, smell_type='dead')
        self.assertEqual(
            self.controller.get_max_smells(self.room), {'monster': 2, 'dead': 4})

    def test_get_max_smell_objects_by_smell_type_empty(self):
        self.assertEqual(
            self.controller.get_max_smell_objects_by_smell_type(
                self.room, 'monster'), [])

    def test_get_max_smell_objects_returns_all_with_equal_max(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=3, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='c', intensity=1, smell_type='monster')
        result = self.controller.get_max_smell_objects_by_smell_type(
            self.room, 'monster')
        self.assertEqual({s.source for s in result}, {'a', 'b'})

    def test_get_max_smell_objects_returns_single_max(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=1, smell_type='monster')
        result = self.controller.get_max_smell_objects_by_smell_type(
            self.room, 'monster')
        self.assertEqual([s.source for s in result], ['a'])


class TestGetSmellText(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.room = make_room()

    def test_none_without_smell(self):
        self.assertIsNone(self.controller.get_smell_text(self.room))

    def test_level_1(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=1, smell_type='monster')
        self.assertIn('Немного пахнет каким-то существом',
                      self.controller.get_smell_text(self.room))

    def test_level_2(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=2, smell_type='monster')
        self.assertIn('Сильно пахнет звериным потом',
                      self.controller.get_smell_text(self.room))

    def test_level_3(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='monster')
        self.assertIn('Невыносимо воняет зверем',
                      self.controller.get_smell_text(self.room))

    def test_level_4(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=4, smell_type='monster')
        self.assertIn('Страшно воняет чем-то нечеловеческим',
                      self.controller.get_smell_text(self.room))

    def test_intensity_clamped_to_level_4(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=100, smell_type='monster')
        self.assertIn('Страшно воняет',
                      self.controller.get_smell_text(self.room))

    def test_dead_type_suffix(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=2, smell_type='dead')
        self.assertIn('тухлой плотью', self.controller.get_smell_text(self.room))

    def test_groups_suffixes_of_same_level(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=3, smell_type='dead')
        self.assertIn('зверем и мертвечиной',
                      self.controller.get_smell_text(self.room))

    def test_levels_sorted_descending(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=1, smell_type='dead')
        text = self.controller.get_smell_text(self.room)
        self.assertLess(text.find('невыносимо'), text.find('немного'))

    def test_key_hole_prefix(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=1, smell_type='monster')
        text = self.controller.get_smell_text(self.room, key_hole=True)
        self.assertIn('Из замочной скважины', text)


class TestCompareSmellIntensity(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.room = make_room()

    def test_false_without_smell(self):
        self.assertFalse(self.controller.compare_smell_intensity(self.room))

    def test_false_when_equal_to_threshold(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=2, smell_type='monster')
        self.assertFalse(
            self.controller.compare_smell_intensity(self.room, intensity=2))

    def test_true_above_threshold(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=3, smell_type='monster')
        self.assertTrue(
            self.controller.compare_smell_intensity(self.room, intensity=2))

    def test_true_with_any_smell_by_default(self):
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=1, smell_type='dead')
        self.assertTrue(self.controller.compare_smell_intensity(self.room))


class TestDeleteSmell(unittest.TestCase):
    def setUp(self):
        self.controller = make_controller()
        self.room = make_room()
        self.controller.create_smell_source(
            room=self.room, source='a', intensity=1, smell_type='monster')
        self.controller.create_smell_source(
            room=self.room, source='b', intensity=1, smell_type='dead')
        self.controller.create_smell_source(
            room=self.room, source='c', intensity=1, smell_type='monster')

    def test_delete_smell_removes_one(self):
        target = self.controller.smells[0]
        self.controller.delete_smell(target)
        self.assertNotIn(target, self.controller.smells)
        self.assertEqual(len(self.controller.smells), 2)

    def test_delete_smell_removes_only_target(self):
        target = self.controller.smells[1]
        other = self.controller.smells[2]
        self.controller.delete_smell(target)
        self.assertIn(other, self.controller.smells)

    def test_delete_smell_by_source_removes_all_matching(self):
        self.controller.delete_smell_by_source('a')
        self.assertEqual(len(self.controller.smells), 2)
        self.assertTrue(all(s.source != 'a' for s in self.controller.smells))

    def test_delete_smell_by_source_missing_is_noop(self):
        self.controller.delete_smell_by_source('absent')
        self.assertEqual(len(self.controller.smells), 3)


if __name__ == '__main__':
    unittest.main()