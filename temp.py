from src.class_allies import Trader
from src.class_game import Game

new_game = Game(100, 100)
new_tarder = Trader.random_trader(new_game, "floor")
print (new_tarder)
print(new_tarder.lexemes)