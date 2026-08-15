import unittest
from unittest.mock import MagicMock, patch

from src.class_backpack import Backpack


class Weapon:
    pass


class Axe(Weapon):
    def __init__(self, weapon_type='топор'):
        self.weapon_type = weapon_type
        self.place = None
        self.can_use_in_fight = True

    def show(self):
        return 'топор'


class FakeItem:
    def __init__(self, name='вещь', can_use_in_fight=False, enchantable=False):
        self.name = name
        self.place = None
        self.can_use_in_fight = can_use_in_fight
        self.enchantable = enchantable

    def check_name(self, name):
        return self.name == name

    def show(self):
        return self.name


def make_who(game, backpack, mastery=None):
    who = MagicMock()
    who.name = 'Герой'
    who.backpack = backpack
    who.game = game
    who.g = MagicMock(return_value='героя')
    who.__format__ = MagicMock(return_value='он')
    who.mastery = mastery or {}
    who.action_controller = MagicMock()
    room = MagicMock()
    room.loot = MagicMock()
    room.action_controller = MagicMock()
    who.current_position = room
    return who, room


class TestBackpackInit(unittest.TestCase):

    def test_default_init(self):
        game = MagicMock()
        backpack = Backpack(game)
        self.assertEqual(backpack.insides, [])
        self.assertEqual(backpack.name, 'рюкзак')
        self.assertIs(backpack.game, game)
        self.assertFalse(backpack.no_backpack)
        self.assertIsNone(backpack.owner)
        self.assertEqual(backpack.lexemes['nom'], 'рюкзак')
        self.assertEqual(backpack.lexemes['accus'], 'рюкзак')
        self.assertIn('осмотреть', backpack.hero_actions)
        self.assertIn('бросить', backpack.hero_actions)
        self.assertEqual(backpack.hero_actions['осмотреть']['method'], 'show')
        self.assertEqual(backpack.hero_actions['бросить']['method'], 'drop')
        self.assertIn('взять', backpack.room_actions)
        self.assertEqual(backpack.room_actions['взять']['method'], 'take')

    def test_init_with_no_backpack_flag(self):
        backpack = Backpack(MagicMock(), no_backpack=True)
        self.assertTrue(backpack.no_backpack)


class TestBackpackNameAndFormat(unittest.TestCase):

    def setUp(self):
        self.backpack = Backpack(MagicMock())

    def test_get_name_for_show(self):
        self.assertEqual(self.backpack.get_name_for_show(MagicMock()), 'Рюкзак героя')

    def test_format_existing_key(self):
        self.assertEqual(format(self.backpack, 'nom'), 'рюкзак')
        self.assertEqual(format(self.backpack, 'gen'), 'рюкзака')
        self.assertEqual(format(self.backpack, 'prep'), 'рюкзаке')

    def test_format_missing_key(self):
        self.assertEqual(format(self.backpack, 'nonexistent'), '')
        self.assertEqual(f'{self.backpack:nom}', 'рюкзак')

    def test_check_name_accepts_name_and_accus(self):
        self.assertTrue(self.backpack.check_name('рюкзак'))
        self.assertTrue(self.backpack.check_name('РЮКЗАК'))
        self.assertFalse(self.backpack.check_name('рюкзаком'))
        self.assertFalse(self.backpack.check_name('мешок'))

    def test_get_names_list(self):
        self.assertEqual(self.backpack.get_names_list(), ['рюкзак'])
        self.assertEqual(self.backpack.get_names_list(['nom', 'accus']), ['рюкзак'])


class TestBackpackAddRemove(unittest.TestCase):

    def setUp(self):
        self.backpack = Backpack(MagicMock())

    def test_append_sets_place(self):
        item = FakeItem()
        self.backpack.append(item)
        self.assertIn(item, self.backpack.insides)
        self.assertIs(item.place, self.backpack)

    def test_add_returns_self(self):
        item = FakeItem()
        result = self.backpack + item
        self.assertIs(result, self.backpack)
        self.assertIn(item, self.backpack.insides)

    def test_iadd_keeps_backpack(self):
        item = FakeItem()
        self.backpack += item
        self.assertIsInstance(self.backpack, Backpack)
        self.assertIn(item, self.backpack.insides)

    def test_remove_with_place(self):
        item = FakeItem()
        self.backpack.append(item)
        target = MagicMock()
        self.backpack.remove(item, place=target)
        self.assertNotIn(item, self.backpack.insides)
        self.assertIs(item.place, target)

    def test_remove_default_place_none(self):
        item = FakeItem()
        self.backpack.append(item)
        self.backpack.remove(item)
        self.assertIsNone(item.place)


class TestBackpackDropTake(unittest.TestCase):

    def test_drop(self):
        game = MagicMock()
        game.no_backpack = MagicMock()
        backpack = Backpack(game)
        backpack.owner = object()
        who, room = make_who(game, backpack)
        result = backpack.drop(who)
        room.loot.add.assert_called_once_with(backpack)
        who.action_controller.delete_actions_by_item.assert_called_once_with(backpack)
        room.action_controller.add_actions.assert_called_once_with(backpack)
        self.assertIsNone(backpack.owner)
        self.assertIs(who.backpack, game.no_backpack)
        self.assertEqual(result, 'Герой снимает рюкзак и кладет в угол комнаты.')

    def test_take_blocked_when_hero_has_backpack(self):
        game = MagicMock()
        backpack = Backpack(game)
        who = MagicMock()
        who.name = 'Герой'
        who.backpack = MagicMock()
        who.backpack.no_backpack = False
        result = backpack.take(who)
        self.assertEqual(
            result,
            'Герой не может надеть новый рюкзак поверх своего рюкзака. Это уже слишком.')
        self.assertIsNot(who.backpack, backpack)

    def test_take_success(self):
        game = MagicMock()
        backpack = Backpack(game)
        who, room = make_who(game, backpack)
        who.backpack.no_backpack = True
        result = backpack.take(who)
        self.assertIs(who.backpack, backpack)
        self.assertIs(backpack.owner, who)
        who.action_controller.add_actions.assert_called_once_with(backpack)
        room.action_controller.delete_actions_by_item.assert_called_once_with(backpack)
        self.assertIn('надевает рюкзак', result)


class TestBackpackItemSearch(unittest.TestCase):

    def setUp(self):
        self.game = MagicMock()
        self.backpack = Backpack(self.game)

    def test_get_items_list(self):
        first = FakeItem()
        second = FakeItem()
        self.backpack.append(first)
        self.backpack.append(second)
        self.assertEqual(self.backpack.get_items_list(), self.backpack.insides)

    def test_get_items_by_class_base(self):
        item = FakeItem()
        self.backpack.append(item)
        self.assertEqual(self.backpack.get_items_by_class('FakeItem'), [item])

    def test_get_items_by_class_subclass(self):
        axe = Axe()
        self.backpack.append(axe)
        self.assertEqual(self.backpack.get_items_by_class('Weapon'), [axe])

    def test_get_first_item_by_name_found(self):
        first = FakeItem(name='книга')
        second = FakeItem(name='руна')
        self.backpack.append(first)
        self.backpack.append(second)
        self.assertIs(self.backpack.get_first_item_by_name('книга'), first)

    def test_get_first_item_by_name_not_found(self):
        self.backpack.append(FakeItem(name='книга'))
        self.assertFalse(self.backpack.get_first_item_by_name('руна'))

    def test_get_first_item_by_class_found(self):
        axe = Axe()
        self.backpack.append(FakeItem())
        self.backpack.append(axe)
        self.assertIs(self.backpack.get_first_item_by_class('Weapon'), axe)

    def test_get_first_item_by_class_not_found(self):
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.get_first_item_by_class('Weapon'))

    def test_count_items(self):
        self.assertEqual(self.backpack.count_items(), 0)
        self.backpack.append(FakeItem())
        self.backpack.append(FakeItem())
        self.assertEqual(self.backpack.count_items(), 2)

    def test_is_empty(self):
        self.assertTrue(self.backpack.is_empty())
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.is_empty())

    def test_get_items_except_class(self):
        axe = Axe()
        book = FakeItem(name='книга')
        self.backpack.append(axe)
        self.backpack.append(book)
        result = self.backpack.get_items_except_class('Weapon')
        self.assertEqual(result, [book])

    @patch('src.class_backpack.randomitem')
    def test_get_random_item(self, mock_randomitem):
        item = FakeItem()
        self.backpack.append(item)
        mock_randomitem.return_value = item
        self.assertIs(self.backpack.get_random_item(), item)
        mock_randomitem.assert_called_once_with(self.backpack.insides)

    def test_get_random_item_empty(self):
        self.assertFalse(self.backpack.get_random_item())

    @patch('src.class_backpack.randomitem')
    def test_get_random_item_by_class(self, mock_randomitem):
        axe = Axe()
        self.backpack.append(axe)
        mock_randomitem.return_value = axe
        self.assertIs(self.backpack.get_random_item_by_class('Weapon'), axe)

    def test_get_random_item_by_class_no_match(self):
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.get_random_item_by_class('Weapon'))

    def test_get_random_item_by_class_empty(self):
        self.assertFalse(self.backpack.get_random_item_by_class('Weapon'))

    def test_get_item_by_number(self):
        first = FakeItem(name='первый')
        second = FakeItem(name='второй')
        self.backpack.append(first)
        self.backpack.append(second)
        self.assertIs(self.backpack.get_item_by_number(1), first)
        self.assertIs(self.backpack.get_item_by_number(2), second)

    def test_get_item_by_number_out_of_range(self):
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.get_item_by_number(2))

    def test_get_item_by_number_zero(self):
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.get_item_by_number(0))

    def test_get_item_by_number_negative(self):
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.get_item_by_number(-1))

    def test_get_item_by_number_non_int(self):
        self.backpack.append(FakeItem())
        self.assertFalse(self.backpack.get_item_by_number('1'))


class TestBackpackFightAndEnchant(unittest.TestCase):

    def test_get_items_for_fight(self):
        backpack = Backpack(MagicMock())
        usable = FakeItem(can_use_in_fight=True)
        useless = FakeItem(can_use_in_fight=False)
        backpack.append(usable)
        backpack.append(useless)
        self.assertEqual(backpack.get_items_for_fight(), [usable])

    def test_get_items_for_fight_empty(self):
        backpack = Backpack(MagicMock())
        self.assertEqual(backpack.get_items_for_fight(), [])

    def test_get_items_to_enchant(self):
        backpack = Backpack(MagicMock())
        enchantable = FakeItem(enchantable=True)
        plain = FakeItem(enchantable=False)
        backpack.append(enchantable)
        backpack.append(plain)
        self.assertEqual(backpack.get_items_to_enchant(), [enchantable])

    def test_get_items_to_enchant_empty(self):
        backpack = Backpack(MagicMock())
        self.assertEqual(backpack.get_items_to_enchant(), [])


class TestBackpackShow(unittest.TestCase):

    def test_show_without_backpack(self):
        game = MagicMock()
        backpack = Backpack(game, no_backpack=True)
        who, _ = make_who(game, backpack)
        self.assertEqual(
            backpack.show(who),
            ['У героя нет рюкзака, поэтому и осматривать нечего.'])

    def test_show_empty(self):
        game = MagicMock()
        backpack = Backpack(game)
        who, _ = make_who(game, backpack)
        self.assertEqual(
            backpack.show(who),
            ['Герой осматривает свой рюкзак и обнаруживает, что тот абсолютно пуст.'])

    def test_show_with_items(self):
        game = MagicMock()
        backpack = Backpack(game)
        who, _ = make_who(game, backpack)
        backpack.append(FakeItem(name='книга'))
        backpack.append(FakeItem(name='руна'))
        message = backpack.show(who)
        self.assertEqual(len(message), 3)
        self.assertEqual(message[0], 'Герой осматривает свой рюкзак и обнаруживает в нем:')
        self.assertEqual(message[1], '1: книга')
        self.assertEqual(message[2], '2: руна')

    def test_show_weapon_with_mastery_level(self):
        game = MagicMock()
        backpack = Backpack(game)
        who, _ = make_who(game, backpack, mastery={'топор': {'level': 3}})
        backpack.append(Axe())
        message = backpack.show(who)
        self.assertEqual(message[1], '1: топор, мастерство - 3')

    def test_show_weapon_with_zero_mastery(self):
        game = MagicMock()
        backpack = Backpack(game)
        who, _ = make_who(game, backpack, mastery={'топор': {'level': 0}})
        backpack.append(Axe())
        message = backpack.show(who)
        self.assertEqual(message[1], '1: топор')

    def test_show_weapon_without_mastery_key(self):
        game = MagicMock()
        backpack = Backpack(game)
        who, _ = make_who(game, backpack, mastery={})
        backpack.append(Axe())
        message = backpack.show(who)
        self.assertEqual(message[1], '1: топор')


if __name__ == '__main__':
    unittest.main()
