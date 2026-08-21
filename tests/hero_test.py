import unittest
from unittest.mock import MagicMock, patch

from src.class_hero import Hero
from src.class_game import Game
from src.class_dice import Dice
from src.enums import state_enum, move_enum


Game.__del__ = lambda self: None


def make_hero():
    game = Game(chat_id='test', bot=MagicMock())
    hero = game.player
    return hero


class TestGetNamesList(unittest.TestCase):
    def test_none_cases_does_not_crash(self):
        hero = make_hero()
        result = hero.get_names_list(cases=None)
        self.assertIn('героя', result)
        self.assertIn('героиню', result)

    def test_with_cases(self):
        hero = make_hero()
        result = hero.get_names_list(cases=['nom', 'gen'])
        self.assertIn(hero.lexemes['nom'].lower(), result)

    def test_empty_cases_list(self):
        hero = make_hero()
        result = hero.get_names_list(cases=[])
        self.assertIn('себя', result)


class TestCheckIfCanRead(unittest.TestCase):
    def test_cannot_read_when_fearful(self):
        hero = make_hero()
        hero.fear = 10
        hero.current_position.light = True
        can_read, msg = hero.check_if_can_read()
        self.assertFalse(can_read)
        self.assertIn('страха', msg)

    def test_cannot_read_in_darkness(self):
        hero = make_hero()
        hero.fear = 0
        hero.current_position.light = False
        can_read, msg = hero.check_if_can_read()
        self.assertFalse(can_read)
        self.assertIn('темноте', msg)

    def test_can_read_when_no_fear_and_light(self):
        hero = make_hero()
        hero.fear = 0
        hero.current_position.light = True
        can_read, msg = hero.check_if_can_read()
        self.assertTrue(can_read)


class TestCheckIfCanExamine(unittest.TestCase):
    def test_cannot_examine_when_fearful(self):
        hero = make_hero()
        hero.fear = 10
        hero.current_position.light = True
        can_examine, msg = hero.check_if_can_examine()
        self.assertFalse(can_examine)
        self.assertIn('страха', msg)

    def test_cannot_examine_in_darkness(self):
        hero = make_hero()
        hero.fear = 0
        with patch.object(hero, 'check_light', return_value=False):
            can_examine, msg = hero.check_if_can_examine()
        self.assertFalse(can_examine)
        self.assertTrue(len(msg) > 0)

    def test_can_examine_when_no_fear_and_light(self):
        hero = make_hero()
        hero.fear = 0
        hero.current_position.light = True
        can_examine, msg = hero.check_if_can_examine()
        self.assertTrue(can_examine)


class TestLoseWeaponOrShield(unittest.TestCase):
    def test_lose_weapon_message_refers_to_real_weapon(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.__format__ = lambda self, fmt: 'железный меч'
        hero.weapon = weapon
        target = MagicMock()
        target.weapon = MagicMock()
        target.weapon.empty = True
        target.carryweapon = True
        with patch('src.class_hero.randint', return_value=1):
            msg = hero.lose_weapon_or_shield(target)
        self.assertIn('железный меч', msg)
        self.assertTrue(hero.weapon.empty)

    def test_lose_shield_message_refers_to_real_shield(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.__format__ = lambda self, fmt: 'деревянный щит'
        hero.shield = shield
        target = MagicMock()
        target.shield = MagicMock()
        target.shield.empty = True
        target.carryshield = True
        with patch('src.class_hero.randint', return_value=2):
            msg = hero.lose_weapon_or_shield(target)
        self.assertIn('деревянный щит', msg)
        self.assertTrue(hero.shield.empty)


class TestDextWound(unittest.TestCase):
    def test_wound_key_is_dext(self):
        hero = make_hero()
        hero.dext_wound()
        self.assertEqual(hero.wounds.get('dext', 0), 1)

    def test_multiple_wounds_stack(self):
        hero = make_hero()
        hero.dext_wound()
        hero.dext_wound()
        self.assertEqual(hero.wounds['dext'], 2)


class TestDisarm(unittest.TestCase):
    def test_unknown_input_returns_false(self):
        hero = make_hero()
        result = hero.disarm('непонятное')
        self.assertFalse(result)

    def test_default_param_is_empty_string(self):
        hero = make_hero()
        result = hero.disarm()
        self.assertIsInstance(result, bool)

    def test_trap_string_returns_bool(self):
        hero = make_hero()
        result = hero.disarm('ловушку')
        self.assertIsInstance(result, bool)


class TestDisarmTrap(unittest.TestCase):
    def test_no_trap_returns_false(self):
        hero = make_hero()
        with patch.object(hero.current_position, 'get_trap', return_value=None):
            self.assertFalse(hero.disarm_trap())

    def test_with_trap_returns_true(self):
        hero = make_hero()
        trap = MagicMock()
        trap.where = MagicMock()
        trap.where.__format__ = lambda self, fmt: 'дверь'
        trap.get_difficulty.return_value = 0
        trap.disarm.return_value = ['Ловушка обезврежена.']
        with patch.object(hero.current_position, 'get_trap', return_value=trap):
            with patch.object(hero, 'check_dext', return_value=100):
                result = hero.disarm_trap()
        self.assertTrue(result)


class TestAttack(unittest.TestCase):
    def test_valid_action_returns_true(self):
        hero = make_hero()
        target = MagicMock()
        target.poisoned = False
        with patch.object(hero, 'hit_enemy'):
            result = hero.attack(target, '')
        self.assertTrue(result)

    def test_unknown_action_returns_false(self):
        hero = make_hero()
        target = MagicMock()
        result = hero.attack(target, 'несуществующее')
        self.assertFalse(result)

    def test_shield_action_returns_true(self):
        hero = make_hero()
        target = MagicMock()
        with patch.object(hero, 'use_shield'):
            result = hero.attack(target, 'з')
        self.assertTrue(result)

    def test_run_action_returns_true(self):
        hero = make_hero()
        target = MagicMock()
        with patch.object(hero, 'run_away', return_value=True):
            result = hero.attack(target, 'б')
        self.assertTrue(result)


class TestIncreaseStats(unittest.TestCase):
    def test_increase_strength_returns_true(self):
        hero = make_hero()
        result = hero.increase_strength(1)
        self.assertTrue(result)

    def test_increase_dexterity_returns_true(self):
        hero = make_hero()
        result = hero.increase_dexterity(1)
        self.assertTrue(result)

    def test_increase_intelligence_returns_true(self):
        hero = make_hero()
        result = hero.increase_intelligence(1)
        self.assertTrue(result)


class TestEnchant(unittest.TestCase):
    def test_returns_true(self):
        hero = make_hero()
        result = hero.enchant('')
        self.assertTrue(result)

    def test_creates_process(self):
        hero = make_hero()
        with patch.object(hero.game.processes_controller, 'create_process') as mock:
            hero.enchant('меч')
            mock.assert_called_once_with(
                owner=hero,
                type='enchantment',
                request_text='меч'
            )


class TestRunAway(unittest.TestCase):
    def test_returns_bool_on_success(self):
        hero = make_hero()
        target = MagicMock()
        target.frightening = False
        hero.weapon = hero.game.no_weapon
        hero.shield = hero.game.no_shield
        with patch('src.class_hero.randomitem', return_value=0):
            result = hero.run_away(target)
        self.assertIsInstance(result, bool)

    def test_returns_false_on_wall_collision_in_dark(self):
        hero = make_hero()
        target = MagicMock()
        target.frightening = False
        hero.weapon = hero.game.no_weapon
        hero.shield = hero.game.no_shield
        hero.current_position.light = False
        with patch('src.class_hero.randint', return_value=99):
            result = hero.run_away(target)
        self.assertFalse(result)


class TestGetHealthPercentage(unittest.TestCase):
    def test_zero_start_health_returns_zero(self):
        hero = make_hero()
        hero.start_health = 0
        hero.health = 0
        self.assertEqual(hero.get_health_percentage(), 0)

    def test_half_health_returns_50(self):
        hero = make_hero()
        hero.start_health = 100
        hero.health = 50
        self.assertEqual(hero.get_health_percentage(), 50)

    def test_full_health_returns_100(self):
        hero = make_hero()
        hero.start_health = 100
        hero.health = 100
        self.assertEqual(hero.get_health_percentage(), 100)


class TestDarkDamageDividerDie(unittest.TestCase):
    def test_is_dice_object(self):
        self.assertIsInstance(Hero._dark_damage_divider_die, Dice)

    def test_rolls_value(self):
        val = Hero._dark_damage_divider_die.roll()
        self.assertIsInstance(val, int)
        self.assertGreater(val, 0)


class TestGetPoisonProtection(unittest.TestCase):
    def test_empty_shield_does_not_crash(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        hero.armor = hero.game.no_armor
        result = hero.get_poison_protection()
        self.assertIsInstance(result, int)


class TestSelectEnemy(unittest.TestCase):
    def test_returns_none_for_no_match(self):
        hero = make_hero()
        enemy1 = MagicMock()
        enemy1.check_name.return_value = False
        fight = MagicMock()
        fight.get_targets.return_value = [enemy1]
        hero.current_fight = fight
        result = hero.select_enemy('несуществующий')
        self.assertIsNone(result)

    def test_returns_none_for_self_attack(self):
        hero = make_hero()
        fight = MagicMock()
        fight.get_targets.return_value = [hero]
        hero.current_fight = fight
        result = hero.select_enemy('1')
        self.assertIsNone(result)

    def test_returns_none_for_out_of_range_index(self):
        hero = make_hero()
        fight = MagicMock()
        fight.get_targets.return_value = []
        hero.current_fight = fight
        result = hero.select_enemy('99')
        self.assertIsNone(result)


class TestFightActions(unittest.TestCase):
    def test_no_enemy_does_not_crash(self):
        hero = make_hero()
        fight = MagicMock()
        fight.get_targets.return_value = []
        hero.current_fight = fight
        hero.select_enemy = MagicMock(return_value=None)
        result = hero.fight_actions('ударить')
        self.assertTrue(result)


class TestWeaponTypeConsistency(unittest.TestCase):
    def test_generate_weapon_attack_uses_weapon_type(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.type = 'кол'
        weapon.weapon_type = 'кол'
        weapon.attack.return_value = 10
        weapon.element.return_value = 0
        weapon.hit_chance = Dice([1])
        target = MagicMock()
        target.__class__.__name__ = 'Monster'
        hero.weapon = weapon
        hero.mastery['кол'] = {'level': 1, 'max_level': 10, 'counter': 0}
        result = hero.generate_weapon_attack(target)
        self.assertIsInstance(result, int)


if __name__ == '__main__':
    unittest.main()
