import unittest
import os
from unittest.mock import MagicMock, patch
from typing import Tuple, Optional
from src.functions.functions import (
    split_actions, roll, randomitem, randomitem_dict, howmany, normal_count,
    cprint, tprint, pprint, get_fight_markup, get_markup,
    generate_keyboard, get_direction_markup, get_levelup_markup, get_cancel_markup,
)

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


class TestRandomItemDict(unittest.TestCase):

    def test_returns_key_value_pair(self):
        d = {'a': 1, 'b': 2}
        key, val = randomitem_dict(d)
        self.assertIn(key, d)
        self.assertEqual(d[key], val)

    def test_not_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            randomitem_dict([1, 2])

    def test_empty_dict_raises_value_error(self):
        with self.assertRaises(ValueError):
            randomitem_dict({})

    def test_single_item(self):
        key, val = randomitem_dict({'only': 42})
        self.assertEqual(key, 'only')
        self.assertEqual(val, 42)


class TestGenerateKeyboard(unittest.TestCase):
    def test_yields_chunks(self):
        result = list(generate_keyboard([1, 2, 3, 4, 5], 2))
        self.assertEqual(result, [[1, 2], [3, 4], [5]])

    def test_exact_chunk(self):
        result = list(generate_keyboard([1, 2, 3, 4], 2))
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_keys_in_row_larger_than_len(self):
        result = list(generate_keyboard([1, 2], 5))
        self.assertEqual(result, [[1, 2]])


class TestGetFightMarkup(unittest.TestCase):

    def _make_game(self, shield_empty=False, can_use=False, weapon_empty=False, second=None):
        game = MagicMock()
        game.player.shield.empty = shield_empty
        game.player.backpack.get_items_for_fight.return_value = 'x' if can_use else []
        if second is None:
            game.player.get_second_weapon.return_value = False
        else:
            game.player.get_second_weapon.return_value = second
        game.player.weapon.empty = weapon_empty
        return game

    def test_basic_keys(self):
        game = self._make_game(shield_empty=True, can_use=False)
        markup = get_fight_markup(game)
        flat = [k for row in markup.keyboard for k in row]
        self.assertIn('ударить', flat)
        self.assertIn('бежать', flat)

    def test_with_shield(self):
        game = self._make_game(shield_empty=False, can_use=False)
        markup = get_fight_markup(game)
        flat = [k for row in markup.keyboard for k in row]
        self.assertIn('защититься', flat)

    def test_with_use_items(self):
        game = self._make_game(shield_empty=True, can_use=True)
        markup = get_fight_markup(game)
        flat = [k for row in markup.keyboard for k in row]
        self.assertIn('использовать', flat)

    def test_with_switch_weapon(self):
        game = self._make_game(shield_empty=True, can_use=False,
                               weapon_empty=False, second=True)
        markup = get_fight_markup(game)
        flat = [k for row in markup.keyboard for k in row]
        self.assertIn('сменить оружие', flat)

    def test_no_switch_without_second_weapon(self):
        game = self._make_game(shield_empty=True, can_use=False,
                               weapon_empty=False, second=False)
        markup = get_fight_markup(game)
        flat = [k for row in markup.keyboard for k in row]
        self.assertNotIn('сменить оружие', flat)

    def test_no_switch_with_empty_weapon(self):
        game = self._make_game(shield_empty=True, can_use=False,
                               weapon_empty=True, second=True)
        markup = get_fight_markup(game)
        flat = [k for row in markup.keyboard for k in row]
        self.assertNotIn('сменить оружие', flat)


class TestGetMarkup(unittest.TestCase):

    def test_off_state(self):
        markup = get_markup(MagicMock(), 'off')
        self.assertIsNotNone(markup)

    def test_fight_state(self):
        game = MagicMock()
        game.player.shield.empty = True
        game.player.backpack.get_items_for_fight.return_value = []
        game.player.weapon.empty = True
        markup = get_markup(game, 'fight')
        self.assertIsNotNone(markup)

    def test_direction_state(self):
        markup = get_markup(MagicMock(), 'direction')
        self.assertIsNotNone(markup)

    def test_levelup_state(self):
        markup = get_markup(MagicMock(), 'levelup')
        self.assertIsNotNone(markup)

    def test_enchant_state(self):
        markup = get_markup(MagicMock(), 'enchant')
        self.assertIsNotNone(markup)

    def test_use_in_fight_state(self):
        markup = get_markup(MagicMock(), 'use_in_fight')
        self.assertIsNotNone(markup)

    def test_trade_state(self):
        markup = get_markup(MagicMock(), 'trade')
        self.assertIsNotNone(markup)

    def test_read_state(self):
        markup = get_markup(MagicMock(), 'read')
        self.assertIsNotNone(markup)

    def test_unknown_state(self):
        self.assertEqual(get_markup(MagicMock(), 'unknown'), '')


class TestDirectionMarkup(unittest.TestCase):
    def test_direction_markup(self):
        markup = get_direction_markup()
        self.assertIsNotNone(markup)
        self.assertTrue(len(markup.keyboard) >= 1)

    def test_levelup_markup(self):
        markup = get_levelup_markup()
        self.assertIsNotNone(markup)

    def test_cancel_markup(self):
        markup = get_cancel_markup()
        self.assertIsNotNone(markup)


class TestCPrint(unittest.TestCase):

    @patch('builtins.print')
    def test_cprint_empty_returns_false(self, mock_print):
        result = cprint('')
        self.assertFalse(result)
        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_cprint_none_returns_false(self, mock_print):
        result = cprint(None)
        self.assertFalse(result)
        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_cprint_string(self, mock_print):
        result = cprint('hello')
        self.assertIsNone(result)
        mock_print.assert_called_once_with('hello')

    @patch('builtins.print')
    def test_cprint_list(self, mock_print):
        cprint(['line1', 'line2'])
        mock_print.assert_called_once_with('line1\nline2')

    @patch('builtins.print')
    def test_cprint_list_with_empty_lines(self, mock_print):
        cprint(['a', '', 'b'])
        mock_print.assert_called_once_with('a\nb')

    @patch('builtins.print')
    def test_cprint_list_single_line(self, mock_print):
        cprint(['only'])
        mock_print.assert_called_once_with('only')


class TestTPrint(unittest.TestCase):

    def _make_game(self):
        game = MagicMock()
        game.bot = MagicMock()
        game.chat_id = 'chat'
        return game

    @patch('src.functions.functions.get_markup')
    def test_tprint_empty_returns_false(self, mock_get_markup):
        game = self._make_game()
        result = tprint(game, '')
        self.assertFalse(result)
        game.bot.send_message.assert_not_called()

    @patch('src.functions.functions.get_markup')
    def test_tprint_none_returns_false(self, mock_get_markup):
        game = self._make_game()
        result = tprint(game, None)
        self.assertFalse(result)
        game.bot.send_message.assert_not_called()

    @patch('src.functions.functions.get_markup')
    def test_tprint_string(self, mock_get_markup):
        game = self._make_game()
        mock_get_markup.return_value = 'markup'
        tprint(game, 'hello', state='fight')
        game.bot.send_message.assert_called_once_with('chat', 'hello',
                                                      reply_markup='markup')

    @patch('src.functions.functions.get_markup')
    def test_tprint_list(self, mock_get_markup):
        game = self._make_game()
        tprint(game, ['line1', 'line2'])
        game.bot.send_message.assert_called_once_with('chat', 'line1\nline2',
                                                      reply_markup=mock_get_markup.return_value)

    @patch('src.functions.functions.get_markup')
    def test_tprint_list_with_empty_lines(self, mock_get_markup):
        game = self._make_game()
        tprint(game, ['a', '', 'b'])
        game.bot.send_message.assert_called_once_with('chat', 'a\nb',
                                                      reply_markup=mock_get_markup.return_value)


class TestPPrint(unittest.TestCase):

    def _make_game(self):
        game = MagicMock()
        game.bot = MagicMock()
        game.chat_id = 'chat'
        return game

    @patch('src.functions.functions.Image.new')
    @patch('src.functions.functions.ImageDraw.Draw')
    @patch('src.functions.functions.ImageFont.truetype')
    def test_pprint_string(self, mock_font, mock_draw, mock_image):
        game = self._make_game()
        draw = mock_draw.return_value
        pprint(game, 'hello')
        draw.text.assert_called_once()
        game.bot.send_photo.assert_called_once_with('chat', mock_image.return_value)

    @patch('src.functions.functions.Image.new')
    @patch('src.functions.functions.ImageDraw.Draw')
    @patch('src.functions.functions.ImageFont.truetype')
    def test_pprint_list(self, mock_font, mock_draw, mock_image):
        game = self._make_game()
        draw = mock_draw.return_value
        pprint(game, ['a', 'b'])
        draw.text.assert_called_once()
        game.bot.send_photo.assert_called_once_with('chat', mock_image.return_value)

    @patch('src.functions.functions.Image.new')
    @patch('src.functions.functions.ImageDraw.Draw')
    @patch('src.functions.functions.ImageFont.truetype')
    def test_pprint_custom_dimensions(self, mock_font, mock_draw, mock_image):
        game = self._make_game()
        pprint(game, 'x', width=300, height=200, color='#FF0000')
        mock_image.assert_called_once_with('RGB', (300, 200), color='#FF0000')
            
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