import unittest
from unittest.mock import MagicMock, patch
from src.class_potions import (
    Potion, HealPotion, HealthPotion, StrengthPotion,
    StrengtheningPotion, DexterityPotion, EvasionPotion,
    IntelligencePotion, EnlightmentPotion, Antidote
)
from src.controllers.controller_potions import PotionsController
from src.class_dice import Dice


def make_hero(name='Герой', no_backpack=False):
    hero = MagicMock()
    hero.name = name
    hero.g = lambda m, f: m
    hero.backpack = MagicMock()
    hero.backpack.no_backpack = no_backpack
    hero.current_position = MagicMock()
    hero.current_position.light = True
    hero.action_controller = MagicMock()
    hero.health = 10
    hero.start_health = 10
    hero.poisoned = False
    hero.fear = 0
    hero.__format__ = lambda self, fmt: name
    return hero


def make_potion(cls, game=None, effect=5):
    game = game or MagicMock()
    p = cls(game)
    p.effect = effect
    p.description = 'Тестовое зелье'
    p.name = 'Зелье'
    p.lexemes = {
        'nom': 'зелье', 'accus': 'зелье',
        'gen': 'зелья', 'dat': 'зелью',
        'prep': 'зелье', 'inst': 'зельем'
    }
    return p


def make_heal_potion(game=None, dice_value=5):
    game = game or MagicMock()
    p = HealPotion(game)
    p.effect = Dice([dice_value])
    p.description = 'Тестовое зелье лечения'
    p.name = 'Зелье исцеления'
    p.lexemes = {
        'nom': 'зелье исцеления',
        'accus': 'зелье исцеления',
        'gen': 'зелья исцеления',
        'dat': 'зелью исцеления',
        'prep': 'зелье исцеления',
        'inst': 'зельем исцеления'
    }
    return p


class TestPotionInit(unittest.TestCase):
    def test_default_attributes(self):
        p = Potion(MagicMock())
        self.assertFalse(p.empty)
        self.assertIsNone(p.owner)

    def test_hero_actions_keys(self):
        p = Potion(MagicMock())
        self.assertEqual(set(p.hero_actions.keys()), {'бросить', 'выбросить', 'оставить'})

    def test_room_actions_keys(self):
        p = Potion(MagicMock())
        self.assertEqual(set(p.room_actions.keys()), {'взять', 'брать', 'собрать'})

    def test_drop_methods(self):
        p = Potion(MagicMock())
        for v in p.hero_actions.values():
            self.assertEqual(v['method'], 'drop')

    def test_take_methods(self):
        p = Potion(MagicMock())
        for v in p.room_actions.values():
            self.assertEqual(v['method'], 'take')

    def test_drop_not_in_combat(self):
        p = Potion(MagicMock())
        for v in p.hero_actions.values():
            self.assertFalse(v['in_combat'])

    def test_take_not_in_combat(self):
        p = Potion(MagicMock())
        for v in p.room_actions.values():
            self.assertFalse(v['in_combat'])

    def test_take_bulk(self):
        p = Potion(MagicMock())
        for v in p.room_actions.values():
            self.assertTrue(v['bulk'])

    def test_drop_not_bulk(self):
        p = Potion(MagicMock())
        for v in p.hero_actions.values():
            self.assertFalse(v['bulk'])

    def test_drop_in_darkness(self):
        p = Potion(MagicMock())
        for v in p.hero_actions.values():
            self.assertTrue(v['in_darkness'])

    def test_take_not_in_darkness(self):
        p = Potion(MagicMock())
        for v in p.room_actions.values():
            self.assertFalse(v['in_darkness'])


class TestPotionFormat(unittest.TestCase):
    def test_format_known_case(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'зелье', 'accus': 'зелью'}
        self.assertEqual(f'{p:nom}', 'зелье')
        self.assertEqual(f'{p:accus}', 'зелью')

    def test_format_unknown_case(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'зелье'}
        self.assertEqual(f'{p:dat}', '')


class TestPotionStr(unittest.TestCase):
    def test_returns_description(self):
        p = Potion(MagicMock())
        p.description = 'Описание'
        self.assertEqual(str(p), 'Описание')


class TestPotionCheckName(unittest.TestCase):
    def test_exact_match(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'противоядие', 'accus': 'противоядие'}
        self.assertTrue(p.check_name('противоядие'))

    def test_case_insensitive(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'abc', 'accus': 'abc'}
        self.assertTrue(p.check_name('ABC'))

    def test_wrong_name(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'x', 'accus': 'x'}
        self.assertFalse(p.check_name('y'))


class TestPotionGetNamesList(unittest.TestCase):
    def test_base_names(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'название', 'accus': 'название'}
        names = p.get_names_list(['nom', 'accus'])
        self.assertIn('название', names)

    def test_empty_cases(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'n'}
        names = p.get_names_list([])
        self.assertEqual(len(names), 2)


class TestPotionOnCreate(unittest.TestCase):
    def test_returns_true(self):
        self.assertTrue(Potion(MagicMock()).on_create())


class TestPotionShow(unittest.TestCase):
    def test_returns_description(self):
        p = Potion(MagicMock())
        p.description = 'Desc'
        self.assertEqual(p.show(), 'Desc')


class TestPotionPlace(unittest.TestCase):
    def test_place_in_specific_place(self):
        p = Potion(MagicMock())
        place = MagicMock()
        place.action_controller = MagicMock()
        result = p.place(MagicMock(), place=place)
        self.assertTrue(result)
        place.add.assert_called_once_with(p)
        place.action_controller.add_actions.assert_called_once_with(p)

    def test_place_in_room_with_furniture(self):
        p = Potion(MagicMock())
        castle = MagicMock()
        furn = MagicMock()
        furn.action_controller = MagicMock()
        room = MagicMock()
        room.furniture = [furn]
        castle.plan = [room]
        with patch('src.class_potions.randomitem', side_effect=[room, furn]):
            result = p.place(castle)
        self.assertTrue(result)
        furn.add.assert_called_once_with(p)

    def test_place_in_room_without_furniture(self):
        p = Potion(MagicMock())
        castle = MagicMock()
        room = MagicMock()
        room.furniture = []
        room.action_controller = MagicMock()
        castle.plan = [room]
        with patch('src.class_potions.randomitem', return_value=room):
            result = p.place(castle)
        self.assertTrue(result)
        room.add.assert_called_once_with(p)

    def test_place_room_no_action_controller(self):
        p = Potion(MagicMock())
        castle = MagicMock()
        room = MagicMock()
        room.furniture = []
        del room.action_controller
        castle.plan = [room]
        with patch('src.class_potions.randomitem', return_value=room):
            result = p.place(castle)
        self.assertTrue(result)
        room.add.assert_called_once_with(p)


class TestPotionTake(unittest.TestCase):
    def test_take_with_backpack(self):
        p = Potion(MagicMock())
        p.lexemes = {'nom': 'a', 'accus': 'b'}
        hero = MagicMock()
        hero.backpack = MagicMock()
        hero.backpack.no_backpack = False
        hero.name = 'Герой'
        hero.g = MagicMock(return_value='em')
        msg = p.take(hero)
        self.assertIn('Герой', msg)
        hero.put_in_backpack.assert_called_once_with(p)

    def test_take_without_backpack(self):
        p = Potion(MagicMock())
        hero = MagicMock()
        hero.name = 'Герой'
        hero.g = MagicMock(return_value='em')
        hero.backpack = MagicMock()
        hero.backpack.no_backpack = True
        msg = p.take(hero)
        self.assertIn('не может', msg)


class TestPotionDrop(unittest.TestCase):
    def test_drop(self):
        p = Potion(MagicMock())
        hero = make_hero()
        msg = p.drop(hero)
        self.assertIn('Герой', msg)
        hero.current_position.loot.add.assert_called_once_with(p)
        hero.backpack.remove.assert_called_once_with(item=p, place=hero.current_position)
        hero.current_position.action_controller.add_actions.assert_called_once_with(p)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(p)


class TestHealPotionUse(unittest.TestCase):
    def test_use_in_combat_heals(self):
        hero = make_hero()
        hero.health = 5
        hero.start_health = 10
        p = make_heal_potion(dice_value=3)
        msg = p.use(hero, in_action=True)
        self.assertEqual(hero.health, 8)
        self.assertIn('восполняет', msg)

    def test_use_outside_combat_blocked(self):
        hero = make_hero()
        p = make_heal_potion()
        msg = p.use(hero, in_action=False)
        self.assertIn('только в бою', msg)

    def test_use_heals_to_max(self):
        hero = make_hero()
        hero.health = 9
        hero.start_health = 10
        p = make_heal_potion(dice_value=5)
        msg = p.use(hero, in_action=True)
        self.assertEqual(hero.health, 10)

    def test_use_full_health_zero(self):
        hero = make_hero()
        hero.health = 10
        hero.start_health = 10
        p = make_heal_potion(dice_value=5)
        msg = p.use(hero, in_action=True)
        self.assertEqual(hero.health, 10)
        self.assertIn('0', msg)

    def test_use_cures_poison(self):
        hero = make_hero()
        hero.health = 5
        hero.start_health = 10
        hero.poisoned = True
        p = make_heal_potion(dice_value=3)
        msg = p.use(hero, in_action=True)
        self.assertFalse(hero.poisoned)
        self.assertIn('излечивается', msg)

    def test_use_removes_item(self):
        hero = make_hero()
        hero.health = 5
        hero.start_health = 10
        p = make_heal_potion(dice_value=3)
        p.use(hero, in_action=True)
        hero.backpack.remove.assert_called_once_with(p)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(p)

    def test_hero_actions_keys(self):
        p = make_heal_potion()
        for key in ['пить', 'выпить', 'попить']:
            self.assertIn(key, p.hero_actions)
            self.assertTrue(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['method'], 'use')
            self.assertEqual(p.hero_actions[key]['duration'], 1)


class TestHealthPotionUse(unittest.TestCase):
    def test_use_outside_combat(self):
        hero = make_hero()
        p = make_potion(HealthPotion, effect=1)
        msg = p.use(hero, in_action=False)
        self.assertEqual(hero.start_health, 11)
        self.assertEqual(hero.health, 11)
        self.assertIn('увеличивает', msg)

    def test_use_in_combat_blocked(self):
        hero = make_hero()
        p = make_potion(HealthPotion)
        msg = p.use(hero, in_action=True)
        self.assertIn('нельзя использовать в бою', msg)

    def test_use_removes_item(self):
        hero = make_hero()
        p = make_potion(HealthPotion, effect=1)
        p.use(hero, in_action=False)
        hero.backpack.remove.assert_called_once_with(p)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(p)

    def test_hero_actions_not_in_combat(self):
        p = make_potion(HealthPotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertFalse(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['duration'], 1)


class TestStrengthPotionUse(unittest.TestCase):
    def test_use_outside_combat(self):
        hero = make_hero()
        p = make_potion(StrengthPotion, effect=1)
        msg = p.use(hero, in_action=False)
        hero.stren.increase_base_die.assert_called_once_with(1)
        hero.start_stren.increase_base_die.assert_called_once_with(1)
        self.assertIn('увеличивает', msg)

    def test_use_in_combat_blocked(self):
        hero = make_hero()
        p = make_potion(StrengthPotion)
        msg = p.use(hero, in_action=True)
        self.assertIn('нельзя использовать в бою', msg)

    def test_hero_actions(self):
        p = make_potion(StrengthPotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertFalse(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['duration'], 1)


class TestStrengtheningPotionUse(unittest.TestCase):
    def test_use_in_combat(self):
        hero = make_hero()
        p = make_potion(StrengtheningPotion, effect=5)
        msg = p.use(hero, in_action=True)
        hero.stren.add_temporary.assert_called_once_with(5)
        self.assertIn('На время боя', msg)

    def test_use_outside_combat_blocked(self):
        hero = make_hero()
        p = make_potion(StrengtheningPotion)
        msg = p.use(hero, in_action=False)
        self.assertIn('только в бою', msg)

    def test_hero_actions(self):
        p = make_potion(StrengtheningPotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertTrue(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['method'], 'use')

    def test_removes_item(self):
        hero = make_hero()
        p = make_potion(StrengtheningPotion, effect=5)
        p.use(hero, in_action=True)
        hero.backpack.remove.assert_called_once_with(p)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(p)


class TestDexterityPotionUse(unittest.TestCase):
    def test_use_outside_combat(self):
        hero = make_hero()
        p = make_potion(DexterityPotion, effect=1)
        msg = p.use(hero, in_action=False)
        hero.dext.increase_base_die.assert_called_once_with(1)
        hero.start_dext.increase_base_die.assert_called_once_with(1)
        self.assertIn('увеличивает', msg)

    def test_use_in_combat_blocked(self):
        hero = make_hero()
        p = make_potion(DexterityPotion)
        msg = p.use(hero, in_action=True)
        self.assertIn('нельзя использовать в бою', msg)

    def test_hero_actions(self):
        p = make_potion(DexterityPotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertFalse(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['duration'], 1)


class TestEvasionPotionUse(unittest.TestCase):
    def test_use_in_combat(self):
        hero = make_hero()
        p = make_potion(EvasionPotion, effect=5)
        msg = p.use(hero, in_action=True)
        hero.dext.add_temporary.assert_called_once_with(5)
        self.assertIn('На время боя', msg)

    def test_use_outside_combat_blocked(self):
        hero = make_hero()
        p = make_potion(EvasionPotion)
        msg = p.use(hero, in_action=False)
        self.assertIn('только в бою', msg)

    def test_hero_actions(self):
        p = make_potion(EvasionPotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertTrue(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['method'], 'use')


class TestIntelligencePotionUse(unittest.TestCase):
    def test_use_outside_combat(self):
        hero = make_hero()
        p = make_potion(IntelligencePotion, effect=1)
        msg = p.use(hero, in_action=False)
        hero.intel.increase_base_die.assert_called_once_with(1)
        hero.start_intel.increase_base_die.assert_called_once_with(1)
        self.assertIn('увеличивает', msg)

    def test_use_in_combat_blocked(self):
        hero = make_hero()
        p = make_potion(IntelligencePotion)
        msg = p.use(hero, in_action=True)
        self.assertIn('нельзя использовать в бою', msg)

    def test_hero_actions(self):
        p = make_potion(IntelligencePotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertFalse(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['duration'], 1)


class TestEnlightmentPotionUse(unittest.TestCase):
    def test_use_in_combat(self):
        hero = make_hero()
        p = make_potion(EnlightmentPotion, effect=5)
        msg = p.use(hero, in_action=True)
        hero.intel.add_temporary.assert_called_once_with(5)
        self.assertIn('На время боя', msg)

    def test_use_outside_combat_blocked(self):
        hero = make_hero()
        p = make_potion(EnlightmentPotion)
        msg = p.use(hero, in_action=False)
        self.assertIn('только в бою', msg)

    def test_hero_actions(self):
        p = make_potion(EnlightmentPotion)
        for key in ['пить', 'выпить', 'попить']:
            self.assertTrue(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['method'], 'use')


class TestAntidoteUse(unittest.TestCase):
    def test_use_poisoned(self):
        hero = make_hero()
        hero.poisoned = True
        hero.fear = 3
        p = make_potion(Antidote)
        msg = p.use(hero)
        self.assertFalse(hero.poisoned)
        self.assertEqual(hero.fear, 0)
        self.assertIn('излечивается', msg)

    def test_use_fearful(self):
        hero = make_hero()
        hero.poisoned = False
        hero.fear = 5
        p = make_potion(Antidote)
        msg = p.use(hero)
        self.assertEqual(hero.fear, 0)
        self.assertIn('избавляется', msg)

    def test_use_healthy_declines(self):
        hero = make_hero()
        hero.poisoned = False
        hero.fear = 0
        p = make_potion(Antidote)
        msg = p.use(hero)
        self.assertIn('не чувствует', msg)
        hero.backpack.remove.assert_not_called()

    def test_use_removes_item(self):
        hero = make_hero()
        hero.poisoned = True
        p = make_potion(Antidote)
        p.use(hero)
        hero.backpack.remove.assert_called_once_with(p)
        hero.action_controller.delete_actions_by_item.assert_called_once_with(p)

    def test_use_both_poisoned_and_fearful(self):
        hero = make_hero()
        hero.poisoned = True
        hero.fear = 7
        p = make_potion(Antidote)
        msg = p.use(hero)
        self.assertFalse(hero.poisoned)
        self.assertEqual(hero.fear, 0)

    def test_hero_actions(self):
        p = make_potion(Antidote)
        for key in ['пить', 'выпить', 'попить']:
            self.assertTrue(p.hero_actions[key]['in_combat'])
            self.assertEqual(p.hero_actions[key]['method'], 'use')
            self.assertEqual(p.hero_actions[key]['duration'], 1)


class TestPotionsController(unittest.TestCase):
    def test_init_loads_templates(self):
        ctrl = PotionsController(game=MagicMock())
        self.assertGreater(len(ctrl.templates), 0)
        self.assertEqual(len(ctrl.all_objects), 0)
        self.assertEqual(ctrl.how_many, 0)

    def test_additional_actions_returns_true(self):
        ctrl = PotionsController(game=MagicMock())
        self.assertTrue(ctrl.additional_actions(MagicMock()))

    def test_create_heal_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('HealPotion', 1)
        self.assertEqual(len(objs), 1)
        p = objs[0]
        self.assertIsInstance(p, HealPotion)
        self.assertIsInstance(p.effect, Dice)
        self.assertTrue(p.can_use_in_fight)
        self.assertFalse(p.enchantable)

    def test_create_health_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('HealthPotion', 1)
        p = objs[0]
        self.assertIsInstance(p, HealthPotion)
        self.assertFalse(p.can_use_in_fight)
        self.assertIsInstance(p.effect, int)

    def test_create_strength_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('StrengthPotion', 1)
        self.assertIsInstance(objs[0], StrengthPotion)

    def test_create_strengthening_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('StrengtheningPotion', 1)
        p = objs[0]
        self.assertIsInstance(p, StrengtheningPotion)
        self.assertTrue(p.can_use_in_fight)

    def test_create_dexterity_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('DexterityPotion', 1)
        self.assertIsInstance(objs[0], DexterityPotion)

    def test_create_evasion_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('EvasionPotion', 1)
        p = objs[0]
        self.assertIsInstance(p, EvasionPotion)
        self.assertTrue(p.can_use_in_fight)

    def test_create_intelligence_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('IntelligencePotion', 1)
        self.assertIsInstance(objs[0], IntelligencePotion)

    def test_create_enlightment_potion(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('EnlightmentPotion', 1)
        p = objs[0]
        self.assertIsInstance(p, EnlightmentPotion)
        self.assertTrue(p.can_use_in_fight)

    def test_create_antidote(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('Antidote', 1)
        p = objs[0]
        self.assertIsInstance(p, Antidote)
        self.assertTrue(p.can_use_in_fight)

    def test_create_multiple_objects(self):
        ctrl = PotionsController(game=MagicMock())
        objs = ctrl.get_random_objects_by_class_name('HealthPotion', 3)
        self.assertEqual(len(objs), 3)
        self.assertEqual(ctrl.how_many, 3)
        self.assertEqual(len(ctrl.all_objects), 3)

    def test_all_classes_registered(self):
        ctrl = PotionsController(game=MagicMock())
        expected = {'Potion', 'HealPotion', 'HealthPotion', 'StrengtheningPotion',
                    'StrengthPotion', 'IntelligencePotion', 'EnlightmentPotion',
                    'DexterityPotion', 'EvasionPotion', 'Antidote'}
        self.assertEqual(set(ctrl._classes.keys()), expected)

    def test_get_random_object_by_filters(self):
        ctrl = PotionsController(game=MagicMock())
        p = ctrl.get_random_object_by_filters(can_use_in_fight=True)
        self.assertTrue(p.can_use_in_fight)

    def test_load_templates_from_json(self):
        ctrl = PotionsController(game=MagicMock())
        names = [t.class_name for t in ctrl.templates]
        self.assertIn('HealPotion', names)
        self.assertIn('HealthPotion', names)
        self.assertIn('Antidote', names)

    def test_all_objects_tracked(self):
        ctrl = PotionsController(game=MagicMock())
        ctrl.get_random_objects_by_class_name('HealPotion', 2)
        ctrl.get_random_objects_by_class_name('HealthPotion', 1)
        self.assertEqual(ctrl.how_many, 3)
        self.assertEqual(len(ctrl.all_objects), 3)

    def test_all_potions_have_actions(self):
        ctrl = PotionsController(game=MagicMock())
        for template in ctrl.templates:
            if template.class_name == 'Potion':
                continue
            obj = ctrl.create_object_from_template(template)
            self.assertIn('пить', obj.hero_actions)
            self.assertIn('выпить', obj.hero_actions)
            self.assertIn('попить', obj.hero_actions)
            self.assertIn('бросить', obj.hero_actions)

    def test_templates_have_enchantable_field(self):
        ctrl = PotionsController(game=MagicMock())
        for template in ctrl.templates:
            self.assertTrue(hasattr(template, 'enchantable'))


if __name__ == '__main__':
    unittest.main()