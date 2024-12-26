import unittest
from unittest.mock import MagicMock
from src.controller_weapon import WeaponController


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
        self.weapon.damage.set_modificator(0)
        
        self.mock_monster = MagicMock()

    def test_attack_with_negative_weakness(self):
        self.mock_monster.get_weakness.return_value = -1
        damage = self.weapon.attack(self.mock_monster)
        self.assertIn(damage, [0, 1, 2, 3, 4, 5])

    def test_attack_with_positive_weakness(self):
        self.mock_monster.get_weakness.return_value = 1              
        damage = self.weapon.attack(self.mock_monster)
        self.assertIn(damage, [2, 3, 4, 5, 6, 7])

    def test_attack_with_no_weakness(self):
        self.mock_monster.get_weakness.return_value = 0
        damage = self.weapon.attack(self.mock_monster)
        self.assertIn(damage, [1, 2, 3, 4, 5, 6])

if __name__ == '__main__':
    unittest.main()