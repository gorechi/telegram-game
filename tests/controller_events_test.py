import contextlib
import gc
import io
import unittest

from src.class_game import Game
from src.controllers.controller_events import EventsController
from src.enums import state_enum


class FakeBot:
    """Заглушка бота, которая запоминает отправленные сообщения."""

    def __init__(self):
        self.sent = []

    def send_message(self, chat_id, text, reply_markup=None):
        self.sent.append(str(text))


class Stub:
    """Заглушка-субъект события, запоминающая вызовы."""

    def __init__(self):
        self.calls = []

    def record(self, obj):
        self.calls.append(('record', obj))

    def other(self, obj):
        self.calls.append(('other', obj))


class TestCreateEvent(unittest.TestCase):
    """Создание событий."""

    def setUp(self):
        self.controller = EventsController(game=None)

    def test_immediate_event_goes_to_queue(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj')
        self.assertEqual(len(self.controller.queue), 1)
        self.assertEqual(len(self.controller.pending_events), 0)

    def test_delayed_event_goes_to_pending(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj', counter=5)
        self.assertEqual(len(self.controller.queue), 0)
        self.assertEqual(len(self.controller.pending_events), 1)

    def test_event_fields_are_stored(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj', counter=3)
        event = self.controller.pending_events[0]
        self.assertIs(event.event_subject, subject)
        self.assertEqual(event.subject_method_name, 'record')
        self.assertEqual(event.event_object, 'obj')
        self.assertEqual(event.counter, 3)


class TestExecuteEvent(unittest.TestCase):
    """Выполнение событий из очереди."""

    def setUp(self):
        self.controller = EventsController(game=None)

    def test_execute_queued_event_calls_subject_method(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj')
        self.controller.execute_all_events(0)
        self.assertEqual(subject.calls, [('record', 'obj')])

    def test_execute_queued_events_in_fifo_order(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'first')
        self.controller.create_event(subject, 'other', 'second')
        self.controller.create_event(subject, 'record', 'third')
        self.controller.execute_all_events(0)
        self.assertEqual(subject.calls, [
            ('record', 'first'),
            ('other', 'second'),
            ('record', 'third'),
        ])

    def test_queue_is_empty_after_execution(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj')
        self.controller.execute_all_events(0)
        self.assertEqual(len(self.controller.queue), 0)

    def test_execute_event_public_method(self):
        subject = Stub()
        event = EventsController.Event(
            event_subject=subject,
            event_object='obj',
            subject_method_name='record'
        )
        self.controller.execute_event(event)
        self.assertEqual(subject.calls, [('record', 'obj')])

    def test_missing_method_is_ignored(self):
        subject = Stub()
        self.controller.create_event(subject, 'no_such_method', 'obj')
        self.controller.execute_all_events(0)

    def test_empty_queue_is_not_crash(self):
        self.controller.execute_all_events(0)


class TestPendingEvents(unittest.TestCase):
    """Отложенные события со счетчиком."""

    def setUp(self):
        self.controller = EventsController(game=None)

    def test_pending_event_not_executed_until_counter_reaches_zero(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj', counter=5)
        self.controller.execute_all_events(4)
        self.assertEqual(subject.calls, [])
        self.assertEqual(len(self.controller.pending_events), 1)
        event = self.controller.pending_events[0]
        self.assertEqual(event.counter, 1)

    def test_pending_event_executed_when_counter_reaches_zero(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj', counter=5)
        self.controller.execute_all_events(5)
        self.assertEqual(subject.calls, [('record', 'obj')])
        self.assertEqual(len(self.controller.pending_events), 0)

    def test_counter_is_an_upper_bound(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'obj', counter=5)
        self.controller.execute_all_events(6)
        self.assertEqual(subject.calls, [('record', 'obj')])

    def test_multiple_pending_events_ready_in_one_call_all_execute(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'first', counter=3)
        self.controller.create_event(subject, 'other', 'second', counter=3)
        self.controller.execute_all_events(3)
        self.assertEqual(len(subject.calls), 2)
        self.assertEqual(len(self.controller.pending_events), 0)

    def test_pending_events_with_different_counters(self):
        subject = Stub()
        self.controller.create_event(subject, 'record', 'soon', counter=2)
        self.controller.create_event(subject, 'other', 'later', counter=5)
        self.controller.execute_all_events(2)
        self.assertEqual(subject.calls, [('record', 'soon')])
        self.assertEqual(len(self.controller.pending_events), 1)
        self.assertEqual(self.controller.pending_events[0].counter, 3)
        self.controller.execute_all_events(3)
        self.assertEqual(subject.calls, [
            ('record', 'soon'),
            ('other', 'later'),
        ])


class TestDeletePendingEvents(unittest.TestCase):
    """Удаление отложенных событий по субъекту."""

    def setUp(self):
        self.controller = EventsController(game=None)

    def test_deletes_pending_events_by_subject(self):
        subject1 = Stub()
        subject2 = Stub()
        self.controller.create_event(subject1, 'record', 'a', counter=1)
        self.controller.create_event(subject2, 'record', 'b', counter=1)
        self.controller.delete_pending_events_by_subject(subject1)
        self.assertEqual(len(self.controller.pending_events), 1)
        self.assertIs(self.controller.pending_events[0].event_subject, subject2)

    def test_deleting_unknown_subject_keeps_all(self):
        subject1 = Stub()
        subject2 = Stub()
        self.controller.create_event(subject1, 'record', 'a', counter=1)
        self.controller.delete_pending_events_by_subject(subject2)
        self.assertEqual(len(self.controller.pending_events), 1)
        self.assertIs(self.controller.pending_events[0].event_subject, subject1)


class TestFurnitureAmbushEvent(unittest.TestCase):
    """Засада монстра в мебели, реализованная через события."""

    @staticmethod
    def _create_game():
        bot = FakeBot()
        with contextlib.redirect_stdout(io.StringIO()):
            game = Game('test', bot)
        return bot, game

    def _set_up_scene(self):
        bot, game = self._create_game()
        hero = game.player
        room = hero.current_position
        room.floor.monsters_in_rooms[room] = []
        furniture = game.furniture_controller.create_object_by_name('сундук')
        furniture.room = room
        room.furniture.append(furniture)
        monster = game.monsters_controller.create_object_by_name('Гоблин')
        with contextlib.redirect_stdout(io.StringIO()):
            monster.place(room.floor, room_to_place=room)
        monster.can_hide = True
        monster.hide = True
        monster.hiding_place = furniture
        return bot, game, hero, room, furniture, monster

    def tearDown(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for attr in ('bot', 'game', 'hero', 'room', 'furniture', 'monster'):
                setattr(self, attr, None)
            gc.collect()

    def test_search_creates_ambush_event(self):
        bot, game, hero, room, furniture, monster = self._set_up_scene()
        with contextlib.redirect_stdout(io.StringIO()):
            result = furniture.search(hero)
        self.assertFalse(result)
        self.assertEqual(len(game.events_controller.queue), 1)
        event = game.events_controller.queue[0]
        self.assertIs(event.event_subject, monster)
        self.assertEqual(event.subject_method_name, 'attack_from_ambush')
        self.assertIs(event.event_object, hero)

    def test_ambush_event_does_not_trigger_until_execution(self):
        bot, game, hero, room, furniture, monster = self._set_up_scene()
        with contextlib.redirect_stdout(io.StringIO()):
            furniture.search(hero)
        self.assertEqual(monster.hiding_place, furniture)
        self.assertTrue(monster.hide)
        self.assertIsNone(hero.current_fight)

    def test_executing_ambush_event_starts_fight(self):
        bot, game, hero, room, furniture, monster = self._set_up_scene()
        with contextlib.redirect_stdout(io.StringIO()):
            furniture.search(hero)
            game.events_controller.execute_all_events(0)
        self.assertIsNone(monster.hiding_place)
        self.assertFalse(monster.hide)
        self.assertEqual(hero.state, state_enum.FIGHT)
        self.assertIsNotNone(hero.current_fight)

    def test_executing_ambush_event_sends_messages_to_bot(self):
        bot, game, hero, room, furniture, monster = self._set_up_scene()
        with contextlib.redirect_stdout(io.StringIO()):
            furniture.search(hero)
            game.events_controller.execute_all_events(0)
        self.assertTrue(bot.sent)


if __name__ == '__main__':
    unittest.main()
