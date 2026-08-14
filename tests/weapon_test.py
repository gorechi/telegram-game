import unittest
from unittest.mock import MagicMock
from src.controllers.controller_weapon import WeaponController


class TestWeaponCheckName(unittest.TestCase):
    
    def setUp(self):
        self.mock_game = MagicMock()
        
        self.controller = WeaponController(self.mock_game)
        
        self.weapon = self.controller.get_random_object_by_filters()
        
        self.weapon.lexemes = {
            'nom': 'меч',
            'accus': 'меча'
        }
        
        self.weapon.empty = False

    def test_check_name_weapon_empty(self):
        self.weapon.empty = True
        self.assertFalse(self.weapon.check_name('меч'))

    def test_check_name_message_matches(self):
        self.assertTrue(self.weapon.check_name('меч'))
        self.assertTrue(self.weapon.check_name('меча'))

    def test_check_name_message_does_not_match(self):
        self.assertFalse(self.weapon.check_name('лук'))

    def test_check_name_case_insensitivity(self):
        self.assertTrue(self.weapon.check_name('МЕЧ'))
        self.assertTrue(self.weapon.check_name('МЕЧА'))
        
    def test_check_name_substring(self):
        self.assertTrue(self.weapon.check_name('ме'))
        self.assertFalse(self.weapon.check_name('мю'))
        

class TestWeaponAttack(unittest.TestCase):
    
    def setUp(self):
        self.mock_game = MagicMock()
        
        self.controller = WeaponController(self.mock_game)
        
        self.weapon = self.controller.get_random_object_by_filters()
        
        self.weapon.damage.set_dice([6])
        self.weapon.damage.set_modifier(0)
        
        self.mock_monster = MagicMock()

    def attack_with_coefficient(self, coefficient, base_damage):
        self.weapon.damage.roll = lambda: base_damage
        self.mock_monster.get_weakness.return_value = coefficient
        return self.weapon.attack(self.mock_monster)

    def test_attack_with_no_weakness(self):
        self.mock_monster.get_weakness.return_value = 1
        damage = self.weapon.attack(self.mock_monster)
        self.assertIn(damage, [1, 2, 3, 4, 5, 6])

    def test_attack_multiplies_base_damage(self):
        damage = self.attack_with_coefficient(1.1, 10)
        self.assertEqual(damage, 11)

    def test_attack_resistance_reduces_damage(self):
        damage = self.attack_with_coefficient(0.3, 10)
        self.assertEqual(damage, 3)

    def test_attack_rounds_down_when_fraction_below_half(self):
        damage = self.attack_with_coefficient(1.2, 7)
        self.assertEqual(damage, 8)

    def test_attack_rounds_up_when_fraction_is_half(self):
        damage = self.attack_with_coefficient(1.25, 6)
        self.assertEqual(damage, 8)

    def test_attack_rounds_half_up_not_bankers(self):
        damage = self.attack_with_coefficient(0.25, 10)
        self.assertEqual(damage, 3)

    def test_attack_rounds_up_when_fraction_above_half(self):
        damage = self.attack_with_coefficient(1.19, 10)
        self.assertEqual(damage, 12)

if __name__ == '__main__':
    unittest.main()