import unittest
import os
from typing import Tuple, Optional
from src.functions.functions import split_actions, roll, readfile, randomitem, howmany, normal_count

class TestSplitActions(unittest.TestCase):

    def test_split_with_action_and_target(self):
        message = "run marathon"
        expected_result = ("run", "marathon")
        result = split_actions(message)
        self.assertEqual(result, expected_result)

    def test_split_with_only_action(self):
        message = "jump"
        expected_result = ("jump", None)
        result = split_actions(message)
        self.assertEqual(result, expected_result)

    def test_split_with_empty_message(self):
        message = ""
        expected_result = ("", None)
        result = split_actions(message)
        self.assertEqual(result, expected_result)

    def test_split_with_multiple_spaces(self):
        message = "  dance  party  "
        expected_result = ("dance", " party")
        result = split_actions(message.strip())
        self.assertEqual(result, expected_result)

    def test_split_with_special_characters(self):
        message = "play @game!"
        expected_result = ("play", "@game!")
        result = split_actions(message)
        self.assertEqual(result, expected_result)

class TestRollFunction(unittest.TestCase):

    def test_single_die(self):
        dice = [6]
        result = roll(dice)
        self.assertTrue(1 <= result <= 6)

    def test_multiple_dice(self):
        dice = [6, 8, 10]
        result = roll(dice)
        self.assertTrue(3 <= result <= 24)

    def test_empty_list(self):
        dice = []
        result = roll(dice)
        self.assertEqual(result, 0)

    def test_zero_sided_die(self):
        dice = [0, 6]
        result = roll(dice)
        self.assertTrue(1 <= result <= 6)

    def test_negative_sided_die(self):
        dice = [-4, 6]
        result = roll(dice)
        self.assertTrue(1 <= result <= 6)
        
class TestReadFileFunction(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for testing
        self.test_filename = 'test_file.txt'
        with open(self.test_filename, 'w', encoding='utf-8') as f:
            f.write("line1|part1\n")
            f.write("line2|part2\n")
            f.write("line3|part3\n")

    def tearDown(self):
        # Remove the temporary file after tests
        os.remove(self.test_filename)

    def test_readfile_with_divide(self):
        expected_result = [['line1', 'part1'], ['line2', 'part2'], ['line3', 'part3']]
        result = readfile(self.test_filename, divide=True)
        self.assertEqual(result, expected_result)

    def test_readfile_without_divide(self):
        expected_result = ['line1|part1', 'line2|part2', 'line3|part3']
        result = readfile(self.test_filename, divide=False)
        self.assertEqual(result, expected_result)

    def test_readfile_with_custom_divider(self):
        with open(self.test_filename, 'w', encoding='utf-8') as f:
            f.write("line1,part1\n")
            f.write("line2,part2\n")
            f.write("line3,part3\n")
        
        expected_result = [['line1', 'part1'], ['line2', 'part2'], ['line3', 'part3']]
        result = readfile(self.test_filename, divide=True, divider=',')
        self.assertEqual(result, expected_result)
        
class TestRandomItemFunction(unittest.TestCase):

    def test_single_item_no_index(self):
        items_list = [1, 2, 3, 4, 5]
        result = randomitem(items_list)
        self.assertIn(result, items_list)

    def test_single_item_with_index(self):
        items_list = ['a', 'b', 'c', 'd']
        item, index = randomitem(items_list, need_number=True)
        self.assertIn(item, items_list)
        self.assertEqual(item, items_list[index])

    def test_multiple_items(self):
        items_list = [10, 20, 30, 40, 50]
        how_many = 3
        result = randomitem(items_list, how_many=how_many)
        self.assertEqual(len(result), how_many)
        for item in result:
            self.assertIn(item, items_list)

    def test_empty_list(self):
        items_list = []
        with self.assertRaises(ValueError):
            randomitem(items_list)

    def test_more_items_than_list_length(self):
        items_list = [1, 2, 3]
        with self.assertRaises(ValueError):
            randomitem(items_list, how_many=5)

    def test_invalid_input_type(self):
        items_list = "not a list or tuple"
        with self.assertRaises(TypeError):
            randomitem(items_list)
            
class TestHowManyFunction(unittest.TestCase):
    def test_singular(self):
        self.assertEqual(howmany(1, ['яблоко', 'яблока', 'яблок']), '1 яблоко')
        self.assertEqual(howmany(21, ['яблоко', 'яблока', 'яблок']), '21 яблоко')
        self.assertEqual(howmany(101, ['яблоко', 'яблока', 'яблок']), '101 яблоко')

    def test_few(self):
        self.assertEqual(howmany(2, ['яблоко', 'яблока', 'яблок']), '2 яблока')
        self.assertEqual(howmany(4, ['яблоко', 'яблока', 'яблок']), '4 яблока')
        self.assertEqual(howmany(22, ['яблоко', 'яблока', 'яблок']), '22 яблока')
        self.assertEqual(howmany(104, ['яблоко', 'яблока', 'яблок']), '104 яблока')

    def test_many(self):
        self.assertEqual(howmany(5, ['яблоко', 'яблока', 'яблок']), '5 яблок')
        self.assertEqual(howmany(11, ['яблоко', 'яблока', 'яблок']), '11 яблок')
        self.assertEqual(howmany(14, ['яблоко', 'яблока', 'яблок']), '14 яблок')
        self.assertEqual(howmany(25, ['яблоко', 'яблока', 'яблок']), '25 яблок')
        self.assertEqual(howmany(111, ['яблоко', 'яблока', 'яблок']), '111 яблок')

class TestNormalCountFunction(unittest.TestCase):
    def test_basic_transformation(self):
        self.assertEqual(normal_count('один два три'), 'один, два и три')
        self.assertEqual(normal_count('яблоко груша банан'), 'яблоко, груша и банан')

    def test_with_exclude(self):
        self.assertEqual(normal_count('один два три (четыре) пять (шесть)', exclude='('), 'один, два, три (четыре) и пять (шесть)')
        self.assertEqual(normal_count('яблоко груша (банан)', exclude='('), 'яблоко и груша (банан)')

    def test_custom_divider(self):
        self.assertEqual(normal_count('один-два-три', divider='-'), 'один, два и три')
        self.assertEqual(normal_count('яблоко-груша-банан', divider='-'), 'яблоко, груша и банан')

    def test_no_transformation_needed(self):
        self.assertEqual(normal_count('один'), 'один')
        self.assertEqual(normal_count('яблоко'), 'яблоко')

if __name__ == '__main__':
    unittest.main()