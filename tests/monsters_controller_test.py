import unittest
from src.controllers.controller_monsters import MonstersController
from src.class_monsters import Monster
from src.class_dice import Dice


class FakeGame:
    no_weapon = None
    no_shield = None
    no_armor = None


class FakeWeaponController:
    """Заглушка weapon_controller: on_create присваивает результат атрибуту weapon и не использует его дальше."""

    def __init__(self):
        self.calls = 0

    def get_random_object_by_filters(self, **filters):
        self.calls += 1
        return object()

class TestGenerateValue(unittest.TestCase):

    def setUp(self):
        # Создаем экземпляр MonstersController для использования в тестах
        self.controller = MonstersController(game=None)

    def test_non_dict_input(self):
        # Тестирование случая, когда входные данные не являются словарем
        result = self.controller.generate_value(10)
        self.assertEqual(result, 10)  # Ожидаемое значение: 10

    def test_string_input(self):
        # Тестирование случая, когда входные данные не являются словарем
        result = self.controller.generate_value('10')
        self.assertEqual(result, '10')
    
    def test_list_input(self):
        # Тестирование случая, когда входные данные не являются словарем
        result = self.controller.generate_value([10, 'a'])
        self.assertEqual(result, [10, 'a'])
        
    def test_some_dict_input(self):
        # Тестирование случая, когда входные данные не являются словарем
        result = self.controller.generate_value({'key1': 'value1', 'key2': 'value2'})
        self.assertEqual(result, {'key1': 'value1', 'key2': 'value2'})
    
    def test_random_range(self):
        # Тестирование случая, когда входные данные содержат диапазон случайных значений
        data = {'random': True, 'value': [1, 10]}
        result = self.controller.generate_value(data)
        self.assertIn(result, range(1, 11))
    
    def test_random_range_with_value(self):
        # Тестирование случая, когда входные данные содержат диапазон случайных значений
        data = {'random': True, 'value': [1, 10]}
        result = self.controller.generate_value(data)
        self.assertIn(result, range(1, 11))# Ожидаемое значение: в диапазоне от 1 до 10

    def test_dice_value(self):
        # Тестирование случая, когда входные данные содержат значение для кубика
        data = {'dice': True, 'value': 6}
        result = self.controller.generate_value(data)
        self.assertIsInstance(result, Dice)  # Ожидаемое значение: экземпляр Dice
        self.assertEqual(result.dice, [6])
        
    def test_random_die(self):
        # Тестирование случая, когда входные данные содержат значение для кубика
        data = {'dice': True, 'random': True, 'value': [1, 10]}
        result = self.controller.generate_value(data)
        self.assertIsInstance(result, Dice)
        self.assertEqual(len(result.dice), 1)
        self.assertIn(result.dice[0], range(1, 11))  # Ожидаемое значение: в диапазоне от 1 до 10

    def test_simple_value(self):
        # Тестирование случая, когда входные данные содержат простое значение
        data = {'value': 5}
        result = self.controller.generate_value(data)
        self.assertEqual(result, {'value': 5})  # Ожидаемое значение: {'value': 5}

class TestMonsterAccounting(unittest.TestCase):
    """Тесты учета монстров: kill_monster, resurrect_monster, check_endgame."""

    def setUp(self):
        self.controller = MonstersController(game=None)
        self.monster_1 = Monster(game=FakeGame())
        self.monster_2 = Monster(game=FakeGame())

    def test_kill_monster_removes_and_decrements(self):
        self.controller.all_objects = [self.monster_1, self.monster_2]
        self.controller.how_many = 2
        result = self.controller.kill_monster(self.monster_1)
        self.assertTrue(result)
        self.assertEqual(self.controller.all_objects, [self.monster_2])
        self.assertEqual(self.controller.how_many, 1)

    def test_kill_monster_missing_monster_no_error(self):
        self.controller.all_objects = [self.monster_1]
        self.controller.how_many = 1
        result = self.controller.kill_monster(self.monster_2)
        self.assertTrue(result)
        self.assertEqual(self.controller.all_objects, [self.monster_1])
        self.assertEqual(self.controller.how_many, 1)

    def test_kill_monster_non_monster_raises(self):
        self.controller.all_objects = []
        self.controller.how_many = 0
        with self.assertRaises(TypeError):
            self.controller.kill_monster('not_a_monster')

    def test_resurrect_monster_adds_and_increments(self):
        self.controller.all_objects = [self.monster_1]
        self.controller.how_many = 1
        result = self.controller.resurrect_monster(self.monster_2)
        self.assertTrue(result)
        self.assertEqual(self.controller.all_objects, [self.monster_1, self.monster_2])
        self.assertEqual(self.controller.how_many, 2)

    def test_resurrect_monster_non_monster_raises(self):
        with self.assertRaises(TypeError):
            self.controller.resurrect_monster('not_a_monster')

    def test_check_endgame_true_when_all_killed(self):
        self.controller.all_objects = [self.monster_1]
        self.controller.how_many = 1
        self.controller.kill_monster(self.monster_1)
        self.assertEqual(self.controller.how_many, 0)
        self.assertTrue(self.controller.check_endgame())

    def test_check_endgame_false_when_monsters_remain(self):
        self.controller.all_objects = [self.monster_1, self.monster_2]
        self.controller.how_many = 2
        self.controller.kill_monster(self.monster_1)
        self.assertEqual(self.controller.how_many, 1)
        self.assertFalse(self.controller.check_endgame())

    def test_kill_resurrect_cycle(self):
        self.controller.all_objects = [self.monster_1]
        self.controller.how_many = 1
        self.controller.kill_monster(self.monster_1)
        self.controller.resurrect_monster(self.monster_1)
        self.assertEqual(self.controller.all_objects, [self.monster_1])
        self.assertEqual(self.controller.how_many, 1)


class TestMonsterOnCreate(unittest.TestCase):
    """Тесты инициализации start_health в on_create для всех монстров."""

    def setUp(self):
        self.game = FakeGame()
        self.game.weapon_controller = FakeWeaponController()

    def test_on_create_sets_start_health_without_weapon(self):
        monster = Monster(game=self.game)
        monster.preferred_weapon = ''
        monster.health = 20
        monster.stren = Dice([5])
        monster.on_create()
        self.assertEqual(monster.start_health, 20)
        self.assertTrue(monster.exp > 0)
        self.assertEqual(self.game.weapon_controller.calls, 0)

    def test_on_create_sets_start_health_with_weapon(self):
        monster = Monster(game=self.game)
        monster.preferred_weapon = 'колющее'
        monster.health = 20
        monster.stren = Dice([5])
        monster.on_create()
        self.assertEqual(monster.start_health, 20)
        self.assertEqual(self.game.weapon_controller.calls, 1)
        self.assertTrue(monster.exp > 0)

    def test_all_templates_get_start_health(self):
        controller = MonstersController(game=self.game)
        for template in controller.templates:
            monster = controller.create_object_from_template(template)
            self.assertTrue(hasattr(monster, 'start_health'),
                            f'Монстр {template.name} не получил start_health')
            self.assertEqual(monster.start_health, monster.health,
                             f'Монстр {template.name}: start_health != health')
            self.assertTrue(monster.exp > 0,
                            f'Монстр {template.name} не получил exp')


if __name__ == '__main__':
    unittest.main()
