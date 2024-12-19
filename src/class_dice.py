from random import randint, sample

class Dice():
    
    def __init__(self, dice:list[int], modificator:int=0, dice_type:str=''):
        self.dice = dice
        self.modificator = modificator
        self.dice_type = dice_type

    
    def roll(self) -> int:
        """Функция имитирует бросок нескольких кубиков сразу

        """
        result = 0 
        for die in self.dice:
            if not isinstance(die, int):
                raise ValueError("Все значения кубиков должны быть целыми числами")
            result += randint(1, die)
        return result + self.modificator
    
    
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
        text =  " + ".join(f"d{die}" for die in self.dice)
        if self.modificator > 0:
            text += f' + {self.modificator}'
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
        self.modificator = max(0, self.modificator - value)
        return self.modificator