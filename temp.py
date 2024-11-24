from class_game import Game
from class_hero import Hero

game = Game('sdfsd', '')
hero = Hero(game, 'qq')

print(hero.health, hero.stren, hero.dext, hero.intel)
hero.levelup('здоровье')
print(hero.health, hero.stren, hero.dext, hero.intel)
hero.levelup('силу')
print(hero.health, hero.stren, hero.dext, hero.intel)
hero.levelup('ловкость')
print(hero.health, hero.stren, hero.dext, hero.intel)
hero.levelup('интеллект')
print(hero.health, hero.stren, hero.dext, hero.intel)
hero.levelup('11')
print(hero.health, hero.stren, hero.dext, hero.intel)