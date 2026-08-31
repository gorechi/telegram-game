import unittest
from src.enums import state_enum, move_enum


class TestStateEnum(unittest.TestCase):

    def test_values(self):
        self.assertEqual(state_enum.NO_STATE.value, 0)
        self.assertEqual(state_enum.FIGHT.value, 1)
        self.assertEqual(state_enum.ENCHANT.value, 2)
        self.assertEqual(state_enum.LEVEL_UP.value, 3)
        self.assertEqual(state_enum.USE_IN_FIGHT.value, 4)
        self.assertEqual(state_enum.TRADE.value, 5)
        self.assertEqual(state_enum.DRINK.value, 7)
        self.assertEqual(state_enum.ACTION.value, 8)


class TestMoveEnum(unittest.TestCase):

    def test_static_values(self):
        self.assertEqual(move_enum.UP.index, 0)
        self.assertEqual(move_enum.UP.countermove, 2)
        self.assertEqual(move_enum.RIGHT.index, 1)
        self.assertEqual(move_enum.RIGHT.countermove, 3)
        self.assertEqual(move_enum.DOWN.index, 2)
        self.assertEqual(move_enum.DOWN.countermove, 0)
        self.assertEqual(move_enum.LEFT.index, 3)
        self.assertEqual(move_enum.LEFT.countermove, 1)
        self.assertEqual(move_enum.UPSTAIRS.index, 4)
        self.assertEqual(move_enum.UPSTAIRS.countermove, 5)
        self.assertEqual(move_enum.DOWNSTAIRS.index, 5)
        self.assertEqual(move_enum.DOWNSTAIRS.countermove, 4)
        self.assertEqual(move_enum.START.index, 100)
        self.assertEqual(move_enum.START.countermove, 100)

    def test_get_move_by_number_found(self):
        self.assertIs(move_enum.get_move_by_number(0), move_enum.UP)
        self.assertIs(move_enum.get_move_by_number(1), move_enum.RIGHT)
        self.assertIs(move_enum.get_move_by_number(2), move_enum.DOWN)
        self.assertIs(move_enum.get_move_by_number(3), move_enum.LEFT)
        self.assertIs(move_enum.get_move_by_number(4), move_enum.UPSTAIRS)
        self.assertIs(move_enum.get_move_by_number(5), move_enum.DOWNSTAIRS)
        self.assertIs(move_enum.get_move_by_number(100), move_enum.START)

    def test_get_move_by_number_not_found(self):
        self.assertIsNone(move_enum.get_move_by_number(999))
        self.assertIsNone(move_enum.get_move_by_number(-1))


if __name__ == '__main__':
    unittest.main()
