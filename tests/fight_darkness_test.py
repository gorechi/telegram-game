import contextlib
import gc
import io
import unittest
from unittest.mock import MagicMock

from src.class_dice import Dice
from src.class_fight import Fight
from src.class_game import Game
from src.class_hero import Hero
from src.class_monsters import Monster
from src.class_room import Door
from src.controllers.controller_monsters import MonstersController
from src.controllers.controller_weapon import WeaponController
from src.enums import state_enum


class FakeBot:
    """Заглушка бота, которая запоминает отправленные сообщения."""

    def __init__(self):
        self.sent = []

    def send_message(self, chat_id, text, reply_markup=None):
        self.sent.append(str(text))


class TestFightStartsInDarkness(unittest.TestCase):
    """После провала крадущейся ходьбы в темноте должна начинаться схватка."""

    @staticmethod
    def _create_game():
        bot = FakeBot()
        with contextlib.redirect_stdout(io.StringIO()):
            game = Game('test', bot)
        return bot, game

    @staticmethod
    def _act(hero, command: str):
        with contextlib.redirect_stdout(io.StringIO()):
            hero.action(command, command)

    def _set_up_scene(self, torch_present: bool):
        bot, game = self._create_game()
        hero = game.player
        room = hero.current_position
        room.floor.monsters_in_rooms[room] = []
        room.light = False
        if torch_present:
            if not room.torch:
                room.torch = game.weapon_controller.get_random_objects_by_class_name('Torch')[0]
            room.torch.burning = False
        else:
            room.torch = False
        monster = game.monsters_controller.create_object_by_name('Гоблин')
        with contextlib.redirect_stdout(io.StringIO()):
            monster.place(room.floor, room_to_place=room)
        hero.check_dext = lambda against=0, add=None: False
        go_dir = None
        for index, door in enumerate(room.doors):
            if not door.empty and not door.locked:
                go_dir = Door._directions[index]
                break
        self.assertIsNotNone(go_dir, 'В стартовой комнате нет открытой двери.')
        return bot, game, hero, room, monster, go_dir

    def tearDown(self):
        with contextlib.redirect_stdout(io.StringIO()):
            for attr in ('bot', 'game', 'hero', 'room', 'monster'):
                setattr(self, attr, None)
            gc.collect()

    def test_fight_starts_in_dark_room_without_torch(self):
        """В темной комнате без факела после провала крадущейся ходьбы начинается схватка."""
        bot, game, hero, room, monster, go_dir = self._set_up_scene(torch_present=False)
        self._act(hero, 'идти ' + go_dir)
        self.assertEqual(hero.state, state_enum.FIGHT)
        self.assertIsNotNone(hero.current_fight)
        self.assertTrue(monster.disturbed)
        self.assertTrue(any('нападает' in message for message in bot.sent))

    def test_fight_starts_in_dark_room_with_unlit_torch(self):
        """В темной комнате с потухшим факелом схватка тоже начинается."""
        bot, game, hero, room, monster, go_dir = self._set_up_scene(torch_present=True)
        self._act(hero, 'идти ' + go_dir)
        self.assertEqual(hero.state, state_enum.FIGHT)
        self.assertIsNotNone(hero.current_fight)
        self.assertTrue(monster.disturbed)

    def test_monster_attacks_and_hero_can_attack_in_dark_fight(self):
        """В схватке в темноте работают и атака монстра, и атака героя."""
        bot, game, hero, room, monster, go_dir = self._set_up_scene(torch_present=False)
        self._act(hero, 'идти ' + go_dir)
        hero_health_before = hero.health
        monster_health_before = monster.health
        self._act(hero, 'атаковать 1')
        self.assertEqual(hero.state, state_enum.FIGHT)
        self.assertLessEqual(monster.health, monster_health_before)
        self.assertLessEqual(hero.health, hero_health_before)

    def test_attack_outside_combat_in_darkness(self):
        """Команда 'атаковать' вне схватки в темной комнате не должна падать."""
        bot, game, hero, room, monster, go_dir = self._set_up_scene(torch_present=False)
        self._act(hero, 'атаковать')
        self.assertEqual(hero.state, state_enum.ACTION)
        self.assertIn('Кого-то, прячущегося в темноте', '\n'.join(bot.sent))


class TestDoorCheckDisturbedMonsters(unittest.TestCase):
    """Дверь должна начинать схватку с взбудораженными монстрами."""

    def test_delegates_to_who(self):
        door = Door(game=MagicMock())
        who = MagicMock()
        door.check_disturbed_monsters(who)
        who.check_disturbed_monsters.assert_called_once_with(who)


class TestMonsterIsNotHiding(unittest.TestCase):
    """Условие атаки монстра вызывается с параметром комнаты."""

    def test_accepts_room_argument(self):
        monster = Monster(game=MagicMock())
        monster.hide = False
        self.assertTrue(monster.is_not_hiding(room=None))
        monster.hide = True
        self.assertFalse(monster.is_not_hiding(room=None))


class TestMonsterGetNameForBeingAttacked(unittest.TestCase):
    """Имя монстра в темноте зависит от света в комнате героя."""

    def setUp(self):
        self.monster = Monster(game=MagicMock())
        self.monster.lexemes = {'accus': 'гоблина'}
        self.monster.gender = 0
        self.who = MagicMock()

    def test_hidden_name_in_darkness(self):
        self.who.check_light.return_value = False
        result = self.monster.get_name_for_being_attacked(self.who)
        self.assertEqual(result, 'Кого-то, прячущегося в темноте')
        self.who.check_light.assert_called_once()
        self.who.current_position.check_light.assert_not_called()

    def test_name_when_light(self):
        self.who.check_light.return_value = True
        result = self.monster.get_name_for_being_attacked(self.who)
        self.assertEqual(result, 'Гоблина')


class TestHeroCheckLight(unittest.TestCase):
    """Проверка света в темной комнате без факела не должна падать."""

    def setUp(self):
        self.hero = Hero(game=MagicMock())
        self.hero.weapon = self.hero.game.no_weapon
        self.hero.weapon.element.return_value = 0
        self.hero.shield.element.return_value = 0
        self.hero.armor.element.return_value = 0

    def test_dark_room_without_torch(self):
        room = MagicMock()
        room.light = False
        room.torch = False
        self.hero.current_position = room
        self.assertFalse(self.hero.check_light())

    def test_dark_room_with_unlit_torch(self):
        room = MagicMock()
        room.light = False
        torch = MagicMock()
        torch.burning = False
        room.torch = torch
        self.hero.current_position = room
        self.assertFalse(self.hero.check_light())

    def test_dark_room_with_burning_torch(self):
        room = MagicMock()
        room.light = False
        torch = MagicMock()
        torch.burning = True
        room.torch = torch
        self.hero.current_position = room
        self.assertTrue(self.hero.check_light())

    def test_light_room(self):
        room = MagicMock()
        room.light = True
        room.torch = False
        self.hero.current_position = room
        self.assertTrue(self.hero.check_light())


class TestMonsterHitChanceIsDice(unittest.TestCase):
    """Шанс попадания монстров должен быть кубиком."""

    def test_goblin_hit_chance_is_dice(self):
        controller = MonstersController(game=MagicMock())
        monster = controller.create_object_by_name('Гоблин')
        self.assertIsInstance(monster.hit_chance, Dice)

    def test_all_templates_have_dice_hit_chance(self):
        controller = MonstersController(game=MagicMock())
        for template in controller.templates:
            self.assertTrue(
                template.hit_chance.get('dice'),
                f'У монстра {template.name} hit_chance должен быть кубиком.')


class TestNoWeaponDefaults(unittest.TestCase):
    """Пустое оружие (голые руки) должно корректно участвовать в схватке."""

    def setUp(self):
        self.controller = WeaponController(game=MagicMock())
        self.no_weapon = self.controller.get_empty_object_by_class_name('Weapon')

    def test_hit_chance_default(self):
        self.assertIsInstance(self.no_weapon.hit_chance, Dice)
        self.assertEqual(self.no_weapon.get_hit_chance(), 0)

    def test_weapon_type_default(self):
        self.assertIsNone(self.no_weapon.weapon_type)

    def test_real_weapon_overrides_defaults(self):
        weapon = self.controller.get_random_object_by_filters()
        self.assertIsInstance(weapon.hit_chance, Dice)
        self.assertIsNotNone(weapon.weapon_type)


class TestFightGetFighterByMethods(unittest.TestCase):
    """Выбор бойца по силе и здоровью должен уважать фильтр exclude."""

    class WeakSkeleton:
        def __init__(self, stren=0, health=0):
            self.stren = stren
            self.health = health

    class WeakGoblin:
        def __init__(self, stren=0, health=0):
            self.stren = stren
            self.health = health

    class StrongGoblin:
        def __init__(self, stren=0, health=0):
            self.stren = stren
            self.health = health

    @staticmethod
    def make_fight(fighters):
        fight = Fight.__new__(Fight)
        fight.fighters = fighters
        return fight

    def test_get_fighter_by_health_min_excludes_classes(self):
        excluded = self.WeakSkeleton(stren=10, health=1)
        target = self.WeakGoblin(stren=5, health=10)
        fight = self.make_fight([excluded, target])
        result = fight.get_fighter_by_health(who=None, exclude=['WeakSkeleton'], mode='Min')
        self.assertIs(result, target)

    def test_get_fighter_by_health_max_excludes_classes(self):
        excluded = self.StrongGoblin(stren=5, health=100)
        target = self.WeakSkeleton(stren=10, health=50)
        fight = self.make_fight([excluded, target])
        result = fight.get_fighter_by_health(who=None, exclude=['StrongGoblin'], mode='Max')
        self.assertIs(result, target)

    def test_get_fighter_by_strength_excludes_classes(self):
        excluded = self.WeakSkeleton(stren=100, health=10)
        target = self.WeakGoblin(stren=5, health=5)
        fight = self.make_fight([excluded, target])
        result = fight.get_fighter_by_strength(who=None, exclude=['WeakSkeleton'], mode='Max')
        self.assertIs(result, target)

    def test_excludes_who_itself(self):
        who = self.StrongGoblin(stren=100, health=100)
        target = self.WeakGoblin(stren=5, health=5)
        fight = self.make_fight([who, target])
        result = fight.get_fighter_by_strength(who=who, mode='Max')
        self.assertIs(result, target)

    def test_returns_false_when_all_excluded(self):
        excluded = self.WeakSkeleton(stren=10, health=10)
        fight = self.make_fight([excluded])
        result = fight.get_fighter_by_health(who=None, exclude=['WeakSkeleton'], mode='Max')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
