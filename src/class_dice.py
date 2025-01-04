from random import randint, sample

class Dice():
    
    def __init__(self, dice:list[int], modificator:int=0, dice_type:str=''):
        self.dice:list[int] = dice
        self.modificator = modificator
        self.dice_type = dice_type
        self.temporary = []
        self.initial_dice = self.dice.copy()
        self.initial_modificator = self.modificator

    def __str__(self):
        return self.text()
    
    
    def base_die(self) -> int:
        """Функция возвращает базовый кубик"""
        if not self.dice:
            return 0
        return self.dice[0]
    
    
    def add_temporary(self, die:int):
        """Добавляет кубик к временным кубикам"""
        if not isinstance(die, int) or not die > 0:
            raise ValueError(f"Кубик должен быть целым числом больше нуля, а передан {type(die)} {die}.")
        self.temporary.append(die)
    
    
    def reset_temporary(self):
        """Очищает список временных кубиков"""
        self.temporary = []
    
    
    def roll(self, add:list[int]=[], subtract:list[int]=[], multiplier:int=1) -> int:
        """Функция имитирует бросок кубиков"""
        
        self_result = self.roll_set(self.dice * multiplier + self.temporary)
        if not isinstance(add, list) or not isinstance(subtract, list):
            raise ValueError("В качестве аргумента 'add' или 'subtract' должен быть передан список целых чисел")
        if add:
            add_result = self.roll_set(add)
        else:
            add_result = 0
        if subtract:
            subtract_result = self.roll_set(subtract)
        else:
            subtract_result = 0
        result = self_result + add_result - subtract_result + self.modificator
        return max(0, result)
    
    
    def roll_set(self, dice_set:list[int]) -> int:
        """Функция имитирует бросок нескольких кубиков сразу"""
        result = 0
        for die in dice_set:
            if not isinstance(die, int):
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
            raise ValueError(f"Кубик {die} не найден в кубиках.")
    
    
    def text(self):
        """Возвращает текстовое представление кубиков"""
        if not self.dice:
            return "Нет кубиков"
        text =  " + ".join(f"d{die}" for die in (self.dice + self.temporary))
        if self.modificator > 0:
            text += f' + {self.modificator}'
        if self.modificator < 0:
            text += f' - {-1 * self.modificator}'
        return text
    
    
    def increase_modificator(self, value:int) -> int:
        """Увеличивает значение модификатора"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        self.modificator += value
        return self.modificator
    
        
    def decrease_modificator(self, value:int) -> int:
        """Уменьшает значение модификатора"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        self.modificator -= value
        return self.modificator
    
    
    def set_dice(self, dice:list[int]):
        self.dice = dice
        
    
    def set_modificator(self, modificator:int):
        self.modificator = modificator
    
    
    def copy(self):
        """Возвращает копию кубика"""
        return Dice(self.dice.copy(), self.modificator, self.dice_type)
    
    
    def reset(self):
        self.dice = self.initial_dice.copy()
        self.modificator = self.initial_modificator
        
    
    def increase_base_die(self, value:int=1) -> int:
        """Увеличивает базовый кубик на значение"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        self.dice[0] += value
        return self.dice[0]