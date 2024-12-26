from src.controller_weapon import WeaponController
from src.class_game import Game

game = Game(123, 'bot')  # Replace 123 with the actual game ID
controller = WeaponController(game)

for _ in range(10):
    print (controller.get_random_object_by_filters())