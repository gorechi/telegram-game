import unittest
from unittest.mock import MagicMock, patch

from src.class_protection import Protection, Armor, Shield
from src.controllers.controller_protection import ProtectionController
from src.class_dice import Dice


LEXEMES = {
    'nom': 'тестовый щит',
    'accus': 'тестовый щит',
    'gen': 'тестового щита',
    'dat': 'тестовому щиту',
    'prep': 'тестовом щите',
    'inst': 'тестовым щитом',
}

ARMOR_LEXEMES = {
    'nom': 'тестовая броня',
    'accus': 'тестовую броню',
    'gen': 'тестовой брони',
    'dat': 'тестовой броне',
    'prep': 'тестовой броне',
    'inst': 'тестовой броней',
}


def make_game():
    game = MagicMock()
    game.no_armor = MagicMock()
    game.no_armor.empty = True
    game.no_shield = MagicMock()
    game.no_shield.empty = True
    game.all_shields = []
    return game


def make_rune(element=0, poison=False):
    rune = MagicMock()
    rune.element = element
    rune.poison = poison
    return rune


def make_hero(game=None, armor_empty=True, shield_empty=True, weapon_empty=True, twohanded=False):
    game = game or make_game()
    hero = MagicMock()
    hero.name = 'Герой'
    hero.hide = False
    hero.money = 100
    hero.armor = MagicMock()
    hero.armor.empty = armor_empty
    hero.shield = MagicMock()
    hero.shield.empty = shield_empty
    hero.removed_shield = MagicMock()
    hero.removed_shield.empty = True
    hero.weapon = MagicMock()
    hero.weapon.empty = weapon_empty
    hero.weapon.twohanded = twohanded
    hero.weapon.element.return_value = 0
    hero.weapon.damage = MagicMock()
    hero.weapon.damage.base_die.return_value = 6
    hero.action_controller = MagicMock()
    hero.current_position = MagicMock()
    hero.current_position.loot = MagicMock()
    hero.current_position.light = True
    hero.current_position.action_controller = MagicMock()
    hero.game = game
    return hero


def make_armor(game=None, lexemes=None, protection_type='кованый', gender=1, enchantable=True):
    game = game or make_game()
    a = Armor(game)
    a.lexemes = lexemes or ARMOR_LEXEMES
    a.protection = Dice([4])
    a.name = 'тестовая броня'
    a.enchantable = enchantable
    a.empty = False
    a.runes = []
    a.noisy = True
    a.protection_type = protection_type
    a.gender = gender
    a.user = None
    return a


def make_shield(game=None, lexemes=None, enchantable=True, accumulated_damage=0):
    game = game or make_game()
    s = Shield(game)
    s.lexemes = lexemes or LEXEMES
    s.protection = Dice([3])
    s.name = 'тестовый щит'
    s.enchantable = enchantable
    s.empty = False
    s.runes = []
    s.noisy = True
    s.protection_type = 'щит'
    s.gender = 0
    s.accumulated_damage = accumulated_damage
    s.user = None
    return s


class TestProtectionInit(unittest.TestCase):
    def test_default_attributes(self):
        p = Protection(make_game())
        self.assertTrue(p.can_use_in_fight)
        self.assertFalse(p.empty)
        self.assertEqual(p.runes, [])
        self.assertIsNone(p.user)


class TestProtectionFormat(unittest.TestCase):
    def test_format_known_key(self):
        p = make_armor()
        self.assertEqual(p.__format__('nom'), 'тестовая броня')

    def test_format_unknown_key(self):
        p = make_armor()
        self.assertEqual(p.__format__('unknown'), '')


class TestProtectionStr(unittest.TestCase):
    def test_str_no_enchantment(self):
        a = make_armor()
        result = str(a)
        self.assertIn('тестовая броня', result)
        self.assertIn('(', result)

    def test_str_with_rune(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        result = str(a)
        self.assertIn('огня', result)


class TestProtectionShowForExamine(unittest.TestCase):
    def test_show_for_examine_hero(self):
        p = make_armor()
        result = p.show_for_examine_hero(MagicMock())
        self.assertIn('тестовая броня', result)
        self.assertIn('героя', result)

    def test_show_for_examine_room(self):
        p = make_armor()
        result = p.show_for_examine_room(MagicMock())
        self.assertIn('тестовая броня', result)
        self.assertIn('комнате', result)


class TestProtectionOnCreate(unittest.TestCase):
    def test_protection_on_create(self):
        self.assertTrue(Protection(make_game()).on_create())

    def test_armor_on_create(self):
        self.assertTrue(make_armor().on_create())

    def test_shield_on_create(self):
        self.assertTrue(make_shield().on_create())


class TestProtectionCheckName(unittest.TestCase):
    def test_match_nom(self):
        a = make_armor()
        self.assertTrue(a.check_name('тестовая броня'))

    def test_match_partial(self):
        a = make_armor()
        self.assertTrue(a.check_name('тестовая'))

    def test_no_match(self):
        a = make_armor()
        self.assertFalse(a.check_name('другой предмет'))

    def test_empty_returns_false(self):
        a = make_armor()
        a.empty = True
        self.assertFalse(a.check_name('тестовая броня'))

    def test_case_insensitive(self):
        a = make_armor()
        self.assertTrue(a.check_name('ТЕСТОВАЯ'))

    def test_shield_check_name(self):
        s = make_shield()
        self.assertTrue(s.check_name('тестовый щит'))


class TestProtectionIsPoisoned(unittest.TestCase):
    def test_no_runes(self):
        self.assertFalse(make_armor().is_poisoned())

    def test_runes_without_poison(self):
        rune = make_rune(poison=False)
        a = make_armor()
        a.runes = [rune]
        self.assertFalse(a.is_poisoned())

    def test_runes_with_poison(self):
        rune = make_rune(poison=True)
        a = make_armor()
        a.runes = [rune]
        self.assertTrue(a.is_poisoned())


class TestProtectionElement(unittest.TestCase):
    def test_no_runes(self):
        self.assertEqual(make_armor().element(), 0)

    def test_single_element(self):
        rune = make_rune(element=3)
        a = make_armor()
        a.runes = [rune]
        self.assertEqual(a.element(), 3)

    def test_multiple_elements(self):
        rune1 = make_rune(element=3)
        rune2 = make_rune(element=4)
        a = make_armor()
        a.runes = [rune1, rune2]
        self.assertEqual(a.element(), 7)


class TestProtectionCanBeEnchanted(unittest.TestCase):
    def test_can_be_enchanted(self):
        self.assertTrue(make_armor().can_be_enchanted())

    def test_already_has_two_runes(self):
        a = make_armor()
        a.runes = [make_rune(), make_rune()]
        self.assertFalse(a.can_be_enchanted())

    def test_one_rune_ok(self):
        a = make_armor()
        a.runes = [make_rune()]
        self.assertTrue(a.can_be_enchanted())

    def test_empty_item(self):
        a = make_armor()
        a.empty = True
        self.assertFalse(a.can_be_enchanted())

    def test_not_enchantable(self):
        self.assertFalse(make_armor(enchantable=False).can_be_enchanted())


class TestProtectionEnchant(unittest.TestCase):
    def test_enchant_success(self):
        a = make_armor()
        rune = make_rune(element=1)
        rune.defence = 2
        result = a.enchant(rune)
        self.assertTrue(result)
        self.assertIn(rune, a.runes)
        self.assertEqual(a.protection.modifier, 2)

    def test_enchant_fails(self):
        a = make_armor(enchantable=False)
        rune = make_rune()
        rune.defence = 1
        self.assertFalse(a.enchant(rune))
        self.assertEqual(len(a.runes), 0)


class TestProtectionEnchantment(unittest.TestCase):
    def test_no_runes(self):
        self.assertEqual(make_armor().enchantment(), '')

    def test_one_rune(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        self.assertEqual(a.enchantment(), ' огня')

    def test_two_runes(self):
        rune1 = make_rune(element=3)
        rune2 = make_rune(element=4)
        a = make_armor()
        a.runes = [rune1, rune2]
        self.assertEqual(a.enchantment(), ' земли')

    def test_three_runes(self):
        a = make_armor()
        a.runes = [make_rune(element=1) for _ in range(3)]
        self.assertEqual(a.enchantment(), '')


class TestProtectionProtect(unittest.TestCase):
    @patch('src.class_protection.dice', return_value=3)
    def test_hide_breaks(self, mock_dice):
        a = make_armor()
        hero = make_hero()
        hero.hide = True
        result = a.protect(hero, mastery=2)
        self.assertFalse(hero.hide)
        self.assertIsInstance(result, int)

    @patch('src.class_protection.dice', return_value=3)
    def test_weapon_empty(self, mock_dice):
        result = make_armor().protect(make_hero(weapon_empty=True))
        self.assertIsInstance(result, int)

    @patch('src.class_protection.dice', return_value=3)
    def test_weapon_no_element(self, mock_dice):
        hero = make_hero(weapon_empty=False)
        hero.weapon.element.return_value = 0
        result = make_armor().protect(hero)
        self.assertIsInstance(result, int)

    @patch('src.class_protection.dice', return_value=3)
    def test_protection_no_element(self, mock_dice):
        hero = make_hero(weapon_empty=False)
        hero.weapon.element.return_value = 1
        result = make_armor().protect(hero)
        self.assertIsInstance(result, int)

    @patch('src.class_protection.dice', return_value=3)
    def test_weapon_weak_to_protection(self, mock_dice):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        hero = make_hero(weapon_empty=False)
        hero.weapon.element.return_value = 3
        result = a.protect(hero, mastery=1)
        self.assertIsInstance(result, int)

    @patch('src.class_protection.dice', return_value=3)
    def test_protection_weak_to_weapon(self, mock_dice):
        rune = make_rune(element=3)
        a = make_armor()
        a.runes = [rune]
        hero = make_hero(weapon_empty=False)
        hero.weapon.element.return_value = 1
        result = a.protect(hero, mastery=1)
        self.assertIsInstance(result, int)

    @patch('src.class_protection.dice', return_value=3)
    def test_no_weakness_match(self, mock_dice):
        rune = make_rune(element=4)
        a = make_armor()
        a.runes = [rune]
        hero = make_hero(weapon_empty=False)
        hero.weapon.element.return_value = 1
        result = a.protect(hero)
        self.assertIsInstance(result, int)


class TestProtectionShow(unittest.TestCase):
    def test_empty_returns_empty(self):
        a = make_armor()
        a.empty = True
        self.assertEqual(a.show(), '')

    def test_show_without_element(self):
        result = make_armor().show()
        self.assertIn('тестовая броня', result)

    def test_show_with_element(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        result = a.show()
        self.assertIn('огня', result)


class TestProtectionGetFullNames(unittest.TestCase):
    def test_no_element_with_key(self):
        self.assertEqual(make_armor().get_full_names('nom'), 'тестовая броня')

    def test_no_element_without_key(self):
        result = make_armor().get_full_names()
        self.assertIsInstance(result, dict)
        self.assertIn('nom', result)

    def test_with_element_with_key(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        result = a.get_full_names('nom')
        self.assertIn('огня', result)

    def test_with_element_without_key(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        result = a.get_full_names()
        self.assertIsInstance(result, dict)
        self.assertIn('nom', result)


class TestProtectionGetElementDecorator(unittest.TestCase):
    def test_no_element(self):
        self.assertIsNone(make_armor().get_element_decorator())

    def test_known_element(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        self.assertEqual(a.get_element_decorator(), 'огня')


class TestProtectionGetElementNames(unittest.TestCase):
    def test_no_element(self):
        self.assertEqual(make_armor().get_element_names(), '')

    def test_with_element_with_key(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        self.assertIn('огня', a.get_element_names('nom'))

    def test_with_element_without_key(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        self.assertIsInstance(a.get_element_names(), dict)


class TestArmorGetNamesList(unittest.TestCase):
    def test_get_names_list(self):
        a = make_armor()
        result = a.get_names_list(['nom', 'accus'])
        self.assertIn('защита', result)
        self.assertIn('защиту', result)
        self.assertIn('доспех', result)
        self.assertIn('доспехи', result)
        self.assertIn('тестовая броня', result)
        self.assertIn('тестовую броню', result)

    def test_with_element(self):
        rune = make_rune(element=1)
        a = make_armor()
        a.runes = [rune]
        result = a.get_names_list(['nom'])
        found = [n for n in result if 'огня' in n]
        self.assertTrue(len(found) > 0)


class TestArmorExamine(unittest.TestCase):
    def test_examine_returns_show(self):
        a = make_armor()
        self.assertEqual(a.examine(MagicMock()), a.show())


class TestArmorPlace(unittest.TestCase):
    def test_place_explicit(self):
        a = make_armor()
        place = MagicMock()
        a.place(MagicMock(), place=place)
        place.add.assert_called_once_with(a)

    def test_place_monster_wears_armor(self):
        game = make_game()
        a = make_armor(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        monster = MagicMock()
        monster.wear_armor = True
        room.monsters.return_value = monster
        result = a.place(castle)
        self.assertTrue(result)
        monster.take.assert_called_once_with(a)

    def test_place_monster_cannot_wear_armor(self):
        game = make_game()
        a = make_armor(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        monster = MagicMock()
        monster.wear_armor = False
        room.monsters.return_value = monster
        room.furniture = None
        a.place(castle)
        room.add.assert_called_once_with(a)

    def test_place_no_monster_with_furniture_can_contain(self):
        game = make_game()
        a = make_armor(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        room.monsters.return_value = None
        furniture = MagicMock()
        furniture.can_contain_weapon = True
        room.furniture = [furniture]
        a.place(castle)
        furniture.add.assert_called_once_with(a)

    def test_place_no_monster_furniture_cannot_contain(self):
        game = make_game()
        a = make_armor(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        room.monsters.return_value = None
        furniture = MagicMock()
        furniture.can_contain_weapon = False
        room.furniture = [furniture]
        a.place(castle)
        room.add.assert_called_once_with(a)

    def test_place_with_action_controller(self):
        a = make_armor()
        place = MagicMock()
        a.place(MagicMock(), place=place)
        place.action_controller.add_actions.assert_called_once_with(a)

    def test_place_without_action_controller(self):
        place = MagicMock(spec=['add'])
        place.add = MagicMock()
        make_armor().place(MagicMock(), place=place)
        place.add.assert_called_once()

    def test_place_no_monster_no_furniture(self):
        game = make_game()
        a = make_armor(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        room.monsters.return_value = None
        room.furniture = None
        a.place(castle)
        room.add.assert_called_once_with(a)


class TestArmorTake(unittest.TestCase):
    def test_take_new_armor_no_old(self):
        game = make_game()
        a = make_armor(game=game)
        hero = make_hero(game=game, armor_empty=True)
        result = a.take(hero)
        self.assertIsInstance(result, list)
        self.assertEqual(hero.armor, a)
        self.assertEqual(a.user, hero)

    def test_take_replaces_old_armor(self):
        game = make_game()
        a = make_armor(game=game)
        old = MagicMock()
        old.empty = False
        old.drop = MagicMock()
        old.__format__ = MagicMock(return_value='старая броня')
        hero = make_hero(game=game, armor_empty=False)
        hero.armor = old
        result = a.take(hero)
        self.assertEqual(len(result), 2)
        old.drop.assert_called_once_with(hero)
        self.assertEqual(hero.armor, a)


class TestArmorDrop(unittest.TestCase):
    def test_drop_light_room(self):
        game = make_game()
        a = make_armor(game=game)
        hero = make_hero(game=game)
        hero.current_position.light = True
        result = a.drop(hero)
        self.assertIn('бережно', result)
        self.assertTrue(hero.armor.empty)

    def test_drop_dark_room(self):
        game = make_game()
        a = make_armor(game=game)
        hero = make_hero(game=game)
        hero.current_position.light = False
        result = a.drop(hero)
        self.assertIn('темноту', result)

    def test_drop_adds_to_loot(self):
        game = make_game()
        a = make_armor(game=game)
        hero = make_hero(game=game)
        a.drop(hero)
        hero.current_position.loot.add.assert_called_once_with(a)

    def test_drop_removes_hero_actions(self):
        game = make_game()
        a = make_armor(game=game)
        hero = make_hero(game=game)
        a.drop(hero)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(a)
        hero.current_position.action_controller.add_actions.assert_called_once_with(a)


class TestShieldGetDamagedNames(unittest.TestCase):
    def test_no_damage(self):
        self.assertIsNone(make_shield().get_damaged_names())

    def test_with_damage(self):
        s = make_shield(accumulated_damage=1)
        result = s.get_damaged_names('nom')
        self.assertIsInstance(result, str)
        self.assertIn('Поцарапанный', result)

    def test_with_damage_all_keys(self):
        s = make_shield(accumulated_damage=2)
        result = s.get_damaged_names()
        self.assertIsInstance(result, dict)
        self.assertIn('nom', result)


class TestShieldGetFullNames(unittest.TestCase):
    def test_no_damage_no_element(self):
        s = make_shield()
        self.assertEqual(s.get_full_names('nom'), 'тестовый щит')

    def test_no_damage_with_element(self):
        rune = make_rune(element=1)
        s = make_shield()
        s.runes = [rune]
        self.assertIn('огня', s.get_full_names('nom'))

    def test_with_damage_no_element(self):
        s = make_shield(accumulated_damage=1)
        self.assertIn('Поцарапанный', s.get_full_names('nom'))

    def test_with_damage_with_element(self):
        rune = make_rune(element=1)
        s = make_shield(accumulated_damage=1)
        s.runes = [rune]
        result = s.get_full_names('nom')
        self.assertIn('Поцарапанный', result)
        self.assertIn('огня', result)

    def test_all_keys(self):
        s = make_shield(accumulated_damage=1)
        result = s.get_full_names()
        self.assertIsInstance(result, dict)
        self.assertIn('nom', result)


class TestShieldTakeAway(unittest.TestCase):
    def test_shield_in_hand(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, shield_empty=False)
        hero.shield = s
        result = s.take_away(hero)
        self.assertIn('убирает', result)

    def test_shield_already_behind(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, shield_empty=True)
        hero.removed_shield = s
        result = s.take_away(hero)
        self.assertIn('так', result)


class TestShieldTakeOut(unittest.TestCase):
    def test_twohanded_weapon(self):
        s = make_shield()
        hero = make_hero(twohanded=True)
        self.assertIn('двуручным', s.take_out(hero))

    def test_normal(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, twohanded=False, shield_empty=True, weapon_empty=False)
        hero.removed_shield = s
        result = s.take_out(hero)
        self.assertIn('достает', result)


class TestShieldDrop(unittest.TestCase):
    def test_drop_from_hand(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, shield_empty=False)
        hero.shield = s
        result = s.drop(hero)
        self.assertIn('швыряет', result)
        self.assertTrue(hero.shield.empty)

    def test_drop_from_behind(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, shield_empty=True)
        hero.removed_shield = s
        result = s.drop(hero)
        self.assertIn('ставит', result)
        self.assertTrue(hero.removed_shield.empty)

    def test_drop_adds_to_loot(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, shield_empty=False)
        hero.shield = s
        s.drop(hero)
        hero.current_position.loot.add.assert_called_once_with(s)

    def test_drop_removes_actions(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, shield_empty=False)
        hero.shield = s
        s.drop(hero)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(s)
        hero.current_position.action_controller.add_actions.assert_called_once_with(s)


class TestShieldExamine(unittest.TestCase):
    def test_examine_returns_show(self):
        s = make_shield()
        self.assertEqual(s.examine(MagicMock()), s.show())


class TestShieldRepair(unittest.TestCase):
    def test_repair_no_damage(self):
        s = make_shield(accumulated_damage=0)
        self.assertIn('не нужно', s.repair(make_hero()))

    def test_repair_enough_money(self):
        s = make_shield(accumulated_damage=5)
        hero = make_hero()
        hero.money = 100
        result = s.repair(hero)
        self.assertIn('успешно', result)
        self.assertEqual(s.accumulated_damage, 0)
        self.assertEqual(hero.money, 50)

    def test_repair_not_enough_money(self):
        s = make_shield(accumulated_damage=20)
        hero = make_hero()
        hero.money = 5
        result = s.repair(hero)
        self.assertIn('не может', result)
        self.assertEqual(s.accumulated_damage, 20)


class TestShieldGetDamageDecorator(unittest.TestCase):
    def test_no_damage(self):
        self.assertIsNone(make_shield(accumulated_damage=0).get_damage_decorator())

    def test_damage_1(self):
        result = make_shield(accumulated_damage=1).get_damage_decorator()
        self.assertIsNotNone(result)
        self.assertEqual(result['nom'], 'Поцарапанный')

    def test_damage_2(self):
        self.assertEqual(make_shield(accumulated_damage=2).get_damage_decorator()['nom'], 'Потрепанный')

    def test_damage_3(self):
        self.assertEqual(make_shield(accumulated_damage=3).get_damage_decorator()['nom'], 'Почти сломанный')

    def test_damage_4(self):
        self.assertEqual(make_shield(accumulated_damage=4).get_damage_decorator()['nom'], 'Еле живой')

    def test_damage_5_no_decorator(self):
        self.assertIsNone(make_shield(accumulated_damage=5).get_damage_decorator())


class TestShieldCheckIfBroken(unittest.TestCase):
    @patch('src.class_protection.dice', return_value=1)
    def test_broken(self, mock_dice):
        game = make_game()
        s = make_shield(game=game, accumulated_damage=5)
        s.user = MagicMock()
        game.all_shields = [s]
        result = s.check_if_broken(attack=5, mastery=0)
        self.assertTrue(result)
        self.assertNotIn(s, game.all_shields)
        self.assertTrue(s.user.shield.empty)

    @patch('src.class_protection.dice', return_value=100)
    def test_not_broken(self, mock_dice):
        game = make_game()
        s = make_shield(game=game, accumulated_damage=1)
        s.user = MagicMock()
        game.all_shields = [s]
        result = s.check_if_broken(attack=1, mastery=0)
        self.assertFalse(result)
        self.assertIn(s, game.all_shields)


class TestShieldTakeDamage(unittest.TestCase):
    @patch('src.class_protection.dice', return_value=20)
    def test_normal_damage(self, mock_dice):
        s = make_shield()
        s.take_damage(is_hiding=False)
        self.assertEqual(s.accumulated_damage, 0.2)

    @patch('src.class_protection.dice', return_value=60)
    def test_hiding_damage_higher(self, mock_dice):
        s = make_shield()
        s.take_damage(is_hiding=True)
        self.assertEqual(s.accumulated_damage, 0.6)


class TestShieldGetRepairPrice(unittest.TestCase):
    def test_no_damage(self):
        self.assertEqual(make_shield(accumulated_damage=0).get_repair_price(), 0)

    def test_with_damage(self):
        self.assertEqual(make_shield(accumulated_damage=3.5).get_repair_price(), 35)


class TestShieldGetNamesList(unittest.TestCase):
    def test_basic(self):
        result = make_shield().get_names_list(['nom', 'accus'])
        self.assertIn('щит', result)
        self.assertIn('тестовый щит', result)

    def test_with_damage(self):
        result = make_shield(accumulated_damage=1).get_names_list(['nom'])
        found = [n for n in result if 'поцарапанный' in n]
        self.assertTrue(len(found) > 0)

    def test_with_element(self):
        rune = make_rune(element=1)
        s = make_shield()
        s.runes = [rune]
        result = s.get_names_list(['nom'])
        found = [n for n in result if 'огня' in n]
        self.assertTrue(len(found) > 0)


class TestShieldPlace(unittest.TestCase):
    def test_place_explicit(self):
        s = make_shield()
        place = MagicMock()
        s.place(MagicMock(), place=place)
        place.add.assert_called_once_with(s)

    def test_place_monster_carry_shield(self):
        game = make_game()
        s = make_shield(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        monster = MagicMock()
        monster.carry_shield = True
        room.monsters.return_value = monster
        result = s.place(castle)
        self.assertTrue(result)
        monster.take.assert_called_once_with(s)

    def test_place_monster_not_carry_shield(self):
        game = make_game()
        s = make_shield(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        monster = MagicMock()
        monster.carry_shield = False
        room.monsters.return_value = monster
        room.furniture = None
        s.place(castle)
        room.add.assert_called_once_with(s)

    def test_place_no_monster_with_furniture_can_contain(self):
        game = make_game()
        s = make_shield(game=game)
        castle = MagicMock()
        room = MagicMock()
        castle.plan = [room]
        room.monsters.return_value = None
        furniture = MagicMock()
        furniture.can_contain_weapon = True
        room.furniture = [furniture]
        s.place(castle)
        furniture.add.assert_called_once_with(s)

    def test_place_with_action_controller(self):
        s = make_shield()
        place = MagicMock()
        s.place(MagicMock(), place=place)
        place.action_controller.add_actions.assert_called_once_with(s)


class TestShieldTake(unittest.TestCase):
    def test_take_normal(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, twohanded=False, shield_empty=True, weapon_empty=True)
        result = s.take(hero)
        self.assertIsInstance(result, list)
        self.assertEqual(hero.shield, s)
        self.assertEqual(s.user, hero)

    def test_take_twohanded_weapon(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, twohanded=True, weapon_empty=False)
        result = s.take(hero)
        self.assertIsInstance(result, list)
        self.assertEqual(hero.removed_shield, s)

    def test_take_replaces_old_shield(self):
        game = make_game()
        s = make_shield(game=game)
        old = MagicMock()
        old.empty = False
        old.get_full_names.return_value = 'старый щит'
        old.drop = MagicMock()
        old.__format__ = MagicMock(return_value='старый щит')
        hero = make_hero(game=game, twohanded=False, shield_empty=False)
        hero.shield = old
        hero.removed_shield = old
        result = s.take(hero)
        self.assertTrue(len(result) > 1)
        self.assertEqual(hero.shield, s)

    def test_take_adds_actions(self):
        game = make_game()
        s = make_shield(game=game)
        hero = make_hero(game=game, twohanded=False, shield_empty=True, weapon_empty=True)
        s.take(hero)
        hero.action_controller.add_actions.assert_called()
        hero.current_position.action_controller.delete_actions_by_item.assert_called()


class TestArmorHeroActions(unittest.TestCase):
    def test_has_correct_actions(self):
        a = make_armor()
        self.assertIn('снять', a.hero_actions)
        self.assertEqual(a.hero_actions['снять']['method'], 'drop')
        self.assertFalse(a.hero_actions['снять']['in_combat'])

    def test_room_actions(self):
        a = make_armor()
        self.assertIn('взять', a.room_actions)
        self.assertEqual(a.room_actions['взять']['method'], 'take')


class TestShieldHeroActions(unittest.TestCase):
    def test_hero_actions_take_out(self):
        s = make_shield()
        for key in ['использовать', 'экипировать', 'достать', 'выбрать']:
            self.assertEqual(s.hero_actions[key]['method'], 'take_out')
            self.assertTrue(s.hero_actions[key]['in_combat'])

    def test_hero_actions_drop(self):
        s = make_shield()
        for key in ['бросить', 'выбросить', 'оставить']:
            self.assertEqual(s.hero_actions[key]['method'], 'drop')
            self.assertFalse(s.hero_actions[key]['in_combat'])

    def test_hero_actions_repair(self):
        s = make_shield()
        for key in ['чинить', 'починить']:
            self.assertEqual(s.hero_actions[key]['method'], 'repair')
            self.assertFalse(s.hero_actions[key]['in_combat'])

    def test_hero_actions_other(self):
        s = make_shield()
        self.assertEqual(s.hero_actions['убрать']['method'], 'take_away')
        self.assertEqual(s.hero_actions['осмотреть']['method'], 'examine')

    def test_room_actions(self):
        s = make_shield()
        self.assertEqual(s.room_actions['взять']['method'], 'take')
        self.assertEqual(s.room_actions['осмотреть']['method'], 'examine')


class TestProtectionElementsDictionary(unittest.TestCase):
    def test_all_elements_present(self):
        self.assertIn(1, Protection._elements_dictionary)
        self.assertIn(24, Protection._elements_dictionary)

    def test_weakness_dictionary(self):
        self.assertIn(1, Protection._weakness_dictionary)
        self.assertEqual(Protection._weakness_dictionary[1], [3, 3])


class TestShieldStatesDictionary(unittest.TestCase):
    def test_states_have_all_cases(self):
        cases = {'nom', 'accus', 'gen', 'dat', 'prep', 'inst'}
        for tier, lexemes in Shield._states_dictionary.items():
            self.assertEqual(set(lexemes.keys()), cases, f"Tier {tier} missing cases")


class TestProtectionControllerInit(unittest.TestCase):
    def test_loads_templates(self):
        pc = ProtectionController(make_game())
        self.assertGreater(len(pc.templates), 0)
        self.assertEqual(pc.how_many, 0)
        self.assertEqual(pc.all_objects, [])


class TestProtectionControllerAdditionalActions(unittest.TestCase):
    def test_calls_decorate(self):
        pc = ProtectionController(make_game())
        armor = make_armor()
        with patch.object(pc, 'decorate') as mock_decorate:
            self.assertTrue(pc.additional_actions(armor))
            mock_decorate.assert_called_once_with(armor)


class TestProtectionControllerDecorate(unittest.TestCase):
    def test_armor_decorated(self):
        pc = ProtectionController(make_game())
        armor = make_armor()
        with patch.object(pc, 'decorate_armor') as mock_da:
            pc.decorate(armor)
            mock_da.assert_called_once_with(armor)

    def test_shield_not_decorated(self):
        pc = ProtectionController(make_game())
        shield = make_shield()
        with patch.object(pc, 'decorate_armor') as mock_da:
            pc.decorate(shield)
            mock_da.assert_not_called()


class TestProtectionControllerDecorateArmor(unittest.TestCase):
    def test_decorate_armor_with_decorator(self):
        pc = ProtectionController(make_game())
        armor = make_armor(protection_type='кованый', gender=1)
        original_mod = armor.protection.modifier
        with patch('src.controllers.controller_protection.randomitem') as mock_ri:
            mock_ri.return_value = {
                'protection_modifier': 2,
                1: {'nom': 'Сияющая', 'accus': 'Сияющую', 'gen': 'Сияющей', 'dat': 'Сияющей', 'prep': 'Сияющей', 'inst': 'Сияющей'},
                0: {'nom': 'Сияющий'},
                2: {'nom': 'Сияющее'}
            }
            result = pc.decorate_armor(armor)
            self.assertTrue(result)
            self.assertEqual(armor.protection.modifier, original_mod + 2)
            self.assertIn('Сияющая', armor.lexemes['nom'])

    def test_decorate_armor_no_decorator(self):
        pc = ProtectionController(make_game())
        armor = make_armor(protection_type='несуществующий')
        with patch('src.controllers.controller_protection.randomitem', return_value=[]):
            self.assertFalse(pc.decorate_armor(armor))

    def test_decorate_armor_no_gender_match(self):
        pc = ProtectionController(make_game())
        armor = make_armor(protection_type='кованый', gender=5)
        with patch('src.controllers.controller_protection.randomitem') as mock_ri:
            mock_ri.return_value = {'protection_modifier': 0, 0: {'nom': 'test'}}
            self.assertFalse(pc.decorate_armor(armor))

    def test_decorate_armor_kozhaniy(self):
        pc = ProtectionController(make_game())
        armor = make_armor(protection_type='кожаный', gender=1)
        with patch('src.controllers.controller_protection.randomitem') as mock_ri:
            mock_ri.return_value = {
                'protection_modifier': 1,
                1: {'nom': 'Крепкий', 'accus': 'Крепкого', 'gen': 'Крепкого', 'dat': 'Крепкому', 'prep': 'Крепком', 'inst': 'Крепким'},
                0: {'nom': 'Крепкий'},
                2: {'nom': 'Крепкое'}
            }
            self.assertTrue(pc.decorate_armor(armor))


class TestProtectionControllerCreateObject(unittest.TestCase):
    def test_create_shield(self):
        game = make_game()
        pc = ProtectionController(game)
        template = ProtectionController.Template(
            class_name='Shield', protection_type='щит', gender=0,
            name='Тестовый щит', lexemes=LEXEMES,
            protection={'dice': True, 'random': True, 'value': [2, 3]},
            enchantable=True, actions=['защищается'], noisy=True
        )
        with patch('src.class_controller.randint', return_value=3):
            obj = pc.create_object_from_template(template)
        self.assertIsInstance(obj, Shield)
        self.assertEqual(obj.name, 'Тестовый щит')
        self.assertEqual(pc.how_many, 1)

    def test_create_armor(self):
        pc = ProtectionController(make_game())
        template = ProtectionController.Template(
            class_name='Armor', protection_type='кованый', gender=1,
            name='Тестовая броня', lexemes=ARMOR_LEXEMES,
            protection={'dice': True, 'random': True, 'value': [3, 4]},
            enchantable=True, actions=['защищается'], noisy=True
        )
        with patch('src.class_controller.randint', return_value=3):
            obj = pc.create_object_from_template(template)
        self.assertIsInstance(obj, Armor)
        self.assertIn(obj, pc.all_objects)

    def test_create_invalid_template_type(self):
        pc = ProtectionController(make_game())
        with self.assertRaises(TypeError):
            pc.create_object_from_template("not a template")


class TestProtectionControllerGetEmpty(unittest.TestCase):
    def test_get_empty_shield(self):
        empty = ProtectionController(make_game()).get_empty_object_by_class_name('Shield')
        self.assertIsInstance(empty, Shield)
        self.assertTrue(empty.empty)

    def test_get_empty_armor(self):
        empty = ProtectionController(make_game()).get_empty_object_by_class_name('Armor')
        self.assertIsInstance(empty, Armor)
        self.assertTrue(empty.empty)

    def test_get_empty_invalid(self):
        with self.assertRaises(ValueError):
            ProtectionController(make_game()).get_empty_object_by_class_name('Invalid')


class TestProtectionControllerGetTemplates(unittest.TestCase):
    def test_get_templates_by_class_name(self):
        shield_templates = ProtectionController(make_game()).get_templates_by_class_name('Shield')
        self.assertGreater(len(shield_templates), 0)
        for t in shield_templates:
            self.assertEqual(t.class_name, 'Shield')

    def test_get_templates_invalid_type(self):
        with self.assertRaises(TypeError):
            ProtectionController(make_game()).get_templates_by_class_name(123)

    def test_get_template_by_name(self):
        template = ProtectionController(make_game()).get_template_by_name('Круглый щит')
        self.assertIsNotNone(template)
        self.assertEqual(template.class_name, 'Shield')

    def test_get_template_not_found(self):
        with self.assertRaises(ValueError):
            ProtectionController(make_game()).get_template_by_name('Несуществующий')

    def test_get_template_invalid_type(self):
        with self.assertRaises(TypeError):
            ProtectionController(make_game()).get_template_by_name(123)


class TestProtectionControllerCreateByName(unittest.TestCase):
    def test_create_by_name(self):
        with patch('src.class_controller.randint', return_value=3):
            obj = ProtectionController(make_game()).create_object_by_name('Круглый щит')
        self.assertIsInstance(obj, Shield)
        self.assertEqual(obj.name, 'Круглый щит')


class TestProtectionControllerRandomObjects(unittest.TestCase):
    def test_get_random_objects_shields(self):
        with patch('src.class_controller.randint', return_value=3):
            objects = ProtectionController(make_game()).get_random_objects_by_class_name('Shield', how_many=3)
        self.assertEqual(len(objects), 3)
        for obj in objects:
            self.assertIsInstance(obj, Shield)

    def test_get_random_objects_armors(self):
        with patch('src.class_controller.randint', return_value=3):
            objects = ProtectionController(make_game()).get_random_objects_by_class_name('Armor', how_many=2)
        self.assertEqual(len(objects), 2)
        for obj in objects:
            self.assertIsInstance(obj, Armor)


class TestProtectionControllerRandomByFilters(unittest.TestCase):
    def test_random_by_filters(self):
        with patch('src.class_controller.randint', return_value=3):
            obj = ProtectionController(make_game()).get_random_object_by_filters(class_name='Shield', enchantable=True)
        self.assertIsInstance(obj, Shield)
        self.assertTrue(obj.enchantable)

    def test_random_by_filters_no_match(self):
        with self.assertRaises(ValueError):
            ProtectionController(make_game()).get_random_object_by_filters(class_name='Nonexistent')


class TestShieldConstants(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(Shield._crushed_upper_limit, 10)
        self.assertEqual(Shield._damage_when_hiding_min, 50)
        self.assertEqual(Shield._damage_when_hiding_max, 75)
        self.assertEqual(Shield._damage_min, 10)
        self.assertEqual(Shield._damage_max, 25)
        self.assertEqual(Shield._repair_multiplier, 10)


if __name__ == '__main__':
    unittest.main()
