import unittest
from unittest.mock import MagicMock
from class_fight import Fight

class TestFight(unittest.TestCase):

    def setUp(self):
        # Mock game and hero objects
        self.game = MagicMock()
        self.hero = MagicMock()

    def test_all_fighters_have_light(self):
        # Create mock fighters with light
        fighters = [MagicMock(check_light=MagicMock(return_value=True)) for _ in range(3)]
        
        # Initialize Fight instance
        fight = Fight(self.game, self.hero, fighters[0], fighters)
        
        # Test check_light method
        self.assertTrue(fight.check_light())

    def test_some_fighters_have_light(self):
        # Create mock fighters, some with light
        fighters = [
            MagicMock(check_light=MagicMock(return_value=False)),
            MagicMock(check_light=MagicMock(return_value=True)),
            MagicMock(check_light=MagicMock(return_value=False))
        ]
        
        # Initialize Fight instance
        fight = Fight(self.game, self.hero, fighters[0], fighters)
        
        # Test check_light method
        self.assertTrue(fight.check_light())

    def test_no_fighters_have_light(self):
        # Create mock fighters without light
        fighters = [MagicMock(check_light=MagicMock(return_value=False)) for _ in range(3)]
        
        # Initialize Fight instance
        fight = Fight(self.game, self.hero, fighters[0], fighters)
        
        # Test check_light method
        self.assertFalse(fight.check_light())

if __name__ == '__main__':
    unittest.main()