import unittest
from unittest.mock import MagicMock, patch

from src.class_game import Game
from src.class_allies import Trader


class TestTriggerOnMovement(unittest.TestCase):
    def setUp(self):
        self.game = Game(chat_id='test', bot=MagicMock())

    def test_calls_raise_dead(self):
        with patch.object(self.game, 'raise_dead') as mock:
            self.game.trigger_on_movement()
            mock.assert_called_once()

    def test_does_not_call_check_traders_update(self):
        with patch.object(self.game, 'raise_dead'):
            with patch.object(self.game, 'check_traders_update', create=True) as mock:
                self.game.trigger_on_movement()
                mock.assert_not_called()


class TestRaiseDead(unittest.TestCase):
    def setUp(self):
        self.game = Game(chat_id='test', bot=MagicMock())

    def test_calls_try_to_rise_on_resurrectable_corpses(self):
        c1 = MagicMock()
        c1.can_resurrect = True
        c2 = MagicMock()
        c2.can_resurrect = True
        self.game.all_corpses = [c1, c2]
        self.game.raise_dead()
        c1.try_to_rise.assert_called_once()
        c2.try_to_rise.assert_called_once()

    def test_skips_non_resurrectable_corpses(self):
        c1 = MagicMock()
        c1.can_resurrect = False
        c2 = MagicMock()
        c2.can_resurrect = True
        self.game.all_corpses = [c1, c2]
        self.game.raise_dead()
        c1.try_to_rise.assert_not_called()
        c2.try_to_rise.assert_called_once()

    def test_empty_corpses_list(self):
        self.game.all_corpses = []
        self.game.raise_dead()


class TestTraderCreateEvent(unittest.TestCase):
    def setUp(self):
        self.game = Game(chat_id='test', bot=MagicMock())

    def test_create_event_adds_to_pending(self):
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
        values = set()
        for _ in range(100):
            values.add(Trader._refresh_die.roll())
        self.assertTrue(min(values) >= 30)
        self.assertTrue(max(values) <= 50)


class TestTraderEventCycle(unittest.TestCase):
    """Интеграционный тест: get_goods -> create_event -> execute -> get_goods."""

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
        from src.class_allies import Scribe
        scribe = Scribe.__new__(Scribe)
        Trader.__init__(scribe, self.game, floor)
        scribe.name = 'Книжник'
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


if __name__ == '__main__':
    unittest.main()
