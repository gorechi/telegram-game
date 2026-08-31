import unittest
from unittest.mock import MagicMock

from src.controllers.controller_actions import ActionController


def make_item(name='Меч', hero_actions=None, room_actions=None, fight_actions=None, names=None):
    item = MagicMock()
    item.name = name
    if names is None:
        names = [name, name]
    item.get_names_list.return_value = names
    if hero_actions is not None:
        item.hero_actions = hero_actions
    if room_actions is not None:
        item.room_actions = room_actions
    if fight_actions is not None:
        item.fight_actions = fight_actions
    return item


class TestGetRoom(unittest.TestCase):

    def test_returns_room_when_set(self):
        room = MagicMock()
        ctrl = ActionController(MagicMock(), room=room)
        self.assertIs(ctrl.get_room(), room)

    def test_returns_hero_position_when_no_room(self):
        hero = MagicMock()
        hero.current_position = 'pos'
        ctrl = ActionController(MagicMock(), hero=hero)
        self.assertEqual(ctrl.get_room(), 'pos')

    def test_returns_fight_hero_position_when_no_room_and_no_hero(self):
        fight = MagicMock()
        fight.hero.current_position = 'fight_pos'
        ctrl = ActionController(MagicMock(), fight=fight)
        self.assertEqual(ctrl.get_room(), 'fight_pos')


class TestExtractActions(unittest.TestCase):

    def setUp(self):
        self.hero = MagicMock()
        self.room = MagicMock()
        self.fight = MagicMock()

    def test_hero_actions_priority(self):
        item = make_item(hero_actions={'a': 1}, room_actions={'r': 2}, fight_actions={'f': 3})
        ctrl = ActionController(MagicMock(), hero=self.hero, room=self.room, fight=self.fight)
        self.assertEqual(ctrl.extract_actions(item), {'a': 1})

    def test_room_actions_when_no_hero(self):
        item = make_item(room_actions={'r': 2}, fight_actions={'f': 3})
        ctrl = ActionController(MagicMock(), room=self.room, fight=self.fight)
        self.assertEqual(ctrl.extract_actions(item), {'r': 2})

    def test_fight_actions_when_no_hero_and_no_room(self):
        item = make_item(fight_actions={'f': 3})
        ctrl = ActionController(MagicMock(), fight=self.fight)
        self.assertEqual(ctrl.extract_actions(item), {'f': 3})

    def test_empty_dict_when_nothing_matches(self):
        item = make_item()
        ctrl = ActionController(MagicMock())
        self.assertEqual(ctrl.extract_actions(item), dict())


class TestAddAndGetActions(unittest.TestCase):
    def setUp(self):
        self.hero = MagicMock()
        self.ctrl = ActionController(MagicMock(), hero=self.hero)


class TestGetItemsByAction(unittest.TestCase):

    def test_returns_empty_when_action_absent(self):
        ctrl = ActionController(MagicMock())
        self.assertEqual(ctrl.get_items_by_action('неизвестно'), [])

    def test_returns_items_for_action(self):
        hero = MagicMock()
        ctrl = ActionController(MagicMock(), hero=hero)
        item = make_item(name='Меч', hero_actions={'ударить': {'method': 'attack'}})
        ctrl.add_actions(item)
        result = ctrl.get_items_by_action('ударить')
        self.assertEqual(len(result), 1)
        self.assertIs(result[0].item, item)


class TestGetItemsByActionAndName(unittest.TestCase):

    def _ctrl_with_items(self):
        hero = MagicMock()
        ctrl = ActionController(MagicMock(), hero=hero)
        item1 = make_item(name='Меч', hero_actions={
            'ударить': {'method': 'attack', 'in_combat': True, 'in_darkness': True}})
        item2 = make_item(name='Щит', names=['щит', 'щит'], hero_actions={
            'ударить': {'method': 'defend', 'in_combat': True}})
        ctrl.add_actions(item1)
        ctrl.add_actions(item2)
        return ctrl

    def test_filter_by_in_combat(self):
        ctrl = self._ctrl_with_items()
        result = ctrl.get_items_by_action_and_name('ударить', in_combat=True)
        self.assertEqual(len(result), 2)

    def test_filter_by_in_darkness(self):
        ctrl = self._ctrl_with_items()
        result = ctrl.get_items_by_action_and_name('ударить', in_darkness=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Меч')

    def test_filter_by_name(self):
        ctrl = self._ctrl_with_items()
        result = ctrl.get_items_by_action_and_name('ударить', name='щит')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Щит')

    def test_no_action_returns_empty(self):
        ctrl = self._ctrl_with_items()
        self.assertEqual(ctrl.get_items_by_action_and_name('неттакого'), [])

    def test_both_darkness_and_combat_filters(self):
        ctrl = self._ctrl_with_items()
        result = ctrl.get_items_by_action_and_name('ударить', in_darkness=True, in_combat=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Меч')


if __name__ == '__main__':
    unittest.main()
