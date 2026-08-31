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


class TestFightActions(unittest.TestCase):
    def test_no_enemy_does_not_crash(self):
        hero = make_hero()
        fight = MagicMock()
        fight.get_fighter.return_value = None
        hero.current_fight = fight
        result = hero.fight_actions('ударить')
        self.assertTrue(result)
        fight.get_fighter.assert_called_once_with(text=None, for_hero=True)


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


def make_enemy():
    game = Game(chat_id='test_enemy', bot=MagicMock())
    return game.monsters_controller.create_object_by_name('Гоблин')


class TestHeal(unittest.TestCase):
    def test_no_potion_returns_message(self):
        hero = make_hero()
        hero.backpack.get_random_item_by_class = MagicMock(return_value=None)
        result = hero.heal(None, in_action=False)
        self.assertIn('не может', result)

    def test_with_potion(self):
        hero = make_hero()
        potion = MagicMock()
        potion.use.return_value = 'Выздоровел'
        hero.backpack.get_random_item_by_class = MagicMock(return_value=potion)
        result = hero.heal(None, in_action=True)
        self.assertEqual(result, 'Выздоровел')
        potion.use.assert_called_once_with(hero, True)


class TestNameForExamine(unittest.TestCase):
    def test_returns_string(self):
        hero = make_hero()
        result = hero.name_for_examine(None)
        self.assertIsInstance(result, str)
        self.assertIn('Себя', result)


class TestExamine(unittest.TestCase):
    def test_no_light_returns_dark_message(self):
        hero = make_hero()
        with patch.object(hero, 'check_light', return_value=False):
            result = hero.examine(None)
        self.assertIn('неподходящая обстановка', result)

    def test_with_light_returns_show(self):
        hero = make_hero()
        with patch.object(hero, 'check_light', return_value=True):
            result = hero.examine(None)
        self.assertIsInstance(result, list)


class TestGenerateInitiative(unittest.TestCase):
    def test_returns_positive_int(self):
        hero = make_hero()
        result = hero.generate_initiative()
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)


class TestCheckStren(unittest.TestCase):
    def test_returns_int(self):
        hero = make_hero()
        hero.current_position.light = True
        result = hero.check_stren()
        self.assertIsInstance(result, int)

    def test_with_against_returns_bool(self):
        hero = make_hero()
        hero.current_position.light = True
        result = hero.check_stren(against=1)
        self.assertIsInstance(result, bool)

    def test_wounds_reduce_result(self):
        hero = make_hero()
        hero.wounds['stren'] = 100
        with patch.object(hero.stren, 'roll', return_value=-50):
            result = hero.check_stren()
        self.assertLessEqual(result, 0)


class TestCheckDext(unittest.TestCase):
    def test_returns_int(self):
        hero = make_hero()
        result = hero.check_dext()
        self.assertIsInstance(result, int)

    def test_with_against_returns_bool(self):
        hero = make_hero()
        result = hero.check_dext(against=1)
        self.assertIsInstance(result, bool)

    def test_wounds_reduce_result(self):
        hero = make_hero()
        hero.wounds['dext'] = 100
        result = hero.check_dext()
        self.assertLessEqual(result, 0)


class TestCheckIntel(unittest.TestCase):
    def test_returns_int(self):
        hero = make_hero()
        result = hero.check_intel()
        self.assertIsInstance(result, int)

    def test_with_against_returns_bool(self):
        hero = make_hero()
        result = hero.check_intel(against=1)
        self.assertIsInstance(result, bool)


class TestCheckIfSneakPastMonster(unittest.TestCase):
    def test_returns_bool(self):
        hero = make_hero()
        monster = MagicMock()
        monster.size = Dice([1])
        result = hero.check_if_sneak_past_monster(monster)
        self.assertIsInstance(result, bool)


class TestCheckIfSneakPastFurniture(unittest.TestCase):
    def test_returns_bool(self):
        hero = make_hero()
        result = hero.check_if_sneak_past_furniture()
        self.assertIsInstance(result, bool)


class TestPlace(unittest.TestCase):
    def test_sets_current_position(self):
        hero = make_hero()
        room = MagicMock()
        hero.place(room)
        self.assertEqual(hero.current_position, room)
        self.assertTrue(room.visited)
        self.assertEqual(hero.last_move, move_enum.START)


class TestIncreaseMonsterKnowledge(unittest.TestCase):
    def test_known_type(self):
        from src.class_monsters import Monster
        hero = make_hero()
        hero.monster_knowledge = {}
        result = hero.increase_monster_knowledge('undead')
        self.assertEqual(hero.monster_knowledge['undead'], 1)
        self.assertIn(Monster._types['undead']['accus'], result)

    def test_unknown_type(self):
        hero = make_hero()
        hero.monster_knowledge = {}
        result = hero.increase_monster_knowledge('неведомое')
        self.assertIn('неведомого противника', result)


class TestGoDownWithLightOn(unittest.TestCase):
    def test_no_ladder(self):
        hero = make_hero()
        hero.current_position.ladder_down = None
        result = hero.go_down_with_light_on()
        self.assertIn('абсолютно ровный пол', result)

    def test_locked_ladder(self):
        hero = make_hero()
        ladder = MagicMock()
        ladder.locked = True
        hero.current_position.ladder_down = ladder
        result = hero.go_down_with_light_on()
        self.assertIn('заперта', result)

    def test_open_ladder(self):
        hero = make_hero()
        room = MagicMock()
        ladder = MagicMock()
        ladder.locked = False
        ladder.room_down = MagicMock()
        hero.current_position = room
        hero.current_position.ladder_down = ladder
        with patch.object(hero, 'move'):
            result = hero.go_down_with_light_on()


class TestGoDownWithLightOff(unittest.TestCase):
    def test_no_ladder(self):
        hero = make_hero()
        hero.current_position.ladder_down = None
        result = hero.go_down_with_light_off()
        self.assertIn('шарит', result)


class TestGoUpWithLightOn(unittest.TestCase):
    def test_no_ladder(self):
        hero = make_hero()
        hero.current_position.ladder_up = None
        result = hero.go_up_with_light_on()
        self.assertIn('нет такой возможности', result)

    def test_locked_ladder(self):
        hero = make_hero()
        ladder = MagicMock()
        ladder.locked = True
        hero.current_position.ladder_up = ladder
        result = hero.go_up_with_light_on()
        self.assertIn('заперта', result)


class TestGoUpWithLightOff(unittest.TestCase):
    def test_no_ladder(self):
        hero = make_hero()
        hero.current_position.ladder_up = None
        result = hero.go_up_with_light_off()
        self.assertIn('ничего не может разглядеть', result)


class TestDescend(unittest.TestCase):
    def test_moves_to_lower_room(self):
        hero = make_hero()
        room = MagicMock()
        lower = MagicMock()
        room.ladder_down.room_down = lower
        with patch.object(hero, 'move') as mock_move:
            hero.descend(room)
            mock_move.assert_called_once_with(lower)


class TestAscend(unittest.TestCase):
    def test_moves_to_upper_room(self):
        hero = make_hero()
        room = MagicMock()
        upper = MagicMock()
        room.ladder_up.room_up = upper
        with patch.object(hero, 'move') as mock_move:
            hero.ascend(room)
            mock_move.assert_called_once_with(upper)


class TestIntelWound(unittest.TestCase):
    def test_increments_wound(self):
        hero = make_hero()
        hero.intel_wound()
        self.assertEqual(hero.wounds.get('intel', 0), 1)
        hero.intel_wound()
        self.assertEqual(hero.wounds['intel'], 2)


class TestStrenWound(unittest.TestCase):
    def test_increments_wound(self):
        hero = make_hero()
        hero.stren_wound()
        self.assertEqual(hero.wounds.get('stren', 0), 1)


class TestGetWeakness(unittest.TestCase):
    def test_no_weakness_returns_1(self):
        hero = make_hero()
        hero.weakness = {}
        weapon = MagicMock()
        weapon.element.return_value = 1
        self.assertEqual(hero.get_weakness(weapon), 1)

    def test_known_weakness(self):
        hero = make_hero()
        hero.weakness = {'1': 2.0}
        weapon = MagicMock()
        weapon.element.return_value = 1
        self.assertEqual(hero.get_weakness(weapon), 2.0)


class TestGetShield(unittest.TestCase):
    def test_no_shield_returns_none(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        hero.removed_shield = hero.game.no_shield
        self.assertIsNone(hero.get_shield())

    def test_has_shield_returns_it(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        hero.shield = shield
        self.assertEqual(hero.get_shield(), shield)

    def test_removed_shield_returns_it(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        removed = MagicMock()
        removed.empty = False
        hero.removed_shield = removed
        self.assertEqual(hero.get_shield(), removed)


class TestCheckBackpack(unittest.TestCase):
    def test_has_backpack(self):
        hero = make_hero()
        self.assertTrue(hero.check_backpack())


class TestCheckFight(unittest.TestCase):
    def test_no_fight(self):
        hero = make_hero()
        hero.current_fight = None
        self.assertFalse(hero.check_fight())

    def test_in_fight(self):
        hero = make_hero()
        hero.current_fight = MagicMock()
        self.assertTrue(hero.check_fight())


class TestCheckFear(unittest.TestCase):
    def test_not_fearful(self):
        hero = make_hero()
        hero.fear = 0
        self.assertFalse(hero.check_fear())

    def test_fearful(self):
        hero = make_hero()
        hero.fear = 5
        self.assertTrue(hero.check_fear())


class TestDecreaseRestless(unittest.TestCase):
    def test_decreases(self):
        hero = make_hero()
        hero.restless = 5
        hero.decrease_restless(3)
        self.assertEqual(hero.restless, 2)

    def test_not_below_zero(self):
        hero = make_hero()
        hero.restless = 1
        hero.decrease_restless(5)
        self.assertEqual(hero.restless, 1)

    def test_always_returns_true(self):
        hero = make_hero()
        self.assertTrue(hero.decrease_restless(0))


class TestShow(unittest.TestCase):
    def test_show_returns_message(self):
        hero = make_hero()
        msg = hero.show(return_message=True)
        self.assertIsInstance(msg, list)
        self.assertGreater(len(msg), 0)

    def test_show_does_not_crash(self):
        hero = make_hero()
        hero.show()


class TestShowMastery(unittest.TestCase):
    def test_no_mastery_returns_empty(self):
        hero = make_hero()
        for k in hero.mastery:
            if isinstance(hero.mastery[k], dict):
                hero.mastery[k]['level'] = 0
        self.assertEqual(hero.show_mastery(), '')

    def test_with_mastery(self):
        hero = make_hero()
        hero.mastery['колющее']['level'] = 3
        result = hero.show_mastery()
        self.assertIn('колющее', result)


class TestShowMeMoney(unittest.TestCase):
    def test_zero_coins(self):
        hero = make_hero()
        hero.gender = 1
        result = hero.show_me_money()
        self.assertIn('бедна', result)


class TestShowWeapon(unittest.TestCase):
    def test_no_weapon(self):
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        result = hero.show_weapon()
        self.assertIn('голыми руками', result)

    def test_with_weapon(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.get_full_names.return_value = 'Меч'
        weapon.damage.text.return_value = '1d6'
        weapon.__format__ = lambda s, f: 'Меч'
        hero.weapon = weapon
        result = hero.show_weapon()
        self.assertIn('Меч', result)


class TestShowProtection(unittest.TestCase):
    def test_no_protection(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        hero.armor = hero.game.no_armor
        result = hero.show_protection()
        self.assertIn('нет ни щита', result)

    def test_shield_only(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.show.return_value = 'Щит'
        hero.shield = shield
        hero.armor = hero.game.no_armor
        result = hero.show_protection()
        self.assertIn('Щит', result)

    def test_armor_only(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        armor = MagicMock()
        armor.empty = False
        armor.show.return_value = 'Доспех'
        hero.armor = armor
        result = hero.show_protection()
        self.assertIn('Доспех', result)

    def test_both(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.show.return_value = 'Щит'
        armor = MagicMock()
        armor.empty = False
        armor.show.return_value = 'Доспех'
        hero.shield = shield
        hero.armor = armor
        result = hero.show_protection()
        self.assertIn('Щит', result)
        self.assertIn('Доспех', result)


class TestG(unittest.TestCase):
    def test_male(self):
        hero = make_hero()
        hero.gender = 0
        self.assertEqual(hero.g('м', 'ж'), 'м')

    def test_female(self):
        hero = make_hero()
        hero.gender = 1
        self.assertEqual(hero.g('м', 'ж'), 'ж')


class TestShowMeMoneyBranches(unittest.TestCase):
    def test_zero_money(self):
        hero = make_hero()
        hero.money = MagicMock()
        hero.money.__ge__ = lambda s, o: False
        hero.money.__eq__ = lambda s, o: o == 0
        hero.money.how_much_money = 0
        self.assertIn('бед', hero.show_me_money())

    def test_one_coin(self):
        hero = make_hero()
        hero.money = MagicMock()
        hero.money.__ge__ = lambda s, o: False
        hero.money.__eq__ = lambda s, o: o == 1
        self.assertIn('единственная', hero.show_me_money())

    def test_many_coins(self):
        hero = make_hero()
        hero.money = MagicMock()
        hero.money.__ge__ = lambda s, o: True
        hero.money.how_much_money = 10
        self.assertIn('монет', hero.show_me_money())


class TestGenerateProtectionText(unittest.TestCase):
    def test_no_shield_no_armor(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        hero.armor = hero.game.no_armor
        self.assertEqual(hero.generate_protection_text(), '')

    def test_shield_only(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.protection = MagicMock()
        shield.protection.text.return_value = '2'
        hero.shield = shield
        hero.armor = hero.game.no_armor
        result = hero.generate_protection_text()
        self.assertIn('2', result)

    def test_armor_only(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        armor = MagicMock()
        armor.empty = False
        armor.protection = MagicMock()
        armor.protection.text.return_value = '3'
        hero.armor = armor
        result = hero.generate_protection_text()
        self.assertIn('3', result)

    def test_both(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.protection = MagicMock()
        shield.protection.text.return_value = '2'
        armor = MagicMock()
        armor.empty = False
        armor.protection = MagicMock()
        armor.protection.text.return_value = '3'
        hero.shield = shield
        hero.armor = armor
        result = hero.generate_protection_text()
        self.assertIn('2', result)
        self.assertIn('3', result)


class TestGenerateWeaponText(unittest.TestCase):
    def test_with_weapon(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.damage = MagicMock()
        weapon.damage.text.return_value = '1d6'
        hero.weapon = weapon
        self.assertIn('1d6', hero.generate_weapon_text())

    def test_no_weapon(self):
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        self.assertEqual(hero.generate_weapon_text(), '')


class TestCheckLight(unittest.TestCase):
    def test_room_light_on(self):
        hero = make_hero()
        hero.current_position.light = True
        self.assertTrue(hero.check_light())

    def test_torch_burning(self):
        hero = make_hero()
        hero.current_position.light = False
        hero.current_position.torch = MagicMock()
        hero.current_position.torch.burning = True
        self.assertTrue(hero.check_light())

    def test_torch_not_burning(self):
        hero = make_hero()
        hero.current_position.light = False
        hero.current_position.torch = MagicMock()
        hero.current_position.torch.burning = False
        with patch.object(hero.weapon, 'element', return_value=99):
            with patch.object(hero.shield, 'element', return_value=99):
                with patch.object(hero.armor, 'element', return_value=99):
                    self.assertFalse(hero.check_light())

    def test_no_torch(self):
        hero = make_hero()
        hero.current_position.light = False
        hero.current_position.torch = None
        with patch.object(hero.weapon, 'element', return_value=99):
            with patch.object(hero.shield, 'element', return_value=99):
                with patch.object(hero.armor, 'element', return_value=99):
                    self.assertFalse(hero.check_light())

    def test_weapon_glowing(self):
        from src.class_rune import Rune
        hero = make_hero()
        hero.current_position.light = False
        hero.current_position.torch = None
        with patch.object(hero.weapon, 'element', return_value=Rune._glowing_elements[0]):
            self.assertTrue(hero.check_light())

    def test_shield_glowing(self):
        from src.class_rune import Rune
        hero = make_hero()
        hero.current_position.light = False
        hero.current_position.torch = None
        with patch.object(hero.weapon, 'element', return_value=99):
            with patch.object(hero.shield, 'element', return_value=Rune._glowing_elements[0]):
                self.assertTrue(hero.check_light())

    def test_armor_glowing(self):
        from src.class_rune import Rune
        hero = make_hero()
        hero.current_position.light = False
        hero.current_position.torch = None
        with patch.object(hero.weapon, 'element', return_value=99):
            with patch.object(hero.shield, 'element', return_value=99):
                with patch.object(hero.armor, 'element', return_value=Rune._glowing_elements[0]):
                    self.assertTrue(hero.check_light())


class TestRest(unittest.TestCase):
    def test_cannot_rest(self):
        hero = make_hero()
        with patch.object(hero, 'check_rest_possibility', return_value=['нельзя']):
            result = hero.rest(None)
        self.assertEqual(result, ['нельзя'])

    def test_monster_ambush(self):
        hero = make_hero()
        with patch.object(hero, 'check_rest_possibility', return_value=[]):
            with patch.object(hero, 'check_monster_in_ambush', return_value=['м']):
                result = hero.rest(None)
        self.assertEqual(result, ['м'])

    def test_rest_success(self):
        hero = make_hero()
        hero.poisoned = True
        with patch.object(hero, 'check_rest_possibility', return_value=[]):
            with patch.object(hero, 'check_monster_in_ambush', return_value=[]):
                with patch.object(hero, 'sleep_while_rest', return_value=['сон']):
                    result = hero.rest(None)
        self.assertFalse(hero.poisoned)
        self.assertEqual(result, ['сон'])


class TestSleepWhileRest(unittest.TestCase):
    def test_nightmare(self):
        hero = make_hero()
        hero.fear = 4
        with patch.object(Hero._nightmare_probability, 'roll', return_value=1):
            with patch.object(hero, 'get_robbed_while_sleep', return_value=None):
                msg = hero.sleep_while_rest()
        self.assertIn('кошмар', msg[0])

    def test_good_sleep(self):
        hero = make_hero()
        hero.fear = 4
        with patch.object(Hero._nightmare_probability, 'roll', return_value=2):
            with patch.object(hero, 'get_robbed_while_sleep', return_value=None):
                msg = hero.sleep_while_rest()
        self.assertEqual(hero.fear, 0)

    def test_with_theft(self):
        hero = make_hero()
        with patch.object(Hero._nightmare_probability, 'roll', return_value=2):
            with patch.object(hero, 'get_robbed_while_sleep', return_value='Украл'):
                msg = hero.sleep_while_rest()
        self.assertIn('Украл', msg)


class TestGetRobbedWhileSleep(unittest.TestCase):
    def test_no_steal(self):
        hero = make_hero()
        with patch.object(Hero._steal_probability, 'roll', return_value=2):
            result = hero.get_robbed_while_sleep()
        self.assertIsNone(result)

    def test_empty_backpack(self):
        hero = make_hero()
        hero.backpack.is_empty = MagicMock(return_value=True)
        with patch.object(Hero._steal_probability, 'roll', return_value=1):
            result = hero.get_robbed_while_sleep()
        self.assertIsNone(result)

    def test_no_monsters(self):
        hero = make_hero()
        hero.backpack.is_empty = MagicMock(return_value=False)
        hero.floor.all_monsters = []
        with patch.object(Hero._steal_probability, 'roll', return_value=1):
            result = hero.get_robbed_while_sleep()
        self.assertIsNone(result)

    def test_theft_occurs(self):
        hero = make_hero()
        hero.backpack.is_empty = MagicMock(return_value=False)
        monster = MagicMock()
        monster.stink = False
        monster.can_steal = True
        monster.take.return_value = True
        hero.floor.all_monsters = [monster]
        item = MagicMock()
        item.__format__ = lambda s, f: 'Зелье'
        hero.backpack.get_items_except_class = MagicMock(return_value=[item])
        with patch('src.class_hero.randomitem', side_effect=lambda lst: lst[0]):
            with patch.object(hero.backpack, 'remove'):
                with patch.object(Hero._steal_probability, 'roll', return_value=1):
                    result = hero.get_robbed_while_sleep()
        self.assertIn('Зелье', result)


class TestCheckMonsterInAmbush(unittest.TestCase):
    def test_no_monster(self):
        hero = make_hero()
        place = MagicMock()
        place.monster_in_ambush.return_value = None
        result = hero.check_monster_in_ambush(place)
        self.assertEqual(result, [])

    def test_monster_found(self):
        hero = make_hero()
        place = MagicMock()
        monster = MagicMock()
        monster.name = 'Гоблин'
        monster.hiding_place = MagicMock()
        monster.frightening = False
        monster.g = lambda m, f: m
        place.monster_in_ambush.return_value = monster
        result = hero.check_monster_in_ambush(place)
        self.assertGreater(len(result), 0)
        self.assertIsNone(monster.hiding_place)

    def test_frightening_monster(self):
        hero = make_hero()
        place = MagicMock()
        monster = MagicMock()
        monster.name = 'Дракон'
        monster.hiding_place = MagicMock()
        monster.frightening = True
        monster.g = lambda m, f: m
        place.monster_in_ambush.return_value = monster
        hero.fear = 0
        hero.check_monster_in_ambush(place)
        self.assertEqual(hero.fear, 1)


class TestCheckRestPossibility(unittest.TestCase):
    def test_can_rest(self):
        hero = make_hero()
        hero.restless = 0
        room = MagicMock()
        room.can_rest.return_value = ([], True)
        result = hero.check_rest_possibility(room)
        self.assertEqual(result, [])

    def test_no_rest_place(self):
        hero = make_hero()
        room = MagicMock()
        room.can_rest.return_value = (['Нельзя'], False)
        result = hero.check_rest_possibility(room)
        self.assertGreater(len(result), 0)

    def test_restless(self):
        hero = make_hero()
        hero.restless = 5
        room = MagicMock()
        room.can_rest.return_value = ([], True)
        result = hero.check_rest_possibility(room)
        self.assertGreater(len(result), 0)


class TestPoisonEnemy(unittest.TestCase):
    def test_already_poisoned(self):
        hero = make_hero()
        target = make_enemy()
        target.poisoned = True
        self.assertIsNone(hero.poison_enemy(target))

    def test_high_poison_level_returns_none(self):
        hero = make_hero()
        target = make_enemy()
        target.poison_level = Dice([10])
        self.assertIsNone(hero.poison_enemy(target))

    def test_poison_applied(self):
        hero = make_hero()
        target = make_enemy()
        target.poisoned = False
        target.poison_level = Dice([0])
        target.get_poison_protection = MagicMock(return_value=0)
        hero.poison_level = Dice([10])
        hero.weapon = MagicMock()
        hero.weapon.get_poison_level.return_value = 10
        result = hero.poison_enemy(target)
        self.assertTrue(target.poisoned)
        self.assertIsNotNone(result)


class TestGetHitChance(unittest.TestCase):
    def test_returns_int(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.weapon_type = 'кол'
        weapon.get_hit_chance.return_value = 1
        hero.weapon = weapon
        result = hero.get_hit_chance()
        self.assertIsInstance(result, int)


class TestParryChance(unittest.TestCase):
    def test_not_poisoned(self):
        hero = make_hero()
        hero.poisoned = False
        weapon = MagicMock()
        weapon.weapon_type = 'кол'
        hero.weapon = weapon
        result = hero.parry_chance()
        self.assertIsInstance(result, int)

    def test_poisoned_reduces(self):
        hero = make_hero()
        hero.poisoned = True
        weapon = MagicMock()
        weapon.weapon_type = 'кол'
        hero.weapon = weapon
        result = hero.parry_chance()
        self.assertIsInstance(result, int)


class TestDefence(unittest.TestCase):
    def test_with_shield(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.protect.return_value = 2
        hero.shield = shield
        hero.armor = hero.game.no_armor
        attacker = make_enemy()
        attacker.weapon = MagicMock()
        attacker.weapon.hit_chance = MagicMock()
        attacker.weapon.hit_chance.roll = MagicMock(return_value=1)
        attacker.hit_chance = MagicMock()
        attacker.hit_chance.roll = MagicMock(return_value=1)
        result = hero.defence(attacker)
        self.assertIsInstance(result, int)

    def test_with_armor(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        armor = MagicMock()
        armor.empty = False
        armor.protect.return_value = 3
        hero.armor = armor
        attacker = make_enemy()
        attacker.weapon = MagicMock()
        attacker.weapon.hit_chance = MagicMock()
        attacker.weapon.hit_chance.roll = MagicMock(return_value=1)
        attacker.hit_chance = MagicMock()
        attacker.hit_chance.roll = MagicMock(return_value=1)
        result = hero.defence(attacker)
        self.assertIsInstance(result, int)


class TestDamageShield(unittest.TestCase):
    def test_calls_take_damage(self):
        hero = make_hero()
        shield = MagicMock()
        hero.shield = shield
        hero.hide = True
        hero.damage_shield()
        shield.take_damage.assert_called_once_with(True)


class TestGenerateMeleeAttack(unittest.TestCase):
    def test_returns_int(self):
        hero = make_hero()
        result = hero.generate_mele_attack()
        self.assertIsInstance(result, int)


class TestGenerateWeaponAttack(unittest.TestCase):
    def test_empty_weapon_returns_zero(self):
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        target = MagicMock()
        self.assertEqual(hero.generate_weapon_attack(target), 0)

    def test_normal_attack(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.element.return_value = 0
        weapon.type = 'колющее'
        weapon.weapon_type = 'колющее'
        weapon.attack.return_value = 10
        weapon.hit_chance = Dice([1])
        hero.weapon = weapon
        target = make_enemy()
        with patch.object(hero, 'generate_total_attack', return_value=10):
            result = hero.generate_weapon_attack(target)
        self.assertIsInstance(result, int)


class TestGenerateTotalAttack(unittest.TestCase):
    def test_returns_int(self):
        hero = make_hero()
        target = MagicMock()
        result = hero.generate_total_attack(target)
        self.assertIsInstance(result, int)


class TestGenerateTotalDamage(unittest.TestCase):
    def test_zero_defence(self):
        hero = make_hero()
        target = make_enemy()
        target.defence = MagicMock(return_value=0)
        damage, defn = hero.generate_total_damage(target, 10)
        self.assertEqual(damage, 10)

    def test_negative_defence(self):
        hero = make_hero()
        target = make_enemy()
        target.defence = MagicMock(return_value=-1)
        damage, defn = hero.generate_total_damage(target, 10)
        self.assertEqual(damage, 0)

    def test_defence_greater_than_attack(self):
        hero = make_hero()
        target = make_enemy()
        target.defence = MagicMock(return_value=20)
        damage, defn = hero.generate_total_damage(target, 10)
        self.assertEqual(damage, 0)


class TestBreakEnemyShield(unittest.TestCase):
    def test_no_shield(self):
        hero = make_hero()
        target = make_enemy()
        target.shield = MagicMock()
        target.shield.empty = True
        self.assertIsNone(hero.break_enemy_shield(target, 100))

    def test_shield_not_broken(self):
        hero = make_hero()
        target = make_enemy()
        shield = MagicMock()
        shield.empty = False
        shield.check_if_broken.return_value = False
        target.shield = shield
        self.assertIsNone(hero.break_enemy_shield(target, 10))

    def test_shield_broken(self):
        hero = make_hero()
        target = make_enemy()
        shield = MagicMock()
        shield.empty = False
        shield.check_if_broken.return_value = True
        target.shield = shield
        result = hero.break_enemy_shield(target, 100)
        self.assertIn('ломает', result)


class TestIncreaseMastery(unittest.TestCase):
    def test_empty_weapon(self):
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        self.assertIsNone(hero.increase_mastery())

    def test_max_level(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.weapon_type = 'колющее'
        hero.weapon = weapon
        hero.mastery['колющее']['level'] = 10
        hero.mastery['колющее']['max_level'] = 10
        self.assertIsNone(hero.increase_mastery())

    def test_counter_increment_no_level_up(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.weapon_type = 'колющее'
        hero.weapon = weapon
        hero.mastery['колющее']['level'] = 1
        hero.mastery['колющее']['counter'] = 0.0
        hero.mastery['колющее']['max_level'] = 10
        with patch('src.class_hero.randint', return_value=1):
            result = hero.increase_mastery()
        self.assertIsNone(result)
        self.assertGreater(hero.mastery['колющее']['counter'], 0.0)

    def test_level_up(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.weapon_type = 'колющее'
        hero.weapon = weapon
        hero.mastery['колющее']['level'] = 0
        hero.mastery['колющее']['counter'] = 0.5
        hero.mastery['колющее']['max_level'] = 10
        with patch('src.class_hero.randint', return_value=100):
            result = hero.increase_mastery()
        self.assertEqual(hero.mastery['колющее']['level'], 1)
        self.assertIsNotNone(result)

    def test_creates_new_mastery_when_type_unknown(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.weapon_type = 'рубящее'
        hero.weapon = weapon
        hero.mastery.pop('рубящее', None)
        with patch('src.class_hero.randint', return_value=100):
            result = hero.increase_mastery()
        self.assertIn('рубящее', hero.mastery)
        self.assertEqual(hero.mastery['рубящее']['level'], 1)
        self.assertIsNotNone(result)


class TestHitEnemy(unittest.TestCase):
    def test_hit_without_weapon(self):
        hero = make_hero()
        target = make_enemy()
        target.health = 100
        target.defence = MagicMock(return_value=0)
        hero.weapon = hero.game.no_weapon
        hero.poison_level = Dice([0])
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'generate_total_attack', return_value=10):
                with patch.object(hero, 'poison_enemy', return_value=None):
                    with patch.object(hero, 'increase_mastery', return_value=None):
                        with patch('src.class_hero.tprint'):
                            hero.hit_enemy(target)
        self.assertLess(target.health, 100)

    def test_miss_defence_negative(self):
        hero = make_hero()
        target = make_enemy()
        target.health = 100
        target.defence = MagicMock(return_value=-1)
        hero.weapon = hero.game.no_weapon
        hero.poison_level = Dice([0])
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'poison_enemy', return_value=None):
                with patch.object(hero, 'increase_mastery', return_value=None):
                    with patch('src.class_hero.tprint'):
                        hero.hit_enemy(target)
        self.assertEqual(target.health, 100)

    def test_zero_damage(self):
        hero = make_hero()
        target = make_enemy()
        target.health = 100
        target.defence = MagicMock(return_value=9999)
        hero.weapon = hero.game.no_weapon
        hero.poison_level = Dice([0])
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'poison_enemy', return_value=None):
                with patch.object(hero, 'increase_mastery', return_value=None):
                    with patch('src.class_hero.tprint'):
                        hero.hit_enemy(target)
        self.assertEqual(target.health, 100)


class TestGetTargetName(unittest.TestCase):
    def test_with_light(self):
        hero = make_hero()
        target = make_enemy()
        with patch.object(hero, 'check_light', return_value=True):
            name, acc = hero.get_target_name(target)
        self.assertEqual(name, 'Гоблин')

    def test_without_light(self):
        hero = make_hero()
        target = make_enemy()
        with patch.object(hero, 'check_light', return_value=False):
            name, acc = hero.get_target_name(target)
        self.assertIn('Неизвестная', name)


class TestRunAway(unittest.TestCase):
    def test_lose_items(self):
        hero = make_hero()
        target = make_enemy()
        target.weapon = MagicMock()
        target.weapon.empty = True
        target.shield = MagicMock()
        target.shield.empty = True
        target.carryweapon = False
        target.carryshield = False
        hero.weapon = hero.game.no_weapon
        hero.shield = hero.game.no_shield
        with patch('src.class_hero.randomitem', return_value=0):
            result = hero.run_away(target)
        self.assertIsInstance(result, bool)

    def test_success_with_light(self):
        hero = make_hero()
        target = make_enemy()
        target.weapon = MagicMock()
        target.weapon.empty = True
        target.shield = MagicMock()
        target.shield.empty = True
        target.carryweapon = False
        target.carryshield = False
        hero.weapon = hero.game.no_weapon
        hero.shield = hero.game.no_shield
        room = MagicMock()
        room.light = True
        room.position = 5
        room.get_available_directions.return_value = [1, 3]
        hero.current_position = room
        floor = MagicMock()
        floor.directions_dict = {0: -1, 1: 1, 2: 3, 3: -1}
        new_room = MagicMock()
        floor.plan = {6: new_room}
        hero.floor = floor
        with patch('src.class_hero.randomitem', return_value=1):
            with patch('src.class_hero.tprint'):
                result = hero.run_away(target)
        self.assertTrue(result)
        self.assertTrue(hero.run)
        self.assertIs(hero.current_position, new_room)
        self.assertTrue(new_room.visited)
        self.assertEqual(hero.restless, 0)


class TestUseInFight(unittest.TestCase):
    def test_no_items(self):
        hero = make_hero()
        hero.backpack.get_items_for_fight = MagicMock(return_value=[])
        hero.use_in_fight()

    def test_with_items(self):
        hero = make_hero()
        item = MagicMock()
        item.__format__ = lambda s, f: 'Зелье'
        hero.backpack.get_items_for_fight = MagicMock(return_value=[item])
        hero.use_in_fight()
        self.assertEqual(hero.state, state_enum.USE_IN_FIGHT)


class TestUseShield(unittest.TestCase):
    def test_no_shield(self):
        hero = make_hero()
        hero.shield = hero.game.no_shield
        target = MagicMock()
        hero.use_shield(target)
        self.assertFalse(hero.hide)

    def test_with_shield(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        hero.shield = shield
        hero.mastery = {'щиты': 0}
        hero.rage = MagicMock()
        target = MagicMock()
        hero.use_shield(target)
        self.assertTrue(hero.hide)


class TestInFightActions(unittest.TestCase):
    def test_cancel(self):
        hero = make_hero()
        result = hero.in_fight_actions('отмена')
        self.assertFalse(result)
        self.assertEqual(hero.state, state_enum.FIGHT)

    def test_use_number(self):
        hero = make_hero()
        item = MagicMock()
        item.use.return_value = True
        hero.can_use_in_fight = [item]
        hero.current_fight = MagicMock()
        result = hero.in_fight_actions('1')
        self.assertTrue(result)

    def test_invalid_number(self):
        hero = make_hero()
        item = MagicMock()
        hero.can_use_in_fight = [item]
        result = hero.in_fight_actions('99')
        self.assertFalse(result)

    def test_non_digit(self):
        hero = make_hero()
        result = hero.in_fight_actions('abc')
        self.assertFalse(result)


class TestDo(unittest.TestCase):
    def test_help(self):
        hero = make_hero()
        result = hero.do('?')
        self.assertTrue(result)

    def test_known_command(self):
        hero = make_hero()
        hero.command_dict['торговать'] = MagicMock()
        hero.do('торговать')
        hero.command_dict['торговать'].assert_called_once()

    def test_known_command_with_item(self):
        hero = make_hero()
        hero.command_dict['торговать'] = MagicMock()
        hero.do('торговать меч')
        hero.command_dict['торговать'].assert_called_once_with('меч')

    def test_unknown_command(self):
        hero = make_hero()
        hero.current_position.action_controller = MagicMock()
        hero.action_controller = MagicMock()
        hero.action_controller.get_items_by_action_and_name.return_value = []
        hero.current_position.action_controller.get_items_by_action_and_name.return_value = []
        hero.do('хз')


class TestDoFromDictionary(unittest.TestCase):
    def test_no_items_light(self):
        hero = make_hero()
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'check_fight', return_value=False):
                hero.current_position.action_controller = MagicMock()
                hero.current_position.action_controller.get_items_by_action_and_name.return_value = []
                hero.action_controller = MagicMock()
                hero.action_controller.get_items_by_action_and_name.return_value = []
                result = hero.do_from_dictionary('лечиться')
        self.assertFalse(result)

    def test_no_items_dark(self):
        hero = make_hero()
        with patch.object(hero, 'check_light', return_value=False):
            hero.current_position.action_controller = MagicMock()
            hero.current_position.action_controller.get_items_by_action_and_name.return_value = []
            hero.action_controller = MagicMock()
            hero.action_controller.get_items_by_action_and_name.return_value = []
            result = hero.do_from_dictionary('лечиться')
        self.assertFalse(result)


class TestFreeAction(unittest.TestCase):
    def test_cancel(self):
        hero = make_hero()
        result = hero.free_action('отмена')
        self.assertFalse(result)
        self.assertEqual(hero.state, state_enum.NO_STATE)

    def test_not_digit(self):
        hero = make_hero()
        result = hero.free_action('abc')
        self.assertFalse(result)

    def test_out_of_range(self):
        hero = make_hero()
        hero.to_do_list = []
        result = hero.free_action('99')
        self.assertFalse(result)

    def test_valid_item(self):
        hero = make_hero()
        item = MagicMock()
        item.action = MagicMock(return_value='ok')
        item.post_process = None
        item.duration = 1
        hero.to_do_list = [item]
        hero.game.events_controller = MagicMock()
        hero.game.events_controller.execute_all_events = MagicMock()
        hero.free_action('1')
        self.assertEqual(hero.state, state_enum.NO_STATE)


class TestBulkActions(unittest.TestCase):
    def test_bulk_items_executed(self):
        hero = make_hero()
        item = MagicMock()
        item.bulk = True
        item.duration = 3
        item.action = MagicMock(return_value='ok')
        hero.game.events_controller = MagicMock()
        items = [item]
        result = hero.bulk_actions(items)
        self.assertEqual(len(result), 0)
        hero.game.events_controller.execute_all_events.assert_called_once_with(3)

    def test_non_bulk_items_kept(self):
        hero = make_hero()
        item = MagicMock()
        item.bulk = False
        items = [item]
        result = hero.bulk_actions(items)
        self.assertEqual(len(result), 1)


class TestExcludeHiddenItems(unittest.TestCase):
    def test_visible(self):
        hero = make_hero()
        item = MagicMock()
        item.hidden = False
        self.assertEqual(len(hero.exclude_hidden_items([item])), 1)

    def test_hidden(self):
        hero = make_hero()
        item = MagicMock()
        item.hidden = MagicMock(return_value=True)
        self.assertEqual(len(hero.exclude_hidden_items([item])), 0)

    def test_callable_hidden_false(self):
        hero = make_hero()
        item = MagicMock()
        item.hidden = MagicMock(return_value=False)
        self.assertEqual(len(hero.exclude_hidden_items([item])), 1)


class TestAction(unittest.TestCase):
    def test_no_state_calls_do(self):
        hero = make_hero()
        hero.state = state_enum.NO_STATE
        with patch.object(hero, 'game') as mg:
            mg.check_endgame.return_value = False
            with patch.object(hero, 'do') as md:
                hero.action('cmd', 'msg')
                md.assert_called_once()

    def test_level_up(self):
        hero = make_hero()
        hero.state = state_enum.LEVEL_UP
        with patch.object(hero, 'levelup') as ml:
            hero.action('здоровье', '')
            ml.assert_called_once_with('здоровье')

    def test_trade_state(self):
        hero = make_hero()
        hero.state = state_enum.TRADE
        with patch.object(hero, 'trade_actions', return_value=True) as mt:
            hero.action('cmd', 'msg')
            mt.assert_called_once()

    def test_fight_state(self):
        hero = make_hero()
        hero.state = state_enum.FIGHT
        with patch.object(hero, 'fight_actions', return_value=True) as mf:
            hero.action('cmd', 'msg')
            mf.assert_called_once()

    def test_use_in_fight_state(self):
        hero = make_hero()
        hero.state = state_enum.USE_IN_FIGHT
        with patch.object(hero, 'in_fight_actions', return_value=True) as mf:
            hero.action('cmd', 'msg')
            mf.assert_called_once()

    def test_action_state(self):
        hero = make_hero()
        hero.state = state_enum.ACTION
        with patch.object(hero, 'free_action', return_value=True) as mf:
            hero.action('cmd', 'msg')
            mf.assert_called_once()

    def test_unknown_state(self):
        hero = make_hero()
        hero.state = 'badstate'
        result = hero.action('cmd', 'msg')
        self.assertFalse(result)


class TestLevelup(unittest.TestCase):
    def test_health(self):
        hero = make_hero()
        hero.state = state_enum.LEVEL_UP
        self.assertTrue(hero.levelup('здоровье'))
        self.assertEqual(hero.state, state_enum.NO_STATE)

    def test_strength(self):
        hero = make_hero()
        hero.state = state_enum.LEVEL_UP
        self.assertTrue(hero.levelup('силу'))

    def test_dexterity(self):
        hero = make_hero()
        hero.state = state_enum.LEVEL_UP
        self.assertTrue(hero.levelup('ловкость'))

    def test_intelligence(self):
        hero = make_hero()
        hero.state = state_enum.LEVEL_UP
        self.assertTrue(hero.levelup('интеллект'))

    def test_invalid(self):
        hero = make_hero()
        self.assertFalse(hero.levelup('xyz'))


class TestGainExperience(unittest.TestCase):
    def test_no_levelup(self):
        hero = make_hero()
        hero.levels = [0, 100, 200]
        hero.exp = 0
        hero.level = 1
        hero.gain_experience(10)
        self.assertEqual(hero.exp, 10)
        self.assertEqual(hero.level, 1)

    def test_levelup(self):
        hero = make_hero()
        hero.levels = [0, 5, 200]
        hero.exp = 0
        hero.level = 1
        hero.gain_experience(10)
        self.assertEqual(hero.level, 2)


class TestWin(unittest.TestCase):
    def test_increments_wins(self):
        hero = make_hero()
        old = hero.wins
        loser = MagicMock()
        loser.exp = 5
        hero.win(loser)
        self.assertEqual(hero.wins, old + 1)
        self.assertEqual(hero.restless, 0)


class TestLose(unittest.TestCase):
    def test_resets(self):
        hero = make_hero()
        save = MagicMock()
        hero.save_room = save
        result = hero.lose(MagicMock())
        self.assertEqual(hero.current_position, save)
        self.assertEqual(hero.restless, 0)
        self.assertEqual(hero.last_move, move_enum.START)
        self.assertIsInstance(result, list)


class TestResetDice(unittest.TestCase):
    def test_resets(self):
        hero = make_hero()
        hero.health = 1
        hero.start_health = 100
        hero.reset_dice()
        self.assertEqual(hero.health, 100)


class TestDetectTrap(unittest.TestCase):
    def test_already_seen(self):
        hero = make_hero()
        trap = MagicMock()
        trap.seen = True
        self.assertTrue(hero.detect_trap(trap))

    def test_not_seen_fails(self):
        hero = make_hero()
        trap = MagicMock()
        trap.seen = False
        trap.difficulty = 100
        with patch.object(hero, 'check_intel', return_value=1):
            self.assertFalse(hero.detect_trap(trap))

    def test_not_seen_success(self):
        hero = make_hero()
        trap = MagicMock()
        trap.seen = False
        trap.difficulty = 1
        with patch.object(hero, 'check_intel', return_value=10):
            hero.detect_trap(trap)
        self.assertTrue(trap.seen)


class TestPutInBackpack(unittest.TestCase):
    def test_adds_item(self):
        hero = make_hero()
        item = MagicMock()
        item.__format__ = lambda s, f: 'Предмет'
        with patch.object(hero.current_position.loot, 'is_item_in_loot', return_value=False):
            result = hero.put_in_backpack(item)
        self.assertTrue(result)
        self.assertEqual(item.owner, hero)


class TestUseItemFromBackpack(unittest.TestCase):
    def test_no_backpack(self):
        hero = make_hero()
        hero.backpack.no_backpack = True
        self.assertFalse(hero.use_item_from_backpack('1'))

    def test_digit_item(self):
        hero = make_hero()
        hero.backpack.no_backpack = False
        item = MagicMock()
        item.use.return_value = True
        with patch.object(hero.backpack, 'get_item_by_number', return_value=item):
            self.assertTrue(hero.use_item_from_backpack('1'))

    def test_not_found(self):
        hero = make_hero()
        hero.backpack.no_backpack = False
        with patch.object(hero.backpack, 'get_item_by_number', return_value=None):
            with patch.object(hero.backpack, 'get_first_item_by_name', return_value=None):
                self.assertFalse(hero.use_item_from_backpack('xyz'))


class TestUse(unittest.TestCase):
    def test_no_item(self):
        hero = make_hero()
        self.assertFalse(hero.use(None))

    def test_backpack_item(self):
        hero = make_hero()
        hero.removed_shield = MagicMock()
        hero.removed_shield.check_name.return_value = False
        with patch.object(hero, 'use_item_from_backpack', return_value=True):
            self.assertTrue(hero.use('меч'))


class TestGoWithLightOn(unittest.TestCase):
    def test_no_door(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = True
        hero.current_position.doors = [door]
        self.assertIn('нет двери', hero.go_with_light_on(0))

    def test_locked(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = False
        door.locked = True
        hero.current_position.doors = [door]
        self.assertIn('заперта', hero.go_with_light_on(0))

    def test_open(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = False
        door.locked = False
        door.get_another_room.return_value = MagicMock()
        hero.current_position.doors = [door]
        with patch.object(hero, 'move'):
            self.assertEqual(hero.go_with_light_on(0), '')


class TestGoWithLightOff(unittest.TestCase):
    def test_going_back_locked(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = True
        door.locked = False
        hero.current_position.doors = [door]
        hero.last_move = move_enum.UP
        with patch.object(hero, 'check_if_going_back', return_value=True):
            with patch.object(hero, 'check_noise', return_value=False):
                result = hero.go_with_light_off(0)
        self.assertIn('врезается', result)

    def test_locked_in_dark(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = False
        door.locked = True
        hero.current_position.doors = [door]
        hero.last_move = move_enum.UP
        with patch.object(hero, 'check_if_going_back', return_value=True):
            with patch.object(hero, 'check_noise', return_value=False):
                result = hero.go_with_light_off(0)
        self.assertIn('врезается', result)


class TestCheckNoise(unittest.TestCase):
    def test_noisy(self):
        hero = make_hero()
        hero.weapon = MagicMock()
        hero.weapon.noisy = True
        hero.shield = MagicMock()
        hero.shield.noisy = False
        hero.armor = MagicMock()
        hero.armor.noisy = False
        self.assertTrue(hero.check_noise())

    def test_shield_noisy(self):
        hero = make_hero()
        hero.weapon = MagicMock()
        hero.weapon.noisy = False
        hero.shield = MagicMock()
        hero.shield.noisy = True
        hero.armor = MagicMock()
        hero.armor.noisy = False
        self.assertTrue(hero.check_noise())

    def test_armor_noisy(self):
        hero = make_hero()
        hero.weapon = MagicMock()
        hero.weapon.noisy = False
        hero.shield = MagicMock()
        hero.shield.noisy = False
        hero.armor = MagicMock()
        hero.armor.noisy = True
        self.assertTrue(hero.check_noise())

    def test_silent(self):
        hero = make_hero()
        hero.weapon = MagicMock()
        hero.weapon.noisy = False
        hero.shield = MagicMock()
        hero.shield.noisy = False
        hero.armor = MagicMock()
        hero.armor.noisy = False
        self.assertFalse(hero.check_noise())


class TestSneakThroughDarkRoom(unittest.TestCase):
    def test_monster_detected(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        monster = MagicMock()
        monster.check_name.return_value = False
        room.has_a_monster = MagicMock(return_value=True)
        room.monsters = MagicMock(return_value=[monster])
        room.ladder_down = None
        room.has_furniture = MagicMock(return_value=False)
        with patch.object(hero, 'check_if_sneak_past_monster', return_value=False):
            result = hero.sneak_through_dark_room()
        self.assertFalse(result[0])

    def test_empty_room(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        room.has_a_monster = MagicMock(return_value=False)
        room.ladder_down = None
        room.has_furniture = MagicMock(return_value=False)
        result = hero.sneak_through_dark_room()
        self.assertTrue(result[0])


class TestCheckIfGoingBack(unittest.TestCase):
    def test_going_back(self):
        hero = make_hero()
        hero.last_move = move_enum.UP
        self.assertTrue(hero.check_if_going_back(hero.last_move.countermove))

    def test_not_going_back(self):
        hero = make_hero()
        hero.last_move = move_enum.UP
        self.assertFalse(hero.check_if_going_back(99))


class TestMove(unittest.TestCase):
    def test_sets_position(self):
        hero = make_hero()
        new_room = MagicMock()
        with patch.object(hero, 'check_monster_and_figth'):
            hero.move(new_room)
        self.assertEqual(hero.current_position, new_room)
        self.assertTrue(new_room.visited)


class TestCheckDisturbedMonsters(unittest.TestCase):
    def test_disturbed_found(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        m = MagicMock()
        m.disturbed = True
        m.frightening = False
        room.monsters = MagicMock(return_value=[m])
        with patch.object(hero, 'fight'):
            self.assertTrue(hero.check_disturbed_monsters(None))

    def test_none_disturbed(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        m = MagicMock()
        m.disturbed = False
        room.monsters = MagicMock(return_value=[m])
        self.assertFalse(hero.check_disturbed_monsters(None))


class TestCheckMonsterAndFight(unittest.TestCase):
    def test_no_monster(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        room.monsters.return_value = None
        hero.check_monster_and_figth()

    def test_aggressive_in_light(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        m = MagicMock()
        m.aggressive = True
        room.monsters.return_value = m
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'fight') as mf:
                hero.check_monster_and_figth()
                mf.assert_called_once_with(m)

    def test_passive(self):
        hero = make_hero()
        room = MagicMock()
        hero.current_position = room
        m = MagicMock()
        m.aggressive = False
        room.monsters.return_value = m
        with patch.object(hero, 'fight') as mf:
            hero.check_monster_and_figth()
            mf.assert_not_called()


class TestTradeActions(unittest.TestCase):
    def test_no_trader(self):
        hero = make_hero()
        hero.trader = None
        result = hero.trade_actions('купить меч')
        self.assertFalse(result)

    def test_leave_shop(self):
        hero = make_hero()
        hero.trader = MagicMock()
        with patch.object(hero, 'leave_shop', return_value=True):
            result = hero.trade_actions('закончить')
            self.assertTrue(result)

    def test_buy(self):
        hero = make_hero()
        hero.trader = MagicMock()
        with patch.object(hero, 'buy_item', return_value=True):
            result = hero.trade_actions('купить меч')
            self.assertTrue(result)

    def test_sell(self):
        hero = make_hero()
        hero.trader = MagicMock()
        with patch.object(hero, 'sell_item', return_value=True):
            result = hero.trade_actions('продать меч')
            self.assertTrue(result)

    def test_unknown_action(self):
        hero = make_hero()
        hero.trader = MagicMock()
        result = hero.trade_actions('xyz abc')
        self.assertFalse(result)


class TestBuyItem(unittest.TestCase):
    def test_buy(self):
        hero = make_hero()
        hero.trader = MagicMock()
        hero.trader.sell.return_value = True
        with patch('src.class_hero.tprint'):
            hero.buy_item('меч')
        hero.trader.sell.assert_called_once()

    def test_buy_fails(self):
        hero = make_hero()
        hero.trader = MagicMock()
        hero.trader.sell.return_value = False
        with patch('src.class_hero.tprint'):
            hero.buy_item('меч')


class TestSellItem(unittest.TestCase):
    def test_sell(self):
        hero = make_hero()
        hero.trader = MagicMock()
        hero.trader.buy.return_value = True
        with patch('src.class_hero.tprint'):
            hero.sell_item('меч')
        hero.trader.buy.assert_called_once()


class TestGetSecondWeapon(unittest.TestCase):
    def test_found(self):
        hero = make_hero()
        weapon = MagicMock()
        hero.backpack.get_first_item_by_class = MagicMock(return_value=weapon)
        self.assertEqual(hero.get_second_weapon(), weapon)

    def test_not_found(self):
        hero = make_hero()
        hero.backpack.get_first_item_by_class = MagicMock(return_value=None)
        result = hero.get_second_weapon()
        self.assertTrue(result.empty)


class TestGetMap(unittest.TestCase):
    def test_no_map(self):
        hero = make_hero()
        hero.backpack.get_items_by_class = MagicMock(return_value=[])
        self.assertIsNone(hero.get_map())


class TestGenerateRunAwayText(unittest.TestCase):
    def test_frightening_in_light(self):
        hero = make_hero()
        target = make_enemy()
        target.frightening = True
        with patch.object(hero, 'check_light', return_value=True):
            result = hero.generate_run_away_text(target)
        self.assertIn('ужасе', result)

    def test_not_frightening(self):
        hero = make_hero()
        target = make_enemy()
        target.frightening = False
        with patch.object(hero, 'check_light', return_value=True):
            result = hero.generate_run_away_text(target)
        self.assertIn('сбегает', result)

    def test_dark(self):
        hero = make_hero()
        target = make_enemy()
        target.frightening = False
        with patch.object(hero, 'check_light', return_value=False):
            result = hero.generate_run_away_text(target)
        self.assertIn('тьме', result)


class TestFight(unittest.TestCase):
    def test_hero_started(self):
        hero = make_hero()
        enemy = MagicMock()
        with patch('src.class_hero.Fight') as MockFight:
            mock_fight = MagicMock()
            MockFight.return_value = mock_fight
            result = hero.fight(enemy, enemy_started=False)
            self.assertTrue(result)

    def test_enemy_started(self):
        hero = make_hero()
        enemy = MagicMock()
        with patch('src.class_hero.Fight') as MockFight:
            mock_fight = MagicMock()
            MockFight.return_value = mock_fight
            result = hero.fight(enemy, enemy_started=True)
            self.assertTrue(result)


class TestFormatPronoun(unittest.TestCase):
    def test_male_pronoun(self):
        hero = make_hero()
        hero.gender = 0
        self.assertEqual(f'{hero:pronoun}', 'он')

    def test_female_pronoun(self):
        hero = make_hero()
        hero.gender = 1
        self.assertEqual(f'{hero:pronoun}', 'она')


class TestStr(unittest.TestCase):
    def test_str(self):
        hero = make_hero()
        result = str(hero)
        self.assertIn('Hero', result)
        self.assertIn(hero.name, result)


class TestIsHero(unittest.TestCase):
    def test_returns_true(self):
        hero = make_hero()
        self.assertTrue(hero.is_hero())


class TestTestMethod(unittest.TestCase):
    def test_calls_game_test(self):
        hero = make_hero()
        with patch.object(hero.game, 'test'):
            with patch('src.class_hero.tprint'):
                hero.test()


class TestGoDownWithLightOffOpen(unittest.TestCase):
    def test_open_ladder_calls_descend(self):
        hero = make_hero()
        room = MagicMock()
        room.ladder_down = MagicMock()
        room.ladder_down.locked = False
        room.ladder_down.room_down = MagicMock()
        hero.current_position = room
        with patch.object(hero, 'move', return_value='') as mock_move:
            hero.go_down_with_light_off()
        mock_move.assert_called_once_with(room.ladder_down.room_down)


class TestGoUpWithLightOffOpen(unittest.TestCase):
    def test_open_ladder_calls_ascend(self):
        hero = make_hero()
        room = MagicMock()
        room.ladder_up = MagicMock()
        room.ladder_up.locked = False
        room.ladder_up.room_up = MagicMock()
        hero.current_position = room
        with patch.object(hero, 'move', return_value='') as mock_move:
            hero.go_up_with_light_off()
        mock_move.assert_called_once_with(room.ladder_up.room_up)


class TestGoUpWithLightOnOpen(unittest.TestCase):
    def test_open_ladder_calls_ascend(self):
        hero = make_hero()
        room = MagicMock()
        room.ladder_up = MagicMock()
        room.ladder_up.locked = False
        room.ladder_up.room_up = MagicMock()
        hero.current_position = room
        with patch.object(hero, 'move', return_value='') as mock_move:
            hero.go_up_with_light_on()
        mock_move.assert_called_once_with(room.ladder_up.room_up)


class TestUseInFightItemFails(unittest.TestCase):
    def test_item_use_returns_false(self):
        hero = make_hero()
        item = MagicMock()
        item.use.return_value = False
        item.__format__ = lambda s, f: 'Зелье'
        hero.can_use_in_fight = [item]
        with patch('src.class_hero.tprint'):
            result = hero.in_fight_actions('1')
        self.assertFalse(result)
        self.assertEqual(hero.state, state_enum.FIGHT)


class TestFightActionsWithEnemy(unittest.TestCase):
    def test_enemy_found_calls_attack(self):
        hero = make_hero()
        fight = MagicMock()
        hero.current_fight = fight
        enemy = MagicMock()
        fight.get_fighter.return_value = enemy
        with patch.object(hero, 'attack', return_value=True):
            with patch('src.class_hero.split_actions', return_value=('', '')):
                result = hero.fight_actions('атаковать')
        fight.get_fighter.assert_called_once_with(text='', for_hero=True)
        fight.continue_after_hero.assert_called_once()


class TestLeaveShop(unittest.TestCase):
    def test_leave_shop(self):
        hero = make_hero()
        trader = MagicMock()
        trader.__format__ = lambda s, f: 'Торговец'
        hero.trader = trader
        with patch('src.class_hero.tprint'):
            result = hero.leave_shop()
        self.assertTrue(result)
        self.assertEqual(hero.state, state_enum.NO_STATE)
        self.assertIsNone(hero.trader)


class TestTrade(unittest.TestCase):
    def test_trade_success(self):
        hero = make_hero()
        trader = MagicMock()
        trader.get_prices.return_value = []
        trader.__format__ = lambda s, f: 'Торговец'
        hero.current_position = MagicMock()
        hero.current_position.trader = trader
        with patch('src.class_hero.tprint'):
            result = hero.trade()
        self.assertTrue(result)
        self.assertEqual(hero.state, state_enum.TRADE)
        self.assertEqual(hero.trader, trader)

    def test_trade_no_trader(self):
        hero = make_hero()
        hero.current_position = MagicMock()
        hero.current_position.trader = None
        with patch('src.class_hero.tprint'):
            result = hero.trade()
        self.assertFalse(result)


class TestTryToDisarmTrapFail(unittest.TestCase):
    def test_disarm_fails(self):
        hero = make_hero()
        trap = MagicMock()
        trap.get_difficulty.return_value = 100
        with patch.object(hero, 'get_disarm_trap_chance', return_value=0):
            result = hero.try_to_disarm_trap(trap)
        trap.trigger.assert_called_once_with(hero)


class TestDoSingleActionPostProcess(unittest.TestCase):
    def test_post_process_called(self):
        hero = make_hero()
        item = MagicMock()
        item.action.return_value = ['Действие']
        item.post_process = MagicMock()
        item.duration = 1
        with patch('src.class_hero.tprint'):
            result = hero.do_single_action(item)
        self.assertTrue(result)
        item.post_process.assert_called_once_with(hero)


class TestGetPoisonProtectionPoisoned(unittest.TestCase):
    def test_poisoned_armor_increases_protection(self):
        hero = make_hero()
        hero.armor = MagicMock()
        hero.armor.empty = False
        hero.armor.is_poisoned.return_value = True
        hero.shield = MagicMock()
        hero.shield.empty = True
        with patch.object(hero.poison_protection, 'roll', return_value=3):
            result = hero.get_poison_protection()
        self.assertEqual(result, 5)

    def test_poisoned_shield_increases_protection(self):
        hero = make_hero()
        hero.armor = MagicMock()
        hero.armor.empty = True
        hero.shield = MagicMock()
        hero.shield.empty = False
        hero.shield.is_poisoned.return_value = True
        with patch.object(hero.poison_protection, 'roll', return_value=3):
            result = hero.get_poison_protection()
        self.assertEqual(result, 5)


class TestPoisonEnemyProtectionBlocks(unittest.TestCase):
    def test_protection_blocks_poison(self):
        hero = make_hero()
        target = MagicMock()
        target.poisoned = False
        target.poison_level = MagicMock()
        target.poison_level.base_die.return_value = 0
        target.get_poison_protection.return_value = 100
        with patch.object(hero.poison_level, 'roll', return_value=0):
            with patch.object(hero.weapon, 'get_poison_level', return_value=0):
                result = hero.poison_enemy(target)
        self.assertIsNone(result)
        self.assertFalse(target.poisoned)


class TestGenerateInFightDescription(unittest.TestCase):
    def test_returns_string(self):
        hero = make_hero()
        result = hero.generate_in_fight_description(1)
        self.assertIsInstance(result, str)
        self.assertIn('1:', result)
        self.assertIn(hero.name, result)


class TestLoseWeaponToLoot(unittest.TestCase):
    def test_weapon_goes_to_loot(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.__format__ = lambda s, f: 'Меч'
        hero.weapon = weapon
        target = MagicMock()
        target.weapon.empty = False
        room = MagicMock()
        hero.current_position = room
        with patch('src.class_hero.randint', return_value=1):
            result = hero.lose_weapon_or_shield(target)
        self.assertIsNotNone(result)
        room.loot.add.assert_called_once_with(weapon)


class TestLoseShieldToLoot(unittest.TestCase):
    def test_shield_goes_to_loot(self):
        hero = make_hero()
        shield = MagicMock()
        shield.empty = False
        shield.__format__ = lambda s, f: 'Щит'
        hero.shield = shield
        target = MagicMock()
        target.shield.empty = False
        room = MagicMock()
        hero.current_position = room
        with patch('src.class_hero.randint', return_value=2):
            result = hero.lose_weapon_or_shield(target)
        self.assertIsNotNone(result)
        room.loot.add.assert_called_once_with(shield)


class TestLoseRandomItems(unittest.TestCase):
    def test_loses_items(self):
        hero = make_hero()
        item = MagicMock()
        item.lexemes = {'accus': 'меч'}
        hero.backpack = MagicMock()
        hero.backpack.count_items.return_value = 3
        hero.backpack.get_random_item.return_value = item
        hero.backpack.remove.return_value = True
        room = MagicMock()
        hero.current_position = room
        with patch('src.class_hero.roll', return_value=1):
            result = hero.lose_random_items()
        self.assertGreater(len(result), 0)


class TestRunAwayDarkness(unittest.TestCase):
    def test_runs_into_wall(self):
        hero = make_hero()
        target = MagicMock()
        target.frightening = False
        target.weapon = MagicMock()
        target.weapon.empty = True
        target.carryweapon = False
        target.shield = MagicMock()
        target.shield.empty = True
        target.carryshield = False
        room = MagicMock()
        room.get_available_directions.return_value = [1, 2]
        hero.current_position = room
        hero.weapon = hero.game.no_weapon
        hero.shield = hero.game.no_shield
        with patch.object(hero, 'check_light', return_value=False):
            with patch.object(hero, 'check_noise', return_value=False):
                with patch.object(hero, 'generate_run_away_text', return_value=''):
                    with patch.object(hero, 'lose_weapon_or_shield', return_value=''):
                        with patch.object(hero, 'lose_random_items', return_value=[]):
                            with patch('src.class_hero.randint', return_value=3):
                                with patch('src.class_hero.tprint'):
                                    result = hero.run_away(target)
        self.assertFalse(result)


class TestGenerateWeaponAttackVampire(unittest.TestCase):
    def test_vampire_element_4(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.element.return_value = 4
        weapon.weapon_type = 'колющее'
        hero.weapon = weapon
        target = MagicMock()
        target.health = 50
        target.__class__ = type('Vampire', (), {})
        from src.class_monsters import Vampire
        target = MagicMock(spec=Vampire)
        target.health = 50
        result = hero.generate_weapon_attack(target)
        self.assertEqual(result, 50)


class TestGenerateWeaponAttackCritical(unittest.TestCase):
    def test_critical_hit(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.element.return_value = 0
        weapon.type = 'рубящее'
        weapon.weapon_type = 'рубящее'
        weapon.attack.return_value = 10
        hero.weapon = weapon
        hero.poisoned = False
        hero.mastery['рубящее']['level'] = 5
        target = MagicMock()
        with patch('src.class_hero.randint', return_value=1):
            result = hero.generate_weapon_attack(target)
        self.assertEqual(result, 10 * Hero._critical_multiplier)


class TestHitEnemyWithWeapon(unittest.TestCase):
    def test_weapon_path(self):
        hero = make_hero()
        weapon = MagicMock()
        weapon.empty = False
        weapon.actions = ['атакует']
        weapon.__format__ = lambda s, f: 'Меч'
        hero.weapon = weapon
        target = make_enemy()
        target.health = 100
        target.defence = MagicMock(return_value=0)
        hero.poison_level = Dice([0])
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'generate_total_attack', return_value=10):
                with patch('src.class_hero.randomitem', return_value='атакует'):
                    with patch.object(hero, 'poison_enemy', return_value=None):
                        with patch.object(hero, 'increase_mastery', return_value=None):
                            with patch('src.class_hero.tprint'):
                                hero.hit_enemy(target)
        self.assertLess(target.health, 100)


class TestAttackUseInFight(unittest.TestCase):
    def test_use_in_fight_action(self):
        hero = make_hero()
        target = MagicMock()
        with patch.object(hero, 'use_in_fight'):
            with patch('src.class_hero.split_actions', return_value=('', '')):
                result = hero.attack(target, 'использовать')
        self.assertTrue(result)


class TestAttackChangeWeapon(unittest.TestCase):
    def test_change_weapon_action(self):
        hero = make_hero()
        target = MagicMock()
        hero.change_weapon = MagicMock()
        with patch('src.class_hero.tprint'):
            with patch('src.class_hero.split_actions', return_value=('', '')):
                result = hero.attack(target, 'сменить')
        self.assertTrue(result)
        hero.change_weapon.assert_called_once()


class TestTryToParrySuccess(unittest.TestCase):
    def test_parry_succeeds(self):
        hero = make_hero()
        attacker = MagicMock()
        attacker.weapon = MagicMock()
        with patch.object(hero, 'parry_chance', return_value=100):
            attacker.hit_chance = Dice([0])
            attacker.weapon.hit_chance = Dice([0])
            result = hero.try_to_parry(attacker)
        self.assertTrue(result)


class TestDefenceParry(unittest.TestCase):
    def test_parry_returns_negative(self):
        hero = make_hero()
        attacker = MagicMock()
        attacker.weapon = MagicMock()
        hero.shield = hero.game.no_shield
        hero.armor = hero.game.no_armor
        with patch.object(hero, 'parry_chance', return_value=100):
            attacker.hit_chance = Dice([0])
            attacker.weapon.hit_chance = Dice([0])
            result = hero.defence(attacker)
        self.assertEqual(result, -1)


class TestGoWithLightOffSneakFails(unittest.TestCase):
    def test_sneak_fails_returns_text(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = False
        door.locked = False
        door.get_another_room.return_value = MagicMock()
        room = MagicMock()
        room.doors = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        room.doors[1] = door
        hero.current_position = room
        hero.last_move = MagicMock()
        hero.last_move.countermove = 0
        with patch.object(hero, 'check_light', return_value=False):
            with patch.object(hero, 'sneak_through_dark_room', return_value=(False, 'Столкновение')):
                with patch('src.class_hero.tprint'):
                    result = hero.go_with_light_off(1)
        self.assertEqual(result, 'Столкновение')


class TestGoWithLightOffDoorLocked(unittest.TestCase):
    def test_door_locked_noise(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = False
        door.locked = True
        room = MagicMock()
        room.doors = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        room.doors[1] = door
        hero.current_position = room
        hero.last_move = MagicMock()
        hero.last_move.countermove = 0
        with patch.object(hero, 'check_light', return_value=False):
            with patch.object(hero, 'sneak_through_dark_room', return_value=(True, '')):
                with patch.object(hero, 'check_noise', return_value=True):
                    with patch('src.class_hero.tprint'):
                        result = hero.go_with_light_off(1)
        room.noise.assert_called_once_with(3)


class TestGoWithLightOffSuccess(unittest.TestCase):
    def test_successful_movement(self):
        hero = make_hero()
        door = MagicMock()
        door.empty = False
        door.locked = False
        door.get_another_room.return_value = MagicMock()
        room = MagicMock()
        room.doors = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        room.doors[1] = door
        hero.current_position = room
        hero.last_move = MagicMock()
        hero.last_move.countermove = 0
        with patch.object(hero, 'check_light', return_value=False):
            with patch.object(hero, 'sneak_through_dark_room', return_value=(True, '')):
                with patch.object(hero, 'move', return_value='') as mock_move:
                    hero.go_with_light_off(1)
        mock_move.assert_called_once()


class TestSneakFallDown(unittest.TestCase):
    def test_fall_down_ladder(self):
        hero = make_hero()
        room = MagicMock()
        room.has_a_monster.return_value = False
        room.ladder_down = MagicMock()
        room.has_furniture.return_value = False
        hero.current_position = room
        with patch.object(hero, 'try_not_to_fall_down', return_value=False):
            with patch.object(hero, 'descend', return_value=''):
                result = hero.sneak_through_dark_room()
        self.assertFalse(result[0])
        self.assertIn('лестнице', result[1])


class TestSneakFurnitureHit(unittest.TestCase):
    def test_furniture_hit(self):
        hero = make_hero()
        room = MagicMock()
        room.has_a_monster.return_value = False
        room.ladder_down = None
        room.has_furniture.return_value = True
        hero.current_position = room
        hero.generate_noise = MagicMock()
        with patch.object(hero, 'try_not_to_fall_down', return_value=True):
            with patch.object(hero, 'check_if_sneak_past_furniture', return_value=False):
                result = hero.sneak_through_dark_room()
        self.assertFalse(result[0])
        self.assertIn('мебель', result[1])


class TestTryNotToFallDown(unittest.TestCase):
    def test_falls(self):
        hero = make_hero()
        hero.dext_check = MagicMock(return_value=False)
        result = hero.try_not_to_fall_down()
        self.assertFalse(result)

    def test_stays(self):
        hero = make_hero()
        hero.dext_check = MagicMock(return_value=True)
        result = hero.try_not_to_fall_down()
        self.assertTrue(result)


class TestUseItemFromBackpackMap(unittest.TestCase):
    def test_map_item(self):
        hero = make_hero()
        hero.backpack.no_backpack = False
        map_item = MagicMock()
        with patch.object(hero, 'get_map', return_value=map_item):
            result = hero.use_item_from_backpack('карту')
        map_item.use.assert_called_once()
        self.assertTrue(result)


class TestUseRemovedShield(unittest.TestCase):
    def test_use_shield_name(self):
        hero = make_hero()
        shield = MagicMock()
        hero.removed_shield = shield
        shield.check_name.return_value = True
        hero.take_out_shield = MagicMock(return_value=True)
        result = hero.use('roken')
        self.assertTrue(result)


class TestDoFromDictionaryMultipleItems(unittest.TestCase):
    def test_multiple_items_shows_list(self):
        hero = make_hero()
        item1 = MagicMock()
        item1.presentation = None
        item1.name = 'Предмет'
        item2 = MagicMock()
        item2.presentation = None
        item2.name = 'Вещь'
        items = [item1, item2]
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'check_fight', return_value=False):
                with patch.object(hero, 'get_items_for_action', return_value=items):
                    with patch.object(hero, 'exclude_hidden_items', return_value=items):
                        with patch.object(hero, 'bulk_actions', return_value=items):
                            with patch('src.class_hero.tprint'):
                                result = hero.do_from_dictionary('осмотреть')
        self.assertTrue(result)
        self.assertEqual(hero.state, state_enum.ACTION)

    def test_single_item_auto_selects(self):
        hero = make_hero()
        item = MagicMock()
        item.item = hero
        item.action.return_value = ['Действие']
        item.post_process = None
        item.duration = 1
        items = [item]
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'check_fight', return_value=False):
                with patch.object(hero, 'get_items_for_action', return_value=items):
                    with patch('src.class_hero.tprint'):
                        result = hero.do_from_dictionary('осмотреть', 'осмотр')
        self.assertTrue(result)

    def test_bulk_actions_empty(self):
        hero = make_hero()
        item1 = MagicMock()
        item1.item = 'something'
        items = [item1]
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'check_fight', return_value=False):
                with patch.object(hero, 'get_items_for_action', return_value=items):
                    with patch.object(hero, 'exclude_hidden_items', return_value=items):
                        with patch.object(hero, 'bulk_actions', return_value=[]):
                            with patch('src.class_hero.tprint'):
                                result = hero.do_from_dictionary('осмотреть')
        self.assertTrue(result)

    def test_presentation_branch(self):
        hero = make_hero()
        item1 = MagicMock()
        item1.presentation = lambda h: 'Красивая штука'
        item2 = MagicMock()
        item2.presentation = lambda h: 'Ещё одна штука'
        items = [item1, item2]
        with patch.object(hero, 'check_light', return_value=True):
            with patch.object(hero, 'check_fight', return_value=False):
                with patch.object(hero, 'get_items_for_action', return_value=items):
                    with patch.object(hero, 'exclude_hidden_items', return_value=items):
                        with patch.object(hero, 'bulk_actions', return_value=items):
                            with patch('src.class_hero.tprint'):
                                result = hero.do_from_dictionary('осмотреть')
        self.assertTrue(result)
        self.assertEqual(hero.state, state_enum.ACTION)


class TestPutInBackpackFromLoot(unittest.TestCase):
    def test_removes_from_loot(self):
        hero = make_hero()
        item = MagicMock()
        item.__format__ = lambda s, f: 'Предмет'
        with patch.object(hero.current_position.loot, 'is_item_in_loot', return_value=True):
            with patch.object(hero.current_position.loot, 'remove') as mock_remove:
                result = hero.put_in_backpack(item)
        self.assertTrue(result)
        mock_remove.assert_called_once_with(item)
        self.assertEqual(item.owner, hero)


if __name__ == '__main__':
    unittest.main()
