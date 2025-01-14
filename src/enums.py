from enum import Enum

class state_enum(Enum):
    """
    Текущее состояние персонажа:
    - NO_STATE - обычное состояние. Персонаж ходит, исследует и т.п.
    - FIGHT - происходит бой
    - ENCHANT - персонаж что-то улучшает
    - LEVEL_UP - персонаж поднимает уровень
    - USE_IN_FIGHT - персонадж использует вещь во время боя
    - TRADE - персонаж торгует
    - READ - персонаж выбирает, что ему почитать
    - DRINK - персонаж выбирает, что ему выпть
    """
    NO_STATE = 0
    FIGHT = 1
    ENCHANT = 2
    LEVEL_UP = 3
    USE_IN_FIGHT = 4
    TRADE = 5
    DRINK = 7
    ACTION = 8

class move_enum(Enum):
    """
    Передвижение игрока
    """
    UP = (0, 2)
    RIGHT = (1, 3)
    DOWN = (2, 0)
    LEFT = (3, 1)
    UPSTAIRS = (4, 5)
    DOWNSTAIRS = (5, 4)
    START = (100, 100)

    def __init__(self, index:int, countermove:int):
        self.index = index
        self.countermove = countermove
    
    @classmethod
    def get_move_by_number(cls, number:int):
        for move in cls:
            if move.index == number:
                return move
        return None
