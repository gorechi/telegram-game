import unittest
from src.class_dice import Dice

class TestDiceRoll(unittest.TestCase):

    def test_roll_with_single_die(self):
        dice = Dice([6])
        result = dice.roll()
        self.assertIn(result, range(1, 7))

    def test_roll_with_multiple_dice(self):
        dice = Dice([6, 8])
        result = dice.roll()
        self.assertIn(result, range(2, 15))

    def test_roll_with_modificator(self):
        dice = Dice([6], modificator=2)
        result = dice.roll()
        self.assertIn(result, range(3, 9))
    
    def test_roll_with_negative_modificator(self):
        dice = Dice([6], modificator=-2)
        result = dice.roll()
        self.assertIn(result, range(0, 5))

    def test_roll_with_big_negative_modificator(self):
        dice = Dice([6], modificator=-10)
        result = dice.roll()
        self.assertEqual(result, 0)
    
    def test_roll_with_no_dice(self):
        dice = Dice([]) 
        result = dice.roll()
        self.assertEqual(result, 0)

    def test_roll_with_invalid_die(self):
        dice = Dice([6, 'a'])
        with self.assertRaises(ValueError):
            dice.roll()

class TestDiceAddDie(unittest.TestCase):

    def test_add_valid_die(self):
        dice = Dice([])
        dice.add_die(6)
        self.assertIn(6, dice.dice)

    def test_add_multiple_dice(self):
        dice = Dice([4])
        dice.add_die(6)
        dice.add_die(8)
        self.assertEqual(dice.dice, [4, 6, 8])  

    def test_add_invalid_die(self):
        dice = Dice([])
        with self.assertRaises(ValueError) as context:
            dice.add_die('a')  
        self.assertEqual(str(context.exception), "Кубик должен быть целым числом больше нуля, а передан <class 'str'> a.")

    def test_add_negative_die(self):
        dice = Dice([])
        with self.assertRaises(ValueError) as context:
            dice.add_die(-6)  
        self.assertEqual(str(context.exception), "Кубик должен быть целым числом больше нуля, а передан <class 'int'> -6.")
        
    def test_add_zero_die(self):
        dice = Dice([])
        with self.assertRaises(ValueError) as context:
            dice.add_die(0)  
        self.assertEqual(str(context.exception), "Кубик должен быть целым числом больше нуля, а передан <class 'int'> 0.")
    
class TestDiceRemoveDie(unittest.TestCase):

    def test_remove_existing_die(self):
        dice = Dice([6, 8, 10])
        dice.remove_die(8)
        self.assertNotIn(8, dice.dice)
        
    def test_remove_non_existing_die(self):
        dice = Dice([6, 8, 10])
        with self.assertRaises(ValueError) as context:
            dice.remove_die(12)  
        self.assertEqual(str(context.exception), "Кубик 12 не найден в кубиках.")
    
    def test_remove_doubled_die(self):
        dice = Dice([6, 8, 10, 6])
        dice.remove_die(6)
        self.assertEqual(dice.dice, [8, 10, 6])

    def test_remove_invalid_die(self):
        dice = Dice([6, 8, 10])
        with self.assertRaises(ValueError) as context:
            dice.remove_die('a')
        self.assertEqual(str(context.exception), "Кубик должен быть целым числом, а передан <class 'str'> a.")

    def test_remove_die_from_empty_list(self):
        dice = Dice([])
        with self.assertRaises(ValueError) as context:
            dice.remove_die(6)
        self.assertEqual(str(context.exception), "Кубик 6 не найден в кубиках.")
    
class TestDiceGetText(unittest.TestCase):

    def test_no_dice(self):
        # Тестирование случая, когда нет кубиков
        dice = Dice([])
        result = dice.text()
        self.assertEqual(result, "Нет кубиков")  # Ожидаемое значение: "Нет кубиков"

    def test_dice_without_modificator(self):
        # Тестирование случая, когда есть кубики, но нет модификатора
        dice = Dice([6, 8, 10])
        result = dice.text()
        self.assertEqual(result, "d6 + d8 + d10")  # Ожидаемое значение: "d6 + d8 + d10"

    def test_dice_with_positive_modificator(self):
        # Тестирование случая, когда есть кубики и положительный модификатор
        dice = Dice([6, 8], modificator=3)
        result = dice.text()
        self.assertEqual(result, "d6 + d8 + 3")  # Ожидаемое значение: "d6 + d8 + 3"

    def test_dice_with_zero_modificator(self):
        # Тестирование случая, когда есть кубики и модификатор равен нулю
        dice = Dice([4, 12], modificator=0)
        result = dice.text()
        self.assertEqual(result, "d4 + d12")  # Ожидаемое значение: "d4 + d12"
        
    def test_dice_with_negative_modificator(self):
        # Тестирование случая, когда есть кубики и положительный модификатор
        dice = Dice([6, 8], modificator=-3)
        result = dice.text()
        self.assertEqual(result, "d6 + d8 - 3")  # Ожидаемое значение: "d6 + d8 + 3" 

class TestDiceIncreaseModificator(unittest.TestCase):

    def test_increase_with_positive_integer(self):
        # Тестирование увеличения модификатора положительным числом
        dice = Dice([6, 8], modificator=5)
        dice.increase_modificator(3)
        self.assertEqual(dice.modificator, 8)  # Ожидаемое значение: 8

    def test_increase_with_zero(self):
        # Тестирование случая, когда передан ноль
        dice = Dice([6, 8], modificator=5)
        dice.increase_modificator(0)
        self.assertEqual(dice.modificator, 5)  # Ожидаемое значение: 5

    def test_increase_with_negative_integer(self):
        # Тестирование случая, когда передано отрицательное число
        dice = Dice([6, 8], modificator=5)
        with self.assertRaises(ValueError) as context:
            dice.increase_modificator(-3)
        self.assertEqual(str(context.exception), "Значение должно быть больше или равно нулю.")

    def test_increase_with_non_integer(self):
        # Тестирование случая, когда передано не целое число
        dice = Dice([6, 8], modificator=5)
        with self.assertRaises(ValueError) as context:
            dice.increase_modificator(2.5)
        self.assertEqual(str(context.exception), "Значение должно быть целым числом, а передан <class 'float'> 2.5.")
    
class TestDiceDecreaseModificator(unittest.TestCase):

    def test_decrease_with_positive_integer(self):
        # Тестирование уменьшения модификатора положительным числом
        dice = Dice([6, 8], modificator=5)
        dice.decrease_modificator(3)
        self.assertEqual(dice.modificator, 2)  # Ожидаемое значение: 2

    def test_decrease_with_zero(self):
        # Тестирование случая, когда передан ноль
        dice = Dice([6, 8], modificator=5)
        dice.decrease_modificator(0)
        self.assertEqual(dice.modificator, 5)  # Ожидаемое значение: 5

    def test_decrease_with_negative_integer(self):
        # Тестирование случая, когда передано отрицательное число
        dice = Dice([6, 8], modificator=5)
        with self.assertRaises(ValueError) as context:
            dice.decrease_modificator(-3)
        self.assertEqual(str(context.exception), "Значение должно быть больше или равно нулю.")

    def test_decrease_with_non_integer(self):
        # Тестирование случая, когда передано не целое число
        dice = Dice([6, 8], modificator=5)
        with self.assertRaises(ValueError) as context:
            dice.decrease_modificator(2.5)
        self.assertEqual(str(context.exception), "Значение должно быть целым числом, а передан <class 'float'> 2.5.")

    def test_decrease_to_negative_modificator(self):
        # Тестирование случая, когда уменьшение приводит к отрицательному модификатору
        dice = Dice([6, 8], modificator=3)
        dice.decrease_modificator(4)
        self.assertEqual(dice.modificator, -1)  # Ожидаемое значение: 0
        
if __name__ == '__main__':
    unittest.main()