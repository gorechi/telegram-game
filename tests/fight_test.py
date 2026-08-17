import unittest
from unittest.mock import MagicMock, patch
from collections import deque

from src.class_fight import Fight
from src.class_game import Game
from src.enums import state_enum

Game.__del__ = lambda self: None


class MockFighter:
    def __init__(self, name='Monster', is_hero_val=False, health=10, stren=5, exp=10, initiative=5, has_light=False):
        self.name = name
        self._is_hero = is_hero_val
        self.health = health
        self.stren = stren
        self.exp = exp
        self._initiative = initiative
        self._has_light = has_light
        self.current_position = MagicMock()
        self.current_fight = None
        self.state = None
        self.last_attacker = None

    def is_hero(self):
        return self._is_hero

    def check_light(self):
        return self._has_light

    def generate_initiative(self):
        return self._initiative

    def generate_in_fight_description(self, index):
        return f'{self.name} #{index}'

    def attack(self, fight):
        return f'{self.name} атакует'

    def lose(self, fight):
        return f'{self.name} проиграл'

    def choose_target(self, fight):
        return fight.get_targets(self)

    def want_to_fight(self, fight):
        return True

    def __eq__(self, other):
        if isinstance(other, MockFighter):
            return self is other
        return NotImplemented

    def __repr__(self):
        return f'MockFighter({self.name})'


class Goblin(MockFighter):
    pass


class Orc(MockFighter):
    pass


def make_hero(name='Hero', health=100, stren=10, initiative=10, has_light=True):
    hero = MockFighter(name=name, is_hero_val=True, health=health, stren=stren, initiative=initiative, has_light=has_light)
    hero.current_position = MagicMock()
    hero.current_fight = None
    hero.state = state_enum.NO_STATE
    return hero


def make_goblin(name='Goblin', health=10, stren=5, exp=10, initiative=5, has_light=False):
    return Goblin(name=name, health=health, stren=stren, exp=exp, initiative=initiative, has_light=has_light)


def make_orc(name='Orc', health=15, stren=8, exp=15, initiative=3, has_light=False):
    return Orc(name=name, health=health, stren=stren, exp=exp, initiative=initiative, has_light=has_light)


def make_game():
    return Game(chat_id='test', bot=MagicMock())


def make_fight(hero=None, monsters=None, who_started=None):
    game = make_game()
    if hero is None:
        hero = make_hero()
    if monsters is None:
        monsters = [make_goblin()]
    fighters = [hero] + list(monsters)
    if who_started is None:
        who_started = hero
    return Fight(game=game, hero=hero, who_started=who_started, fighters=fighters)


def make_fight_no_hero(monsters=None):
    game = make_game()
    if monsters is None:
        monsters = [make_goblin('A'), make_goblin('B')]
    fight = Fight.__new__(Fight)
    fight.game = game
    fight.hero = None
    fight.who_started = monsters[0]
    fight.fighters = list(monsters)
    fight.room = MagicMock()
    fight.finished = False
    fight.exp = 0
    fight.light = fight.check_light()
    fight.queue = fight.create_queue()
    fight.hero_in_fight = fight.check_hero_in_fight()
    return fight


@patch('src.class_fight.tprint')
class TestFightInit(unittest.TestCase):
    def test_creates_fight(self, mock_tprint):
        fight = make_fight()
        self.assertIsNotNone(fight.game)
        self.assertIsNotNone(fight.hero)
        self.assertTrue(fight.hero_in_fight)
        self.assertFalse(fight.finished)
        self.assertEqual(fight.exp, 0)

    def test_room_is_hero_position(self, mock_tprint):
        fight = make_fight()
        self.assertEqual(fight.room, fight.hero.current_position)

    def test_hero_started(self, mock_tprint):
        fight = make_fight()
        self.assertEqual(fight.who_started, fight.hero)

    def test_creates_queue(self, mock_tprint):
        fight = make_fight()
        self.assertIsInstance(fight.queue, deque)
        self.assertEqual(len(fight.queue), 2)

    def test_check_light_true(self, mock_tprint):
        fight = make_fight()
        self.assertTrue(fight.light)

    def test_check_light_false(self, mock_tprint):
        hero = make_hero(has_light=False)
        m = make_goblin(has_light=False)
        fight = Fight(game=make_game(), hero=hero, who_started=hero, fighters=[hero, m])
        self.assertFalse(fight.light)

    def test_repr(self, mock_tprint):
        fight = make_fight()
        r = repr(fight)
        self.assertIn('Схватка', r)


@patch('src.class_fight.tprint')
class TestCreateQueue(unittest.TestCase):
    def test_who_started_is_first(self, mock_tprint):
        fight = make_fight()
        self.assertEqual(fight.queue[0], fight.hero)

    def test_queue_order_by_initiative(self, mock_tprint):
        hero = make_hero(initiative=1)
        m1 = make_goblin('Fast', initiative=10)
        m2 = make_goblin('Slow', initiative=2)
        fight = Fight(game=make_game(), hero=hero, who_started=hero, fighters=[hero, m1, m2])
        self.assertEqual(fight.queue[0], hero)
        self.assertEqual(fight.queue[1], m1)
        self.assertEqual(fight.queue[2], m2)

    def test_monster_started_is_first(self, mock_tprint):
        hero = make_hero(initiative=1)
        m1 = make_goblin('Boss', initiative=10)
        fight = Fight(game=make_game(), hero=hero, who_started=m1, fighters=[hero, m1])
        self.assertEqual(fight.queue[0], m1)

    def test_replaces_fighters_list(self, mock_tprint):
        fight = make_fight()
        self.assertIsInstance(fight.fighters, list)


@patch('src.class_fight.tprint')
class TestCheckHeroInFight(unittest.TestCase):
    def test_hero_in_fight(self, mock_tprint):
        fight = make_fight()
        self.assertTrue(fight.hero_in_fight)

    def test_no_hero(self, mock_tprint):
        fight = make_fight_no_hero()
        self.assertFalse(fight.hero_in_fight)


@patch('src.class_fight.tprint')
class TestTprint(unittest.TestCase):
    def test_with_hero_calls_tprint(self, mock_tprint):
        fight = make_fight()
        fight.tprint('hello')
        mock_tprint.assert_called_once()

    @patch('src.class_fight.cprint')
    def test_without_hero_calls_cprint(self, mock_cprint, mock_tprint):
        fight = make_fight_no_hero()
        fight.tprint('hello')
        mock_cprint.assert_called_once()


@patch('src.class_fight.tprint')
class TestShowSides(unittest.TestCase):
    def test_shows_all_fighters(self, mock_tprint):
        fight = make_fight()
        fight.show_sides()
        mock_tprint.assert_called()


@patch('src.class_fight.tprint')
class TestToEndOfQueue(unittest.TestCase):
    def test_moves_to_end(self, mock_tprint):
        fight = make_fight()
        first = fight.queue[0]
        fight.to_the_end_of_the_queue(first)
        self.assertEqual(fight.queue[-1], first)
        self.assertNotEqual(fight.queue[0], first)


@patch('src.class_fight.tprint')
class TestGetTargets(unittest.TestCase):
    def test_returns_all_except_who(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin(), make_orc()])
        targets = fight.get_targets(fight.hero)
        self.assertEqual(len(targets), 2)
        self.assertNotIn(fight.hero, targets)

    def test_excludes_self(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin()])
        monster = fight.fighters[1]
        targets = fight.get_targets(monster)
        self.assertNotIn(monster, targets)
        self.assertIn(fight.hero, targets)


@patch('src.class_fight.tprint')
class TestGetTargetsByClass(unittest.TestCase):
    def test_returns_goblins_only(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin('G1'), make_orc('O1')])
        result = fight.get_targets_by_class(['Goblin'])
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Goblin)

    def test_returns_empty(self, mock_tprint):
        fight = make_fight()
        result = fight.get_targets_by_class(['Nonexistent'])
        self.assertEqual(result, [])


@patch('src.class_fight.tprint')
class TestGetTargetsExcludeClasses(unittest.TestCase):
    def test_excludes_goblins(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin('G1'), make_orc('O1')])
        result = fight.get_targets_exclude_classes(['Goblin'])
        self.assertEqual(len(result), 2)

    def test_includes_all_when_no_match(self, mock_tprint):
        fight = make_fight()
        result = fight.get_targets_exclude_classes(['Nonexistent'])
        self.assertEqual(len(result), 2)


@patch('src.class_fight.tprint')
class TestGetFighterByStrength(unittest.TestCase):
    def test_max_default(self, mock_tprint):
        g = make_goblin('Weak', stren=3)
        o = make_orc('Strong', stren=20)
        fight = make_fight(monsters=[g, o])
        result = fight.get_fighter_by_strength()
        self.assertEqual(result, o)

    def test_min(self, mock_tprint):
        g = make_goblin('Weak', stren=3)
        o = make_orc('Strong', stren=20)
        fight = make_fight(monsters=[g, o])
        result = fight.get_fighter_by_strength(mode='Min')
        self.assertEqual(result, g)

    def test_exclude(self, mock_tprint):
        g = make_goblin('A', stren=20)
        fight = make_fight(monsters=[g])
        result = fight.get_fighter_by_strength(exclude=['Goblin'])
        self.assertEqual(result, fight.hero)

    def test_who_excluded_with_exclude(self, mock_tprint):
        g = make_goblin('A', stren=20)
        o = make_orc('B', stren=3)
        fight = make_fight(monsters=[g, o])
        who = fight.fighters[0]
        result = fight.get_fighter_by_strength(who=who, exclude=[])
        self.assertNotEqual(result, who)

    def test_empty_returns_false(self, mock_tprint):
        fight = make_fight()
        fight.fighters = []
        result = fight.get_fighter_by_strength()
        self.assertFalse(result)

    def test_invalid_mode_returns_none(self, mock_tprint):
        fight = make_fight()
        result = fight.get_fighter_by_strength(mode='Invalid')
        self.assertIsNone(result)

    def test_none_exclude_uses_all(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin(), make_orc()])
        result = fight.get_fighter_by_strength(exclude=None)
        self.assertIsNotNone(result)


@patch('src.class_fight.tprint')
class TestGetFighterByHealth(unittest.TestCase):
    def test_max_default(self, mock_tprint):
        g = make_goblin('Weak', health=5)
        o = make_orc('Strong', health=200)
        fight = make_fight(monsters=[g, o])
        result = fight.get_fighter_by_health()
        self.assertEqual(result, o)

    def test_min(self, mock_tprint):
        g = make_goblin('Weak', health=5)
        o = make_orc('Strong', health=100)
        fight = make_fight(monsters=[g, o])
        result = fight.get_fighter_by_health(mode='Min')
        self.assertEqual(result, g)

    def test_empty_returns_false(self, mock_tprint):
        fight = make_fight()
        fight.fighters = []
        result = fight.get_fighter_by_health()
        self.assertFalse(result)

    def test_invalid_mode_returns_none(self, mock_tprint):
        fight = make_fight()
        result = fight.get_fighter_by_health(mode='Invalid')
        self.assertIsNone(result)

    def test_none_exclude_uses_all(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin(), make_orc()])
        result = fight.get_fighter_by_health(exclude=None)
        self.assertIsNotNone(result)


@patch('src.class_fight.tprint')
class TestAddFighter(unittest.TestCase):
    def test_adds_to_fighters_and_queue(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin('A')])
        new_monster = make_orc('B')
        fight.add_fighter(new_monster)
        self.assertIn(new_monster, fight.fighters)
        self.assertIn(new_monster, fight.queue)

    def test_adds_to_end_of_queue(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin('A')])
        new_monster = make_orc('B')
        fight.add_fighter(new_monster)
        self.assertEqual(fight.queue[-1], new_monster)


@patch('src.class_fight.tprint')
class TestRemoveFighter(unittest.TestCase):
    def test_removes_monster(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin('Goblin'), make_orc('Orc')])
        goblin = fight.fighters[1]
        result = fight.remove_fighter(goblin)
        self.assertTrue(result)
        self.assertNotIn(goblin, fight.fighters)
        self.assertNotIn(goblin, fight.queue)

    def test_removes_hero_clears_state(self, mock_tprint):
        fight = make_fight()
        hero = fight.hero
        result = fight.remove_fighter(hero)
        self.assertTrue(result)
        self.assertIsNone(fight.hero)
        self.assertIsNone(hero.current_fight)
        self.assertEqual(hero.state, state_enum.NO_STATE)
        self.assertNotIn(hero, fight.fighters)


@patch('src.class_fight.tprint')
class TestAccumulateExperience(unittest.TestCase):
    def test_adds_exp(self, mock_tprint):
        fight = make_fight()
        monster = make_goblin(exp=25)
        fight.accumulate_experience(monster)
        self.assertEqual(fight.exp, 25)
        fight.accumulate_experience(monster)
        self.assertEqual(fight.exp, 50)


@patch('src.class_fight.tprint')
class TestMonsterLoses(unittest.TestCase):
    def test_removes_monster_and_accumulates_exp(self, mock_tprint):
        fight = make_fight()
        monster = fight.fighters[1]
        monster.last_attacker = fight.hero
        with patch.object(Fight, 'end', create=True):
            fight.monster_loses(monster)
        self.assertNotIn(monster, fight.fighters)
        self.assertEqual(fight.exp, monster.exp)

    def test_no_exp_when_not_hero_killed(self, mock_tprint):
        fight = make_fight()
        monster = fight.fighters[1]
        monster.last_attacker = None
        with patch.object(Fight, 'end', create=True):
            fight.monster_loses(monster)
        self.assertEqual(fight.exp, 0)


@patch('src.class_fight.tprint')
class TestCheckForTheEnd(unittest.TestCase):
    def test_single_fighter_ends(self, mock_tprint):
        fight = make_fight()
        fight.fighters = [fight.hero]
        fight.queue = deque([fight.hero])
        self.assertTrue(fight.check_for_the_end())

    def test_hero_alive_continues(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin()])
        self.assertFalse(fight.check_for_the_end())

    def test_no_hero_can_fight_continues(self, mock_tprint):
        fight = make_fight_no_hero()
        self.assertFalse(fight.check_for_the_end())

    def test_no_hero_no_targets_ends(self, mock_tprint):
        m1 = make_goblin('A')
        m1.choose_target = MagicMock(return_value=False)
        m2 = make_goblin('B')
        m2.choose_target = MagicMock(return_value=False)
        fight = Fight.__new__(Fight)
        fight.game = make_game()
        fight.hero = None
        fight.who_started = m1
        fight.fighters = [m1, m2]
        fight.queue = deque([m1, m2])
        self.assertTrue(fight.check_for_the_end())


@patch('src.class_fight.tprint')
class TestCheckForLosses(unittest.TestCase):
    def test_monster_dies(self, mock_tprint):
        fight = make_fight()
        monster = fight.fighters[1]
        monster.health = 0
        with patch.object(Fight, 'end', create=True):
            fight.check_for_losses()
        self.assertNotIn(monster, fight.fighters)

    def test_hero_dies(self, mock_tprint):
        fight = make_fight()
        fight.hero.health = 0
        hero = fight.hero
        with patch.object(Fight, 'end', create=True), \
             patch.object(Fight, 'monster_loses', create=True):
            fight.check_for_losses()
        self.assertIsNone(fight.hero)

    def test_multiple_deaths_safe(self, mock_tprint):
        m1 = make_goblin('A')
        m2 = make_goblin('B')
        m3 = make_orc('C')
        fight = make_fight(monsters=[m1, m2, m3])
        m1.health = 0
        m2.health = 0
        with patch.object(Fight, 'end', create=True):
            fight.check_for_losses()
        self.assertNotIn(m1, fight.fighters)
        self.assertNotIn(m2, fight.fighters)

    def test_calls_end_when_fight_over(self, mock_tprint):
        fight = make_fight()
        fight.fighters = [fight.hero]
        fight.queue = deque([fight.hero])
        with patch.object(Fight, 'end', create=True) as mock_end:
            fight.check_for_losses()
            mock_end.assert_called_once()


@patch('src.class_fight.tprint')
class TestCheckLight(unittest.TestCase):
    def test_light_from_hero(self, mock_tprint):
        fight = make_fight()
        self.assertTrue(fight.light)

    def test_no_light(self, mock_tprint):
        hero = make_hero(has_light=False)
        m = make_goblin(has_light=False)
        fight = Fight(game=make_game(), hero=hero, who_started=hero, fighters=[hero, m])
        self.assertFalse(fight.light)

    def test_light_from_monster(self, mock_tprint):
        hero = make_hero(has_light=False)
        m = make_goblin(has_light=True)
        fight = Fight(game=make_game(), hero=hero, who_started=hero, fighters=[hero, m])
        self.assertTrue(fight.light)


@patch('src.class_fight.tprint')
class TestGatherEnemies(unittest.TestCase):
    def test_adds_enemies_from_room(self, mock_tprint):
        fight = make_fight()
        new_monster = make_orc('Reinforcement')
        fight.room.monsters.return_value = [new_monster]
        fight.gather_enemies()
        self.assertIn(new_monster, fight.fighters)
        self.assertIn(new_monster, fight.queue)

    def test_does_not_add_existing_fighters(self, mock_tprint):
        fight = make_fight()
        existing = fight.fighters[1]
        fight.room.monsters.return_value = [existing]
        initial_len = len(fight.fighters)
        fight.gather_enemies()
        self.assertEqual(len(fight.fighters), initial_len)

    def test_respects_want_to_fight(self, mock_tprint):
        fight = make_fight()
        reluctant = make_orc('Reluctant')
        reluctant.want_to_fight = MagicMock(return_value=False)
        fight.room.monsters.return_value = [reluctant]
        fight.gather_enemies()
        self.assertNotIn(reluctant, fight.fighters)


@patch('src.class_fight.tprint')
class TestSequence(unittest.TestCase):
    @patch.object(Fight, 'end', create=True)
    def test_monsters_attack_before_hero(self, mock_end, mock_tprint):
        g = make_goblin('Goblin', initiative=5)
        g.attack = MagicMock(return_value=['attack msg'])
        hero = make_hero(initiative=1)
        m = make_goblin('Fast', initiative=10)
        m.choose_target = MagicMock(return_value=False)
        fight = Fight(game=make_game(), hero=hero, who_started=m, fighters=[hero, g, m])
        self.assertEqual(fight.queue[0], m)
        fight.sequence()
        g.attack.assert_called()

    @patch.object(Fight, 'end', create=True)
    def test_stops_when_hero_turn(self, mock_end, mock_tprint):
        fight = make_fight(monsters=[make_goblin()])
        fight.hero.attack = MagicMock(return_value=['hero atk'])
        fight.sequence()
        fight.hero.attack.assert_not_called()

    @patch.object(Fight, 'end', create=True)
    def test_stops_when_fight_ends(self, mock_end, mock_tprint):
        g = make_goblin('Goblin', health=0)
        g.choose_target = MagicMock(return_value=False)
        fight = make_fight(monsters=[g])
        fight.sequence()


@patch('src.class_fight.tprint')
class TestStart(unittest.TestCase):
    @patch.object(Fight, 'sequence')
    def test_sets_hero_state(self, mock_seq, mock_tprint):
        fight = make_fight()
        fight.start()
        self.assertEqual(fight.hero.state, state_enum.FIGHT)
        self.assertEqual(fight.hero.current_fight, fight)

    @patch.object(Fight, 'sequence')
    def test_gathers_enemies(self, mock_seq, mock_tprint):
        fight = make_fight()
        new_monster = make_orc('Reinforcement')
        fight.room.monsters.return_value = [new_monster]
        fight.start()
        self.assertIn(new_monster, fight.fighters)


@patch('src.class_fight.tprint')
class TestContinueAfterHero(unittest.TestCase):
    @patch.object(Fight, 'sequence')
    def test_hero_moved_to_end(self, mock_seq, mock_tprint):
        fight = make_fight()
        hero = fight.hero
        initial_pos = fight.queue[0]
        fight.continue_after_hero()
        self.assertEqual(fight.queue[-1], hero)


@patch('src.class_fight.tprint')
class TestGetFighterByHealthWithExclude(unittest.TestCase):
    def test_exclude_filters(self, mock_tprint):
        g = make_goblin('Weak', health=5)
        o = make_orc('Strong', health=200)
        fight = make_fight(monsters=[g, o])
        result = fight.get_fighter_by_health(exclude=['Goblin'])
        self.assertEqual(result, o)

    def test_exclude_all_returns_false(self, mock_tprint):
        fight = make_fight(monsters=[make_goblin()])
        result = fight.get_fighter_by_health(exclude=['MockFighter', 'Goblin'])
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
