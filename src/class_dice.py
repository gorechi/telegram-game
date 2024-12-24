from random import randint, sample

class Dice():
    
    def __init__(self, dice:list[int], modificator:int=0, dice_type:str=''):
        self.dice = dice
        self.modificator = modificator
        self.dice_type = dice_type
        self.temporary = []

    def __str__(self):
        return self.get_text()
    
    
    def add_temporary(self, die:int):
        """Добавляет кубик к временным кубикам"""
        if not isinstance(die, int) or not die > 0:
            raise ValueError(f"Кубик должен быть целым числом больше нуля, а передан {type(die)} {die}.")
        self.temporary.append(die)
    
    
    def reset_temporary(self):
        """Очищает список временных кубиков"""
        self.temporary = []
    
    
    def roll(self, add:list[int]=[], subtract:list[int]=[]) -> int:
        """Функция имитирует бросок нескольких кубиков сразу

        """
        self_result = self.roll_set(self.dice + self.temporary)
        if not isinstance(add, list) or not isinstance(subtract, list):
            raise ValueError("В качестве аргумента 'add' или 'subtract' должен быть передан список целых чисел")
        add_result = self.roll_set(add)
        subtract_result = self.roll_set(subtract)
        result = self_result + add_result - subtract_result + self.modificator
        return max(0, result)
    
    
    def roll_set(self, set:list[int]) -> int:
        """Функция имитирует бросок нескольких кубиков сразу"""
        result = 0
        for die in set:
            if not isinstance(die, int):
                raise ValueError("Все значения кубиков должны быть целыми числами")
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
    
    
    def get_text(self):
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
        if value < 0:
            raise ValueError("Значение должно быть больше или равно нулю.")
        self.modificator += value
        return self.modificator
    
        
    def decrease_modificator(self, value:int) -> int:
        """Уменьшает значение модификатора"""
        if not isinstance(value, int):
            raise ValueError(f"Значение должно быть целым числом, а передан {type(value)} {value}.")
        if value < 0:
            raise ValueError("Значение должно быть больше или равно нулю.")
        self.modificator -= value
        return self.modificator