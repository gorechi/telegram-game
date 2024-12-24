import unittest
from src.controller_monsters import MonstersController
from src.class_dice import Dice

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
        data = {'random': [1, 10]}
        result = self.controller.generate_value(data)
        self.assertIn(result, range(1, 11))
    
    def test_random_range_with_value(self):
        # Тестирование случая, когда входные данные содержат диапазон случайных значений
        data = {'random': [1, 10], 'value': 12}
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
        data = {'dice': True, 'random': [1, 10]}
        result = self.controller.generate_value(data)
        self.assertIsInstance(result, Dice)
        self.assertEqual(len(result.dice), 1)
        self.assertIn(result.dice[0], range(1, 11))  # Ожидаемое значение: в диапазоне от 1 до 10

    def test_simple_value(self):
        # Тестирование случая, когда входные данные содержат простое значение
        data = {'value': 5}
        result = self.controller.generate_value(data)
        self.assertEqual(result, {'value': 5})  # Ожидаемое значение: {'value': 5}

if __name__ == '__main__':
    unittest.main()