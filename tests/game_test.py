import unittest
from unittest.mock import MagicMock, patch

from src.class_game import Game


class TestCheckEndgame(unittest.TestCase):
    def setUp(self):
        self.game = Game(chat_id='test', bot=MagicMock())

    def test_delegates_to_monsters_controller(self):
        with patch.object(self.game.monsters_controller, 'check_endgame', return_value=True):
            self.assertTrue(self.game.check_endgame())

    def test_returns_false_when_no_endgame(self):
        with patch.object(self.game.monsters_controller, 'check_endgame', return_value=False):
            self.assertFalse(self.game.check_endgame())


class TestTraderCreateEvent(unittest.TestCase):
    def setUp(self):
        self.game = Game(chat_id='test', bot=MagicMock())

    def test_create_event_adds_to_pending(self):
        from src.class_allies import Trader
        game = MagicMock()
        game.events_controller = MagicMock()
        trader = Trader.__new__(Trader)
        trader.game = game
        trader.create_event()
        game.events_controller.create_event.assert_called_once()
        call_kwargs = game.events_controller.create_event.call_args
        self.assertIs(call_kwargs.kwargs['event_subject'], trader)
        self.assertEqual(call_kwargs.kwargs['method_name'], 'get_goods')
        self.assertGreaterEqual(call_kwargs.kwargs['counter'], 30)
        self.assertLessEqual(call_kwargs.kwargs['counter'], 50)

    def test_refresh_die_range(self):
        from src.class_allies import Trader
        values = set()
        for _ in range(100):
            values.add(Trader._refresh_die.roll())
        self.assertTrue(min(values) >= 30)
        self.assertTrue(max(values) <= 50)


class TestTraderEventCycle(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        self.game = Game(chat_id='test', bot=self.bot)

    def test_scribe_creates_event_on_init(self):
        floor = self.game.castle_floors[0]
        from src.class_allies import Scribe
        with patch.object(self.game.events_controller, 'create_event') as mock:
            scribe = Scribe(self.game, floor)
            mock.assert_called_once()
            call_kwargs = mock.call_args.kwargs
            self.assertIs(call_kwargs['event_subject'], scribe)
            self.assertEqual(call_kwargs['method_name'], 'get_goods')

    def test_scribe_get_goods_creates_event(self):
        floor = self.game.castle_floors[0]
        from src.class_allies import Scribe, Trader
        scribe = Scribe.__new__(Scribe)
        Trader.__init__(scribe, self.game, floor)
        scribe.name = '\u041a\u043d\u0438\u0436\u043d\u0438\u043a'
        scribe.lexemes = Scribe._lexemes
        with patch.object(self.game.events_controller, 'create_event') as mock:
            scribe.get_goods()
            mock.assert_called_once()
            self.assertEqual(mock.call_args.kwargs['method_name'], 'get_goods')

    def test_rune_merchant_creates_event_on_init(self):
        floor = self.game.castle_floors[0]
        from src.class_allies import RuneMerchant
        with patch.object(self.game.events_controller, 'create_event') as mock:
            merchant = RuneMerchant(self.game, floor)
            mock.assert_called_once()

    def test_potions_merchant_creates_event_on_init(self):
        floor = self.game.castle_floors[0]
        from src.class_allies import PotionsMerchant
        with patch.object(self.game.events_controller, 'create_event') as mock:
            merchant = PotionsMerchant(self.game, floor)
            mock.assert_called_once()


class TestCorpseCreateEvent(unittest.TestCase):
    def setUp(self):
        self.game = Game(chat_id='test', bot=MagicMock())

    def test_corpse_creates_event_on_place(self):
        from src.class_monsters import Corpse, Monster
        from src.class_basic import Loot
        floor = self.game.castle_floors[0]
        room = floor.plan[0]
        monster = self.game.monsters_controller.create_object_by_name('\u0413\u043e\u0431\u043b\u0438\u043d')
        monster.place(floor)
        loot = Loot(self.game)
        corpse = Corpse(self.game, '\u0422\u0440\u0443\u043f', loot, room, creature=monster, can_resurrect=True)
        self.assertTrue(len(self.game.events_controller.pending_events) >= 1)

    def test_resurrection_die_range(self):
        from src.class_monsters import Corpse
        values = set()
        for _ in range(50):
            values.add(Corpse._resurection_die.roll())
        self.assertTrue(min(values) >= 1)
        self.assertTrue(max(values) <= 5)


if __name__ == '__main__':
    unittest.main()
