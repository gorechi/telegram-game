from random import randint

class Dice():
    """
    Класс кубиков.    
    """
    
    def __init__(self, dice:list[int], modifier:int=0, dice_type:str=''):
        self.dice:list[int] = dice
        self.modifier = modifier
        self.monster_class_modifiers = {}
        self.dice_type = dice_type
        self.temporary = []
        self.initial_dice = self.dice.copy()
        self.initial_modifier = self.modifier

    def __str__(self):
        """
        Метод возвращает строковое представление кубиков.
        """
        return self.text()
    
    
    def base_die(self) -> int:
        """Функция возвращает базовый кубик"""
        if not self.dice:
            return 0
        return self.dice[0]


    def _comparison_value(self) -> int:
        """Возвращает значение кубика, по которому происходит сравнение: сумма базового кубика и модификатора."""
        return self.base_die() + self.modifier


    def _check_comparable(self, other) -> None:
        """Проверяет, что другой объект является кубиком Dice. Иначе выбрасывает TypeError."""
        if not isinstance(other, Dice):
            raise TypeError(f"Кубик можно сравнивать только с кубиком, а передан {type(other)} {other}.")


    def __eq__(self, other) -> bool:
        """Сравнение на равенство.

        Кубики считаются равными, если равны суммы их базового кубика и модификатора.
        Сравнивать можно только с другим кубиком Dice, иначе выбрасывается TypeError.
        """
        self._check_comparable(other)
        return self._comparison_value() == other._comparison_value()


    def __ne__(self, other) -> bool:
        """Сравнение на неравенство.

        Кубики считаются не равными, если различаются суммы их базового кубика и модификатора.
        Сравнивать можно только с другим кубиком Dice, иначе выбрасывается TypeError.
        """
        self._check_comparable(other)
        return self._comparison_value() != other._comparison_value()


    def __lt__(self, other) -> bool:
        """Сравнение "меньше".

        Кубик меньше другого, если сумма его базового кубика и модификатора
        меньше суммы базового кубика и модификатора другого кубика.
        Сравнивать можно только с другим кубиком Dice, иначе выбрасывается TypeError.
        """
        self._check_comparable(other)
        return self._comparison_value() < other._comparison_value()


    def __gt__(self, other) -> bool:
        """Сравнение "больше".

        Кубик больше другого, если сумма его базового кубика и модификатора
        больше суммы базового кубика и модификатора другого кубика.
        Сравнивать можно только с другим кубиком Dice, иначе выбрасывается TypeError.
        """
        self._check_comparable(other)
        return self._comparison_value() > other._comparison_value()
    
    
    def add_temporary(self, die:int):
        """Добавляет кубик к временным кубикам"""
        if not isinstance(die, int) or not die > 0:
            raise ValueError(f"Кубик должен быть целым числом больше нуля, а передан {type(die)} {die}.")
        self.temporary.append(die)
    
    
    def reset_temporary(self):
        """Очищает список временных кубиков"""
        self.temporary = []
    
    
    def roll(self, add:list[int]=None, subtract:list[int]=None, multiplier:int=1, monster=None) -> int:
        """Функция имитирует бросок кубиков"""
        
        self_result = self.roll_set(self.dice * multiplier + self.temporary)
        if (add and not isinstance(add, list)) or (subtract and not isinstance(subtract, list)):
            raise ValueError("В качестве аргумента 'add' или 'subtract' должен быть передан список целых чисел")
        if add and isinstance(add, list):
            add_result = self.roll_set(add)
        else:
            add_result = 0
        if subtract and isinstance(subtract, list):
            subtract_result = self.roll_set(subtract)
        else:
            subtract_result = 0
        if monster:
            monster_modifier = self.get_monster_modifier(monster)
        else:
            monster_modifier = 0
        result = self_result + add_result - subtract_result + self.modifier + monster_modifier
        return max(0, result)
    
    
    def get_monster_modifier(self, monster) -> int:
        """
        Функция возвращает модификатор в зависимости от класса монстра.
        """
        monster_class = type(monster).__name__
        modifier = self.monster_class_modifiers.get(monster_class, 0)
        return modifier
    
    
    def roll_set(self, dice_set:list[int]) -> int:
        """Функция имитирует бросок нескольких кубиков сразу"""
        result = 0
        for die in dice_set:
            if not isinstance(die, int) or die < 0:
                raise ValueError("Все значения кубиков должны быть целыми числами больше нуля, а передано {die} как часть {dice_set}")
            if die > 0:
                result += randint(1, die)
        return max(0, result)
    
    
    def add_die(self, die:int):
        """Добавляет кубик к кубикам"""
        if not isinstance(die, int) or not die > 0:
            raise ValueError(f"Кубик должен быть целым числом больше нуля, а передан {type(die)} {die}.")
        self.dice.append(die)
        
    
    def remove_die(self, die:int):
        """Удаляет кубик из кубиков"""
        if not isinstance(die, int):
            raise ValueError(f"Кубик должен быть целым числом, а передан {type(die)} {die}.")
        if die in self.dice:
            self.dice.remove(die)
        else:
            raise KeyError(f"Кубик {die} не найден в кубиках.")
    
    
    def text(self):
        """Возвращает текстовое представление кубиков"""
        if not self.dice:
            return "Нет кубиков"
        text =  " + ".join(f"d{die}" for die in (self.dice + self.temporary))
        if self.modifier > 0:
            text += f' + {self.modifier}'
        if self.modifier < 0:
            text += f' - {-1 * self.modifier}'
        return text
    
    
    def increase_modifier(self, value:int) -> int:
        """Увеличивает значение модификатора"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        self.modifier += value
        return self.modifier
    
        
    def decrease_modifier(self, value:int) -> int:
        """Уменьшает значение модификатора"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        self.modifier -= value
        if self.modifier < 0:
            self.modifier = 0
        return self.modifier
    
    
    def set_dice(self, dice:list[int]):
        """
        Устанавливает новый набор кубиков.
        """
        self.dice = dice
        
    
    def set_modifier(self, modifier:int):
        """
        Устанавливает новый модификатор.
        """
        self.modifier = modifier
    
    
    def copy(self):
        """Возвращает копию кубика"""
        return Dice(self.dice.copy(), self.modifier, self.dice_type)
    
    
    def reset(self):
        """
        Сбрасывает кубики и модификатор к изначальным значениям.
        """
        self.dice = self.initial_dice.copy()
        self.modifier = self.initial_modifier
        
    
    def increase_base_die(self, value:int=1) -> int:
        """Увеличивает базовый кубик на значение"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        if value < 0:
            raise ValueError(f"Значение должно быть больше или равно 0, а передано {value}.")
        self.dice[0] += value
        return self.dice[0]