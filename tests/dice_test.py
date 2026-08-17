import unittest
from unittest.mock import patch
from src.class_dice import Dice


class TestInit(unittest.TestCase):
    def test_creates_dice(self):
        d = Dice([6])
        self.assertEqual(d.dice, [6])
        self.assertEqual(d.modifier, 0)
        self.assertEqual(d.dice_type, '')
        self.assertEqual(d.temporary, [])
        self.assertEqual(d.monster_class_modifiers, {})

    def test_creates_with_modifier(self):
        d = Dice([8], modifier=3)
        self.assertEqual(d.modifier, 3)

    def test_creates_with_dice_type(self):
        d = Dice([6], dice_type='weapon')
        self.assertEqual(d.dice_type, 'weapon')

    def test_stores_initial_values(self):
        d = Dice([6, 8], modifier=2)
        self.assertEqual(d.initial_dice, [6, 8])
        self.assertEqual(d.initial_modifier, 2)

    def test_initial_dice_is_stored(self):
        d = Dice([6])
        self.assertEqual(d.initial_dice, [6])

    def test_initial_modifier_is_stored(self):
        d = Dice([6], modifier=5)
        self.assertEqual(d.initial_modifier, 5)


class TestBaseDie(unittest.TestCase):
    def test_returns_first_die(self):
        self.assertEqual(Dice([6]).base_die(), 6)
        self.assertEqual(Dice([8, 6]).base_die(), 8)

    def test_returns_zero_when_empty(self):
        self.assertEqual(Dice([]).base_die(), 0)


class TestComparisonValue(unittest.TestCase):
    def test_returns_base_die_plus_modifier(self):
        d = Dice([6], modifier=2)
        self.assertEqual(d._comparison_value(), 8)

    def test_returns_base_die_when_no_modifier(self):
        d = Dice([10])
        self.assertEqual(d._comparison_value(), 10)


class TestCheckComparable(unittest.TestCase):
    def test_raises_on_non_dice(self):
        d = Dice([6])
        with self.assertRaises(TypeError):
            d._check_comparable(42)
        with self.assertRaises(TypeError):
            d._check_comparable("dice")
        with self.assertRaises(TypeError):
            d._check_comparable(None)

    def test_does_not_raise_on_dice(self):
        d = Dice([6])
        d._check_comparable(Dice([8]))


class TestEq(unittest.TestCase):
    def test_equal(self):
        self.assertTrue(Dice([6], modifier=2).__eq__(Dice([6], modifier=2)))

    def test_not_equal(self):
        self.assertFalse(Dice([6], modifier=2).__eq__(Dice([8], modifier=2)))

    def test_equal_different_base_same_value(self):
        self.assertTrue(Dice([6], modifier=4).__eq__(Dice([8], modifier=2)))

    def test_raises_on_non_dice(self):
        with self.assertRaises(TypeError):
            Dice([6]).__eq__(42)


class TestNe(unittest.TestCase):
    def test_not_equal(self):
        self.assertTrue(Dice([6]).__ne__(Dice([8])))

    def test_equal(self):
        self.assertFalse(Dice([6]).__ne__(Dice([6])))


class TestLt(unittest.TestCase):
    def test_less_than(self):
        self.assertTrue(Dice([6]).__lt__(Dice([8])))

    def test_not_less_than(self):
        self.assertFalse(Dice([8]).__lt__(Dice([6])))

    def test_not_less_than_equal(self):
        self.assertFalse(Dice([6]).__lt__(Dice([6])))


class TestGt(unittest.TestCase):
    def test_greater_than(self):
        self.assertTrue(Dice([8]).__gt__(Dice([6])))

    def test_not_greater_than(self):
        self.assertFalse(Dice([6]).__gt__(Dice([8])))

    def test_not_greater_than_equal(self):
        self.assertFalse(Dice([6]).__gt__(Dice([6])))


class TestAddTemporary(unittest.TestCase):
    def test_adds_temporary(self):
        d = Dice([6])
        d.add_temporary(4)
        self.assertEqual(d.temporary, [4])
        d.add_temporary(2)
        self.assertEqual(d.temporary, [4, 2])

    def test_raises_on_zero(self):
        with self.assertRaises(ValueError):
            Dice([6]).add_temporary(0)

    def test_raises_on_negative(self):
        with self.assertRaises(ValueError):
            Dice([6]).add_temporary(-1)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).add_temporary("d4")


class TestResetTemporary(unittest.TestCase):
    def test_clears_temporary(self):
        d = Dice([6])
        d.add_temporary(4)
        d.add_temporary(2)
        d.reset_temporary()
        self.assertEqual(d.temporary, [])


class TestRoll(unittest.TestCase):
    @patch('src.class_dice.randint', return_value=4)
    def test_basic_roll(self, mock_randint):
        d = Dice([6])
        result = d.roll()
        mock_randint.assert_called_with(1, 6)
        self.assertEqual(result, 4)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_with_modifier(self, mock_randint):
        d = Dice([6], modifier=2)
        self.assertEqual(d.roll(), 6)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_multiple_dice(self, mock_randint):
        d = Dice([6, 8])
        result = d.roll()
        self.assertEqual(result, 8)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_with_add(self, mock_randint):
        d = Dice([6])
        result = d.roll(add=[10])
        self.assertEqual(result, 8)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_with_subtract(self, mock_randint):
        d = Dice([6])
        result = d.roll(subtract=[2])
        self.assertEqual(result, 0)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_with_multiplier(self, mock_randint):
        d = Dice([6])
        result = d.roll(multiplier=2)
        self.assertEqual(result, 8)
        self.assertEqual(mock_randint.call_count, 2)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_with_temporary(self, mock_randint):
        d = Dice([6])
        d.add_temporary(8)
        result = d.roll()
        self.assertEqual(result, 8)
        self.assertEqual(mock_randint.call_count, 2)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_with_monster(self, mock_randint):
        d = Dice([6])
        d.monster_class_modifiers = {'Goblin': 3}
        monster = type('Goblin', (), {})()
        result = d.roll(monster=monster)
        self.assertEqual(result, 7)

    @patch('src.class_dice.randint', return_value=4)
    def test_roll_clamps_to_zero(self, mock_randint):
        d = Dice([6], modifier=-100)
        self.assertEqual(d.roll(), 0)

    def test_roll_raises_on_add_not_list(self):
        with self.assertRaises(ValueError):
            Dice([6]).roll(add=42)

    def test_roll_raises_on_subtract_not_list(self):
        with self.assertRaises(ValueError):
            Dice([6]).roll(subtract=42)

    @patch('src.class_dice.randint', return_value=1)
    def test_roll_default_args_are_none(self, mock_randint):
        d1 = Dice([6])
        d1.roll()
        d2 = Dice([6])
        result = d2.roll()
        self.assertEqual(d1.roll(), result)


class TestGetMonsterModifier(unittest.TestCase):
    def test_returns_modifier(self):
        d = Dice([6])
        d.monster_class_modifiers = {'Goblin': 5}
        monster = type('Goblin', (), {})()
        self.assertEqual(d.get_monster_modifier(monster), 5)

    def test_returns_zero_when_not_found(self):
        d = Dice([6])
        monster = type('Orc', (), {})()
        self.assertEqual(d.get_monster_modifier(monster), 0)


class TestRollSet(unittest.TestCase):
    @patch('src.class_dice.randint', return_value=4)
    def test_rolls_set(self, mock_randint):
        d = Dice([6])
        result = d.roll_set([6, 8])
        self.assertEqual(result, 8)

    @patch('src.class_dice.randint', return_value=4)
    def test_skips_empty_list(self, mock_randint):
        d = Dice([6])
        self.assertEqual(d.roll_set([]), 0)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).roll_set(["d6"])

    def test_skips_zero(self):
        d = Dice([6])
        with patch('src.class_dice.randint', return_value=4):
            result = d.roll_set([0, 6])
            self.assertEqual(result, 4)

    def test_raises_on_negative(self):
        with self.assertRaises(ValueError):
            Dice([6]).roll_set([-1])


class TestAddDie(unittest.TestCase):
    def test_adds_die(self):
        d = Dice([6])
        d.add_die(8)
        self.assertEqual(d.dice, [6, 8])

    def test_raises_on_zero(self):
        with self.assertRaises(ValueError):
            Dice([6]).add_die(0)

    def test_raises_on_negative(self):
        with self.assertRaises(ValueError):
            Dice([6]).add_die(-1)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).add_die("d8")


class TestRemoveDie(unittest.TestCase):
    def test_removes_die(self):
        d = Dice([6, 8])
        d.remove_die(8)
        self.assertEqual(d.dice, [6])

    def test_raises_when_not_found(self):
        d = Dice([6])
        with self.assertRaises(KeyError):
            d.remove_die(8)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).remove_die("d6")


class TestText(unittest.TestCase):
    def test_single_die(self):
        self.assertEqual(Dice([6]).text(), "d6")

    def test_multiple_dice(self):
        self.assertEqual(Dice([6, 8]).text(), "d6 + d8")

    def test_with_positive_modifier(self):
        self.assertEqual(Dice([6], modifier=3).text(), "d6 + 3")

    def test_with_negative_modifier(self):
        self.assertEqual(Dice([6], modifier=-2).text(), "d6 - 2")

    def test_with_temporary(self):
        d = Dice([6])
        d.add_temporary(4)
        self.assertEqual(d.text(), "d6 + d4")

    def test_empty(self):
        self.assertEqual(Dice([]).text(), "Нет кубиков")

    def test_str_calls_text(self):
        d = Dice([6], modifier=2)
        self.assertEqual(str(d), d.text())


class TestIncreaseModifier(unittest.TestCase):
    def test_increases(self):
        d = Dice([6], modifier=2)
        result = d.increase_modifier(3)
        self.assertEqual(d.modifier, 5)
        self.assertEqual(result, 5)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).increase_modifier("3")


class TestDecreaseModifier(unittest.TestCase):
    def test_decreases(self):
        d = Dice([6], modifier=5)
        result = d.decrease_modifier(2)
        self.assertEqual(d.modifier, 3)
        self.assertEqual(result, 3)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).decrease_modifier("2")


class TestSetDice(unittest.TestCase):
    def test_sets_dice(self):
        d = Dice([6])
        d.set_dice([8, 10])
        self.assertEqual(d.dice, [8, 10])


class TestSetModifier(unittest.TestCase):
    def test_sets_modifier(self):
        d = Dice([6], modifier=2)
        d.set_modifier(5)
        self.assertEqual(d.modifier, 5)


class TestCopy(unittest.TestCase):
    def test_creates_independent_copy(self):
        d = Dice([6, 8], modifier=2, dice_type='weapon')
        c = d.copy()
        self.assertEqual(c.dice, [6, 8])
        self.assertEqual(c.modifier, 2)
        self.assertEqual(c.dice_type, 'weapon')
        c.dice.append(10)
        self.assertEqual(d.dice, [6, 8])

    def test_copy_shares_initial_state(self):
        d = Dice([6], modifier=2)
        c = d.copy()
        self.assertEqual(c.initial_dice, [6])
        self.assertEqual(c.initial_modifier, 2)


class TestReset(unittest.TestCase):
    def test_resets_to_initial(self):
        d = Dice([6, 8], modifier=2)
        d.dice.append(10)
        d.modifier = 5
        d.reset()
        self.assertEqual(d.dice, [6, 8])
        self.assertEqual(d.modifier, 2)


class TestIncreaseBaseDie(unittest.TestCase):
    def test_increases(self):
        d = Dice([6])
        result = d.increase_base_die(2)
        self.assertEqual(d.dice[0], 8)
        self.assertEqual(result, 8)

    def test_default_value(self):
        d = Dice([6])
        d.increase_base_die()
        self.assertEqual(d.dice[0], 7)

    def test_raises_on_non_int(self):
        with self.assertRaises(ValueError):
            Dice([6]).increase_base_die("2")

    def test_raises_on_negative(self):
        with self.assertRaises(ValueError):
            Dice([6]).increase_base_die(-1)

    def test_zero_is_valid(self):
        d = Dice([6])
        result = d.increase_base_die(0)
        self.assertEqual(result, 6)


if __name__ == '__main__':
    unittest.main()
