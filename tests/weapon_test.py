import unittest
from unittest.mock import MagicMock, patch

from src.class_dice import Dice
from src.class_weapon import Weapon, Torch
from src.controllers.controller_weapon import WeaponController


def make_game():
    game = MagicMock()
    game.player = MagicMock()
    game.no_weapon = MagicMock()
    game.no_weapon.empty = True
    game.no_shield = MagicMock()
    game.no_shield.empty = True
    return game


def make_lexemes(base='меч'):
    return {
        'nom': base,
        'accus': base,
        'gen': base + 'а',
        'dat': base + 'у',
        'prep': base + 'е',
        'inst': base + 'ом',
    }


def make_weapon(game=None, **kwargs):
    if game is None:
        game = make_game()
    weapon = Weapon(game)
    weapon.weapon_type = kwargs.get('weapon_type', 'рубящее')
    weapon.gender = kwargs.get('gender', 0)
    weapon.name = kwargs.get('name', 'Меч')
    weapon.twohanded = kwargs.get('twohanded', False)
    weapon.enchantable = kwargs.get('enchantable', True)
    weapon.fencing = kwargs.get('fencing', True)
    weapon.empty = kwargs.get('empty', False)
    weapon.lexemes = kwargs.get('lexemes', make_lexemes(kwargs.get('base', 'меч')))
    weapon.damage = kwargs.get('damage', Dice([8]))
    weapon.hit_chance = kwargs.get('hit_chance', Dice([5]))
    weapon.runes = kwargs.get('runes', [])
    return weapon


def make_torch(game=None, **kwargs):
    if game is None:
        game = make_game()
    torch = Torch(game)
    torch.name = kwargs.get('name', 'Факел')
    torch.weapon_type = kwargs.get('weapon_type', 'ударное')
    torch.damage = kwargs.get('damage', Dice([6]))
    torch.hit_chance = kwargs.get('hit_chance', Dice([4]))
    torch.enchantable = kwargs.get('enchantable', False)
    torch.twohanded = kwargs.get('twohanded', False)
    torch.fencing = kwargs.get('fencing', False)
    torch.gender = kwargs.get('gender', 0)
    torch.empty = kwargs.get('empty', False)
    torch.lexemes = kwargs.get('lexemes', make_lexemes(kwargs.get('base', 'факел')))
    torch.runes = []
    torch.burning = kwargs.get('burning', False)
    return torch


def make_rune(element=1, damage=2, poison=False):
    rune = MagicMock()
    rune.element = element
    rune.damage = damage
    rune.poison = poison
    return rune


class FakeHero:
    """Герой с поддержкой форматирования падежей через lexemes."""

    def __init__(self, name='Герой', gender=0):
        self.name = name
        self.gender = gender
        self.lexemes = {
            'nom': 'герой',
            'accus': 'героя',
            'gen': 'героя',
            'dat': 'герою',
            'prep': 'герое',
            'inst': 'героем',
            'pronoun': 'он',
        }

    def __format__(self, fmt):
        return self.lexemes.get(fmt, '')

    def g(self, male, female):
        return male if self.gender == 0 else female


class HeroStub(FakeHero):
    """Герой для тестов: поддерживает форматирование и имеет MagicMock-атрибуты."""

    def __init__(self, game=None, name='Герой', gender=0):
        super().__init__(name=name, gender=gender)
        if game is None:
            game = make_game()
        self.game = game
        self.current_position = MagicMock()
        self.action_controller = MagicMock()
        self.backpack = MagicMock()
        self.weapon = game.no_weapon
        self.shield = game.no_shield
        self.removed_shield = game.no_shield
        self.get_second_weapon = MagicMock()
        self.check_light = MagicMock()


def make_hero(game=None, name='Герой', gender=0):
    return HeroStub(game=game, name=name, gender=gender)


class TestWeaponCheckName(unittest.TestCase):

    def setUp(self):
        self.mock_game = MagicMock()
        self.controller = WeaponController(self.mock_game)
        self.weapon = self.controller.get_random_object_by_filters()
        self.weapon.lexemes = {
            'nom': 'меч',
            'accus': 'меча'
        }
        self.weapon.empty = False

    def test_check_name_weapon_empty(self):
        self.weapon.empty = True
        self.assertFalse(self.weapon.check_name('меч'))

    def test_check_name_message_matches(self):
        self.assertTrue(self.weapon.check_name('меч'))
        self.assertTrue(self.weapon.check_name('меча'))

    def test_check_name_message_does_not_match(self):
        self.assertFalse(self.weapon.check_name('лук'))

    def test_check_name_case_insensitivity(self):
        self.assertTrue(self.weapon.check_name('МЕЧ'))
        self.assertTrue(self.weapon.check_name('МЕЧА'))

    def test_check_name_substring(self):
        self.assertTrue(self.weapon.check_name('ме'))
        self.assertFalse(self.weapon.check_name('мю'))


class TestWeaponCheckNameWithRunes(unittest.TestCase):
    """Проверка распознавания имени оружия с рунами (декоратор элемента)."""

    def test_check_name_with_element(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        self.assertTrue(weapon.check_name('меч'))
        self.assertTrue(weapon.check_name('огня'))

    def test_check_name_not_matching_element(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        self.assertFalse(weapon.check_name('медведь'))


class TestWeaponAttack(unittest.TestCase):

    def setUp(self):
        self.mock_game = MagicMock()
        self.controller = WeaponController(self.mock_game)
        self.weapon = self.controller.get_random_object_by_filters()
        self.weapon.damage.set_dice([6])
        self.weapon.damage.set_modifier(0)
        self.mock_monster = MagicMock()

    def attack_with_coefficient(self, coefficient, base_damage):
        self.weapon.damage.roll = lambda: base_damage
        self.mock_monster.get_weakness.return_value = coefficient
        return self.weapon.attack(self.mock_monster)

    def test_attack_with_no_weakness(self):
        self.mock_monster.get_weakness.return_value = 1
        damage = self.weapon.attack(self.mock_monster)
        self.assertIn(damage, [1, 2, 3, 4, 5, 6])

    def test_attack_multiplies_base_damage(self):
        damage = self.attack_with_coefficient(1.1, 10)
        self.assertEqual(damage, 11)

    def test_attack_resistance_reduces_damage(self):
        damage = self.attack_with_coefficient(0.3, 10)
        self.assertEqual(damage, 3)

    def test_attack_rounds_down_when_fraction_below_half(self):
        damage = self.attack_with_coefficient(1.2, 7)
        self.assertEqual(damage, 8)

    def test_attack_rounds_up_when_fraction_is_half(self):
        damage = self.attack_with_coefficient(1.25, 6)
        self.assertEqual(damage, 8)

    def test_attack_rounds_half_up_not_bankers(self):
        damage = self.attack_with_coefficient(0.25, 10)
        self.assertEqual(damage, 3)

    def test_attack_rounds_up_when_fraction_above_half(self):
        damage = self.attack_with_coefficient(1.19, 10)
        self.assertEqual(damage, 12)


class TestWeaponExamineAndFormat(unittest.TestCase):

    def test_examine_returns_show(self):
        weapon = make_weapon(name='Копье', weapon_type='колющее', damage=Dice([8]))
        result = weapon.examine(None)
        self.assertIn('Копье', result)

    def test_format_known_case(self):
        weapon = make_weapon(base='меч')
        self.assertEqual(f'{weapon:accus}', 'меч')
        self.assertEqual(f'{weapon:nom}', 'меч')

    def test_format_unknown_case(self):
        weapon = make_weapon(base='меч')
        self.assertEqual(f'{weapon:zzz}', '')

    def test_show_for_examine_hero(self):
        weapon = make_weapon()
        hero = make_hero()
        result = weapon.show_for_examine_hero(hero)
        self.assertEqual(result, 'Меч (в руках у героя)')

    def test_show_for_examine_room(self):
        weapon = make_weapon()
        hero = make_hero()
        result = weapon.show_for_examine_room(hero)
        self.assertEqual(result, 'Меч (лежит в комнате)')

    def test_on_create_returns_true(self):
        weapon = make_weapon()
        self.assertTrue(weapon.on_create())

    def test_get_hit_chance(self):
        weapon = make_weapon(hit_chance=Dice([7]))
        value = weapon.get_hit_chance()
        self.assertGreaterEqual(value, 1)
        self.assertLessEqual(value, 7)


class TestWeaponStrShow(unittest.TestCase):

    def test_str_no_runes(self):
        weapon = make_weapon(name='Топор', damage=Dice([9]))
        self.assertEqual(str(weapon), 'Топор (d9)')

    def test_str_with_element(self):
        weapon = make_weapon(name='Меч', damage=Dice([8]), runes=[make_rune(element=1)])
        self.assertEqual(str(weapon), 'Меч огня (d8)')

    def test_show(self):
        weapon = make_weapon(name='Топор', weapon_type='рубящее', damage=Dice([9]))
        self.assertEqual(weapon.show(), 'Топор (d9), рубящее')


class TestWeaponNameForChange(unittest.TestCase):

    def test_with_second_weapon(self):
        weapon = make_weapon(name='Меч', damage=Dice([8]))
        second = make_weapon(name='Копье', weapon_type='колющее', damage=Dice([8]))
        hero = make_hero()
        hero.get_second_weapon.return_value = second
        result = weapon.name_for_change(hero)
        self.assertIn('Меч', result)
        self.assertIn('Копье', result)

    def test_without_second_weapon(self):
        weapon = make_weapon(name='Меч', damage=Dice([8]))
        hero = make_hero()
        hero.get_second_weapon.return_value = hero.game.no_weapon
        result = weapon.name_for_change(hero)
        self.assertIn('Меч', result)
        self.assertNotIn('меняется', result)


class TestWeaponChange(unittest.TestCase):

    def test_cannot_change_only_one_weapon(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero()
        hero.weapon = weapon
        hero.get_second_weapon.return_value = hero.game.no_weapon
        result = weapon.change(hero)
        self.assertIn('не может сменить', result)

    def test_change_female_message(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero(name='Героиня', gender=1)
        hero.weapon = weapon
        hero.get_second_weapon.return_value = hero.game.no_weapon
        result = weapon.change(hero)
        self.assertIn('нее', result)

    def test_change_to_twohanded_with_shield(self):
        weapon = make_weapon(name='Меч')
        second = make_weapon(name='Секира', weapon_type='рубящее', twohanded=True, base='секира')
        hero = make_hero()
        hero.weapon = weapon
        hero.backpack.remove = MagicMock()
        hero.get_second_weapon.return_value = second
        shield = MagicMock()
        shield.empty = False
        hero.shield = shield
        hero.removed_shield = hero.game.no_shield
        result = weapon.change(hero)
        self.assertIs(hero.removed_shield, shield)
        self.assertIs(hero.shield, hero.game.no_shield)
        self.assertIn('двуручное оружие', result[1])
        hero.backpack.remove.assert_called_once_with(second, hero)
        hero.backpack.add.assert_called_once_with(weapon)
        self.assertIs(hero.weapon, second)

    def test_change_to_onehanded_restores_shield(self):
        weapon = make_weapon(name='Секира', twohanded=True)
        second = make_weapon(name='Меч', base='меч')
        hero = make_hero()
        hero.weapon = weapon
        hero.backpack.remove = MagicMock()
        hero.get_second_weapon.return_value = second
        removed_shield = MagicMock()
        removed_shield.empty = False
        hero.removed_shield = removed_shield
        hero.shield = hero.game.no_shield
        result = weapon.change(hero)
        self.assertIn('одноручное оружие', result[1])
        self.assertIs(hero.weapon, second)
        hero.backpack.add.assert_called_once_with(weapon)

    def test_change_plain(self):
        weapon = make_weapon(name='Меч')
        second = make_weapon(name='Копье', weapon_type='колющее', base='копье')
        hero = make_hero()
        hero.weapon = weapon
        hero.backpack.remove = MagicMock()
        hero.get_second_weapon.return_value = second
        hero.shield = hero.game.no_shield
        hero.removed_shield = hero.game.no_shield
        result = weapon.change(hero)
        self.assertIn('берет в руки', result[0])
        self.assertIs(hero.weapon, second)
        self.assertEqual(len(result), 1)


class TestWeaponPlaceIntoBackpack(unittest.TestCase):

    def test_place_into_backpack(self):
        weapon = make_weapon()
        hero = make_hero()
        weapon.place_into_backpack(hero)
        hero.backpack.add.assert_called_once_with(weapon)


class TestWeaponGetFullNames(unittest.TestCase):

    def test_no_element_no_key_returns_lexemes(self):
        weapon = make_weapon()
        result = weapon.get_full_names()
        self.assertEqual(result, weapon.lexemes)

    def test_no_element_with_key(self):
        weapon = make_weapon()
        self.assertEqual(weapon.get_full_names('nom'), 'меч')

    def test_no_element_with_unknown_key(self):
        weapon = make_weapon()
        self.assertEqual(weapon.get_full_names('zzz'), '')

    def test_with_element_and_key(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        result = weapon.get_full_names('nom')
        self.assertIn('меч', result)
        self.assertIn('огня', result)

    def test_with_element_without_key(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        result = weapon.get_full_names()
        self.assertIsInstance(result, dict)
        for case in result:
            self.assertIn(weapon.lexemes[case], result[case])


class TestWeaponDrop(unittest.TestCase):

    def test_drop_when_equipped(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero()
        hero.weapon = weapon
        result = weapon.drop(hero)
        self.assertIs(hero.weapon, weapon.game.no_weapon)
        hero.current_position.loot.add.assert_called_once_with(weapon)
        hero.current_position.action_controller.add_actions.assert_called_once_with(weapon)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(weapon)
        self.assertIn('Меч', result)

    def test_drop_when_not_equipped(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero()
        other = make_weapon(name='Копье')
        hero.weapon = other
        weapon.drop(hero)
        self.assertIs(hero.weapon, other)
        hero.current_position.loot.add.assert_called_once_with(weapon)


class TestWeaponElements(unittest.TestCase):

    def test_get_element_decorator_known(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        self.assertEqual(weapon.get_element_decorator(), 'огня')

    def test_get_element_decorator_unknown(self):
        weapon = make_weapon(runes=[make_rune(element=999)])
        self.assertIsNone(weapon.get_element_decorator())

    def test_element_no_runes(self):
        weapon = make_weapon()
        self.assertEqual(weapon.element(), 0)

    def test_element_sum(self):
        weapon = make_weapon(runes=[make_rune(element=1), make_rune(element=3)])
        self.assertEqual(weapon.element(), 4)

    def test_get_element_names_no_decorator(self):
        weapon = make_weapon(runes=[make_rune(element=999)])
        self.assertIsNone(weapon.get_element_names('nom'))

    def test_get_element_names_with_key(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        result = weapon.get_element_names('nom')
        self.assertEqual(result, 'меч огня')

    def test_get_element_names_without_key(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        result = weapon.get_element_names()
        self.assertEqual(result['nom'], 'меч огня')

    def test_get_element_names_unknown_key(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        self.assertEqual(weapon.get_element_names('zzz'), '')

    def test_get_poison_level_zero(self):
        weapon = make_weapon(runes=[make_rune(element=1, poison=False)])
        self.assertEqual(weapon.get_poison_level(), 0)

    def test_get_poison_level_count(self):
        weapon = make_weapon(runes=[
            make_rune(element=1, poison=True),
            make_rune(element=3, poison=False),
            make_rune(element=2, poison=True),
        ])
        self.assertEqual(weapon.get_poison_level(), 2)


class TestWeaponEnchant(unittest.TestCase):

    def test_can_be_enchanted_true(self):
        weapon = make_weapon(enchantable=True)
        self.assertTrue(weapon.can_be_enchanted())

    def test_can_be_enchanted_many_runes(self):
        weapon = make_weapon(runes=[make_rune(), make_rune()])
        self.assertFalse(weapon.can_be_enchanted())

    def test_can_be_enchanted_empty_weapon(self):
        weapon = make_weapon(empty=True)
        self.assertFalse(weapon.can_be_enchanted())

    def test_can_be_enchanted_not_enchantable(self):
        weapon = make_weapon(enchantable=False)
        self.assertFalse(weapon.can_be_enchanted())

    def test_enchant_success(self):
        weapon = make_weapon(damage=Dice([8]))
        rune = make_rune(element=1, damage=2)
        result = weapon.enchant(rune)
        self.assertTrue(result)
        self.assertIn(rune, weapon.runes)
        self.assertEqual(weapon.damage.modifier, 2)

    def test_enchant_failure(self):
        weapon = make_weapon(enchantable=False)
        rune = make_rune()
        self.assertFalse(weapon.enchant(rune))
        self.assertEqual(weapon.runes, [])


class TestWeaponEnchantment(unittest.TestCase):

    def test_no_runes_empty(self):
        weapon = make_weapon()
        self.assertEqual(weapon.enchantment(), '')

    def test_three_runes_empty(self):
        weapon = make_weapon(runes=[make_rune(), make_rune(), make_rune()])
        self.assertEqual(weapon.enchantment(), '')

    def test_one_rune(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        self.assertEqual(weapon.enchantment(), ' огня')

    def test_two_runes(self):
        weapon = make_weapon(runes=[make_rune(element=1), make_rune(element=2)])
        self.assertEqual(weapon.enchantment(), ' воздуха')


class TestWeaponNamesList(unittest.TestCase):

    def test_base_names(self):
        weapon = make_weapon()
        names = weapon.get_names_list(['nom', 'accus'])
        self.assertIn('оружие', names)
        self.assertIn('меч', names)

    def test_element_names(self):
        weapon = make_weapon(runes=[make_rune(element=1)])
        names = weapon.get_names_list(['nom'])
        self.assertIn('меч огня', names)

    def test_unknown_case(self):
        weapon = make_weapon()
        names = weapon.get_names_list(['zzz'])
        self.assertIn('', names)


class TestWeaponTake(unittest.TestCase):

    def test_take_empty_hands(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        hero.get_second_weapon.return_value = hero.game.no_weapon
        result = weapon.take(hero)
        self.assertIs(hero.weapon, weapon)
        self.assertIn('теперь использует', result[1])
        hero.action_controller.add_actions.assert_called_once_with(weapon)
        hero.current_position.action_controller.delete_actions_by_item.assert_called_once_with(weapon)

    def test_take_twohanded_with_shield(self):
        weapon = make_weapon(name='Секира', weapon_type='рубящее', twohanded=True, base='секира')
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        hero.get_second_weapon.return_value = hero.game.no_weapon
        shield = MagicMock()
        shield.empty = False
        hero.shield = shield
        hero.removed_shield = MagicMock()
        hero.removed_shield.get_full_names.return_value = 'щит'
        result = weapon.take(hero)
        self.assertIs(hero.weapon, weapon)
        shield.take_away.assert_called_once_with(hero)
        self.assertIn('двуручное оружие', result[2])

    def test_take_when_hands_full_and_second_exists(self):
        weapon = make_weapon(name='Копье', weapon_type='колющее', base='копье')
        hero = make_hero()
        old = make_weapon(name='Меч')
        hero.weapon = old
        hero.get_second_weapon.return_value = make_weapon(name='Топор', base='топор')
        old.drop = MagicMock()
        result = weapon.take(hero)
        self.assertIn('бросить Меч', result[1])
        old.drop.assert_called_once_with(hero)
        self.assertIs(hero.weapon, weapon)

    def test_take_when_hands_full_no_second(self):
        weapon = make_weapon(name='Копье', weapon_type='колющее', base='копье')
        hero = make_hero()
        hero.weapon = make_weapon(name='Меч')
        hero.get_second_weapon.return_value = hero.game.no_weapon
        result = weapon.take(hero)
        self.assertIn('второго оружия', result[1])
        hero.backpack.add.assert_called_once_with(weapon)


class TestWeaponUse(unittest.TestCase):

    def test_use_already_in_hands(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero()
        hero.weapon = weapon
        result = weapon.use(hero)
        self.assertIn('уже использует', result[0])

    def test_use_switch_weapons(self):
        weapon = make_weapon(name='Копье', base='копье')
        hero = make_hero()
        old = make_weapon(name='Меч')
        hero.weapon = old
        hero.backpack.add = MagicMock()
        hero.backpack.remove = MagicMock()
        result = weapon.use(hero)
        hero.backpack.add.assert_called_once_with(old)
        hero.backpack.remove.assert_called_once_with(weapon, hero)
        self.assertIs(hero.weapon, weapon)
        self.assertIn('теперь использует', result[0])

    def test_use_empty_hands(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero()
        hero.weapon = hero.game.no_weapon
        result = weapon.use(hero)
        self.assertIs(hero.weapon, weapon)
        self.assertIn('теперь использует', result[0])

    def test_use_twohanded_removes_shield(self):
        weapon = make_weapon(name='Секира', twohanded=True, base='секира')
        hero = make_hero(game=weapon.game)
        hero.weapon = hero.game.no_weapon
        shield = MagicMock()
        shield.empty = False
        hero.shield = shield
        hero.removed_shield = hero.game.no_shield
        result = weapon.use(hero)
        self.assertIs(hero.removed_shield, shield)
        self.assertIs(hero.shield, hero.game.no_shield)
        self.assertIn('двуручное', result[1])

    def test_use_onehanded_restores_shield(self):
        weapon = make_weapon(name='Меч')
        hero = make_hero(game=weapon.game)
        hero.weapon = hero.game.no_weapon
        shield = MagicMock()
        shield.empty = False
        shield.get_full_names.return_value = 'щит'
        hero.removed_shield = shield
        hero.shield = hero.game.no_shield
        result = weapon.use(hero)
        self.assertIs(hero.shield, shield)
        self.assertIs(hero.removed_shield, hero.game.no_shield)
        self.assertIn('щит', result[1])


class TestWeaponPlace(unittest.TestCase):

    def test_place_with_explicit_place(self):
        weapon = make_weapon()
        floor = MagicMock()
        place = MagicMock()
        place.action_controller = MagicMock()
        result = weapon.place(floor, place=place)
        place.add.assert_called_once_with(weapon)
        place.action_controller.add_actions.assert_called_once_with(weapon)
        self.assertTrue(result)

    def test_place_taken_by_monster(self):
        weapon = make_weapon()
        floor = MagicMock()
        room = MagicMock()
        monster = MagicMock()
        monster.carry_weapon = True
        room.monsters.return_value = monster
        floor.plan = [room]
        with patch('src.class_weapon.randomitem', return_value=room):
            result = weapon.place(floor)
        monster.take.assert_called_once_with(weapon)
        self.assertTrue(result)

    def test_place_in_furniture(self):
        weapon = make_weapon()
        floor = MagicMock()
        room = MagicMock()
        monster = MagicMock()
        monster.carry_weapon = False
        room.monsters.return_value = monster
        furniture = MagicMock()
        furniture.can_contain_weapon = True
        room.furniture = [furniture]
        floor.plan = [room]
        with patch('src.class_weapon.randomitem', side_effect=[room, furniture]):
            result = weapon.place(floor)
        furniture.add.assert_called_once_with(weapon)
        self.assertTrue(result)

    def test_place_in_room_loot_no_furniture(self):
        weapon = make_weapon()
        floor = MagicMock()
        room = MagicMock()
        room.monsters.return_value = None
        room.furniture = []
        floor.plan = [room]
        with patch('src.class_weapon.randomitem', return_value=room):
            result = weapon.place(floor)
        room.add.assert_called_once_with(weapon)
        self.assertTrue(result)

    def test_place_furniture_none_can_contain(self):
        weapon = make_weapon()
        floor = MagicMock()
        room = MagicMock()
        room.monsters.return_value = None
        furniture = MagicMock()
        furniture.can_contain_weapon = False
        room.furniture = [furniture]
        floor.plan = [room]
        with patch('src.class_weapon.randomitem', return_value=room):
            result = weapon.place(floor)
        room.add.assert_called_once_with(weapon)
        self.assertTrue(result)

    def test_place_no_action_controller(self):
        weapon = make_weapon()
        floor = MagicMock()
        room = MagicMock(spec=['add', 'monsters', 'furniture'])
        room.add = MagicMock()
        room.monsters.return_value = None
        room.furniture = []
        floor.plan = [room]
        with patch('src.class_weapon.randomitem', return_value=room):
            result = weapon.place(floor)
        room.add.assert_called_once_with(weapon)
        self.assertTrue(result)


class TestTorchInit(unittest.TestCase):

    def test_init_sets_burning_false(self):
        torch = make_torch()
        self.assertFalse(torch.burning)

    def test_init_hero_actions(self):
        torch = make_torch()
        for key in ('поджечь', 'зажечь', 'потушить'):
            self.assertIn(key, torch.hero_actions)

    def test_init_room_actions(self):
        torch = make_torch()
        for key in ('поджечь', 'зажечь', 'потушить'):
            self.assertIn(key, torch.room_actions)

    def test_init_base_weapon_actions_preserved(self):
        torch = make_torch()
        for key in ('сменить', 'осмотреть', 'бросить', 'использовать'):
            self.assertIn(key, torch.hero_actions)
        self.assertIn('взять', torch.room_actions)

    def test_init_fire_methods(self):
        torch = make_torch()
        self.assertEqual(torch.hero_actions['поджечь']['method'], 'fire')
        self.assertEqual(torch.hero_actions['потушить']['method'], 'extinguish')
        self.assertEqual(torch.room_actions['поджечь']['method'], 'fire_in_room')
        self.assertEqual(torch.room_actions['потушить']['method'], 'extinguish_in_room')

    def test_init_conditions(self):
        torch = make_torch()
        self.assertEqual(torch.hero_actions['поджечь']['condition'], 'is_not_burning')
        self.assertEqual(torch.hero_actions['потушить']['condition'], 'is_burning')
        self.assertEqual(torch.room_actions['поджечь']['condition'], 'is_not_burning')
        self.assertEqual(torch.room_actions['потушить']['condition'], 'is_burning')


class TestTorchExtinguish(unittest.TestCase):

    def test_extinguish_light_still(self):
        torch = make_torch(burning=True)
        hero = make_hero()
        hero.check_light.return_value = True
        result = torch.extinguish(hero)
        self.assertFalse(torch.burning)
        self.assertIn('тушит', result)
        self.assertIn('держит в руке', result)

    def test_extinguish_room_dark(self):
        torch = make_torch(burning=True)
        hero = make_hero()
        hero.check_light.return_value = False
        result = torch.extinguish(hero)
        self.assertFalse(torch.burning)
        self.assertIn('тьму', result)

    def test_extinguish_in_room_light_still(self):
        torch = make_torch(burning=True)
        hero = make_hero()
        hero.check_light.return_value = True
        result = torch.extinguish_in_room(hero)
        self.assertFalse(torch.burning)
        self.assertIn('освещает комнату', result)
        self.assertNotIn('тьму', result)

    def test_extinguish_in_room_dark(self):
        torch = make_torch(burning=True)
        hero = make_hero()
        hero.check_light.return_value = False
        result = torch.extinguish_in_room(hero)
        self.assertFalse(torch.burning)
        self.assertIn('тьму', result)


class TestTorchFire(unittest.TestCase):

    def test_fire_with_matches(self):
        torch = make_torch()
        hero = make_hero()
        matches = MagicMock()
        matches.quantity = 1
        hero.backpack.get_first_item_by_class.return_value = matches
        result = torch.fire(hero)
        matches.use_one.assert_called_once_with()
        self.assertTrue(torch.burning)
        self.assertIn('спичками', result)

    def test_fire_without_matches(self):
        torch = make_torch()
        hero = make_hero()
        hero.backpack.get_first_item_by_class.return_value = None
        result = torch.fire(hero)
        self.assertFalse(torch.burning)
        self.assertIn('не может поджечь', result)

    def test_fire_in_room_with_matches(self):
        torch = make_torch()
        hero = make_hero()
        matches = MagicMock()
        matches.quantity = 3
        hero.backpack.get_first_item_by_class.return_value = matches
        result = torch.fire_in_room(hero)
        matches.use_one.assert_called_once_with()
        self.assertTrue(torch.burning)
        hero.current_position.light = True
        self.assertIn('озаряется', result)

    def test_fire_in_room_without_matches(self):
        torch = make_torch()
        hero = make_hero()
        hero.backpack.get_first_item_by_class.return_value = None
        result = torch.fire_in_room(hero)
        self.assertFalse(torch.burning)
        self.assertIn('не может поджечь', result)


class TestTorchState(unittest.TestCase):

    def test_is_not_burning_when_cold(self):
        torch = make_torch(burning=False)
        self.assertTrue(torch.is_not_burning())
        self.assertFalse(torch.is_burning())

    def test_is_burning_when_lit(self):
        torch = make_torch(burning=True)
        self.assertFalse(torch.is_not_burning())
        self.assertTrue(torch.is_burning())

    def test_light_sets_burning(self):
        torch = make_torch(burning=False)
        torch.light()
        self.assertTrue(torch.burning)

    def test_place_into_backpack_extinguishes(self):
        torch = make_torch(burning=True)
        hero = make_hero()
        torch.place_into_backpack(hero)
        hero.backpack.add.assert_called_once_with(torch)
        self.assertFalse(torch.burning)

    def test_element_burning(self):
        torch = make_torch(burning=True)
        self.assertEqual(torch.element(), 2)

    def test_element_not_burning(self):
        torch = make_torch(burning=False)
        self.assertEqual(torch.element(), 0)

    def test_show_burning(self):
        torch = make_torch(burning=True)
        result = torch.show()
        self.assertIn('Горящий факел', result)

    def test_show_not_burning(self):
        torch = make_torch(burning=False)
        result = torch.show()
        self.assertIn('Потухший факел', result)

    def test_show_for_examine_hero_burning(self):
        torch = make_torch(burning=True)
        who = FakeHero()
        result = torch.show_for_examine_hero(who)
        self.assertIn('горящий', result)
        self.assertIn('факел', result)

    def test_show_for_examine_hero_cold(self):
        torch = make_torch(burning=False)
        who = FakeHero()
        result = torch.show_for_examine_hero(who)
        self.assertIn('потухший', result)

    def test_show_for_examine_room_burning(self):
        torch = make_torch(burning=True)
        who = make_hero()
        result = torch.show_for_examine_room(who)
        self.assertIn('горящий', result)
        self.assertIn('находящийся в комнате', result)

    def test_show_for_examine_room_cold(self):
        torch = make_torch(burning=False)
        who = make_hero()
        result = torch.show_for_examine_room(who)
        self.assertIn('потухший', result)


class TestTorchPlace(unittest.TestCase):

    def test_place_with_explicit_room(self):
        torch = make_torch()
        floor = MagicMock()
        room = MagicMock()
        room.action_controller = MagicMock()
        result = torch.place(floor, place=room)
        self.assertIs(room.torch, torch)
        self.assertTrue(room.light)
        room.action_controller.add_actions.assert_called_once_with(torch)
        self.assertTrue(result)

    def test_place_random_room_without_torch(self):
        torch = make_torch()
        floor = MagicMock()
        room = MagicMock()
        room.torch = False
        floor.plan = [room]
        with patch('src.class_weapon.randomitem', return_value=room):
            result = torch.place(floor)
        self.assertIs(room.torch, torch)
        self.assertTrue(room.light)
        self.assertTrue(result)

    def test_place_no_room_returns_false(self):
        torch = make_torch()
        floor = MagicMock()
        floor.plan = []
        with patch('src.class_weapon.randomitem', return_value=None):
            result = torch.place(floor)
        self.assertFalse(result)


class TestWeaponControllerInit(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.controller = WeaponController(self.game)

    def test_controller_game(self):
        self.assertIs(self.controller.game, self.game)

    def test_controller_how_many_starts_zero(self):
        self.assertEqual(self.controller.how_many, 0)

    def test_controller_all_objects_empty(self):
        self.assertEqual(self.controller.all_objects, [])

    def test_controller_templates_loaded(self):
        self.assertGreater(len(self.controller.templates), 0)

    def test_controller_classes_has_torch(self):
        self.assertIs(WeaponController._classes['Torch'], Torch)


class TestWeaponControllerDecorate(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.controller = WeaponController(self.game)

    def test_decorate_no_decorators_for_type(self):
        weapon = make_weapon(weapon_type='неизвестный тип')
        with patch('src.controllers.controller_weapon.randomitem', return_value=None):
            result = self.controller.decorate(weapon)
        self.assertFalse(result)

    def test_decorate_missing_gender(self):
        weapon = make_weapon(gender=5)
        with patch('src.controllers.controller_weapon.randomitem',
                   return_value={'damage_modifier': 1}):
            result = self.controller.decorate(weapon)
        self.assertFalse(result)

    def test_decorate_success(self):
        weapon = make_weapon(gender=0, damage=Dice([8]))
        decorator = {
            'damage_modifier': 1,
            0: {'nom': 'Большой', 'accus': 'Большой', 'gen': 'Большого',
                'dat': 'Большому', 'prep': 'Большом', 'inst': 'Большим'},
        }
        with patch('src.controllers.controller_weapon.randomitem',
                   return_value=decorator):
            result = self.controller.decorate(weapon)
        self.assertTrue(result)
        self.assertEqual(weapon.lexemes['nom'], 'Большой меч')
        self.assertEqual(weapon.damage.modifier, 1)

    def test_decorate_negative_modifier(self):
        weapon = make_weapon(gender=0, damage=Dice([8]))
        decorator = {
            'damage_modifier': -1,
            0: {'nom': 'Малый', 'accus': 'Малый', 'gen': 'Малого',
                'dat': 'Малому', 'prep': 'Малом', 'inst': 'Малым'},
        }
        with patch('src.controllers.controller_weapon.randomitem',
                   return_value=decorator):
            result = self.controller.decorate(weapon)
        self.assertTrue(result)
        self.assertEqual(weapon.lexemes['nom'], 'Малый меч')
        self.assertEqual(weapon.damage.modifier, -1)

    def test_additional_actions_for_weapon_decorates(self):
        weapon = make_weapon()
        with patch.object(self.controller, 'decorate', return_value=True) as mock_decorate:
            result = self.controller.additional_actions(weapon)
        self.assertTrue(result)
        mock_decorate.assert_called_once_with(weapon)

    def test_additional_actions_for_torch_skips(self):
        torch = make_torch()
        with patch.object(self.controller, 'decorate', return_value=True) as mock_decorate:
            result = self.controller.additional_actions(torch)
        self.assertTrue(result)
        mock_decorate.assert_not_called()


class TestWeaponControllerGetEmpty(unittest.TestCase):

    def setUp(self):
        self.game = make_game()
        self.controller = WeaponController(self.game)

    def test_get_empty_weapon(self):
        weapon = self.controller.get_empty_object_by_class_name('Weapon')
        self.assertIsInstance(weapon, Weapon)
        self.assertTrue(weapon.empty)
        self.assertFalse(weapon.twohanded)
        self.assertFalse(weapon.fencing)
        self.assertIs(weapon.game, self.game)

    def test_get_empty_torch(self):
        torch = self.controller.get_empty_object_by_class_name('Torch')
        self.assertIsInstance(torch, Torch)
        self.assertTrue(torch.empty)

    def test_get_empty_unknown_class(self):
        with self.assertRaises(ValueError):
            self.controller.get_empty_object_by_class_name('Sword')


if __name__ == '__main__':
    unittest.main()