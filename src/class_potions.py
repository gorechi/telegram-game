from src.functions.functions import howmany, randomitem, tprint
from random import randint as dice


class Potion:
    """ 
    Родительский класс для всех зелий.     
    """
    def __init__(self, game):
        self.game = game
        self.empty = False
        self.owner = None
        self.hero_actions = {
            "бросить": {
                "method": "drop",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 0
                },
            "выбросить": {
                "method": "drop",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 0
                },
            "оставить": {
                "method": "drop",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 0
                },
            }
        self.room_actions = {
            "взять": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "брать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                },
            "собрать": {
                "method": "take",
                "bulk": True,
                "in_combat": False,
                "in_darkness": False,
                "duration": 0
                }
            }


    
    def __format__(self, format:str) -> str:
        """ 
        Метод форматирования зелья в различных падежах.
        """
        return self.lexemes.get(format, '')
    
    
    def __str__(self):
        """ 
        Метод строкового представления зелья.
        """
        return self.description
    
    
    def check_name(self, message:str) -> bool:
        """ 
        Проверяет, соответствует ли введенное имя имени зелья.
        """
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """ 
        Метод возвращает список имен зелья в различных падежах.
        """
        names_list = ['зелье', 'напиток']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def on_create(self):
        """ 
        Метод вызывается при создании зелья.
        """
        return True

    
    def show(self):
        """ 
        Метод возвращает описание зелья.
        """
        return self.description

    
    def place(self, castle, room=None):
        """ 
        Метод размещения зелья в комнате замка.
        """
        if not room:
            rooms = castle.plan
            room = randomitem(rooms)
        if room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
            room.action_controller.add_actions(self)
        return True

       
    def take(self, who, in_action:bool=False):
        """ 
        Метод взятия зелья.
        """
        if who.backpack.no_backpack:
            return f'{who.name} не может взять зелье потому что {who.g('ему', 'ей')} некуда его положить.'
        who.put_in_backpack(self)
        return f'{who.name} забирает {self:accus} себе.'
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        """ 
        Метод проверки возможности использования зелья в текущем контексте (в бою или вне его).
        """
        game = self.game
        if not in_action and self.can_use_in_fight:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        if in_action and not self.can_use_in_fight:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True
    
    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания зелья.
        """
        room = who.current_position
        room.loot.add(self)
        who.backpack.remove(item=self, place=room)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} аккуратно ставит пузырек с зельем подальше от посторонних глаз.'


class HealPotion(Potion):
    """ 
    Зелье лечения.     
    """
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            }
        
    
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья лечения.
        """
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        if (who.start_health - who.health) < self.effect:
            heal = dice(1, (who.start_health - who.health))
        else:
            heal = dice(1, self.effect)
        who.health += heal
        message = f'{who:nom} восполняет {howmany(heal, ["единицу жизни", "единицы жизни", "диниц жизни"])}'
        if who.poisoned:
            who.poisoned = False
            message += ' и излечивается от отравления'
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return message
    

class HealthPotion(Potion):
    """ 
    Зелье увеличения максимального здоровья.     
    """
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            }
    
    
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья увеличения максимального здоровья.
        """
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.start_health += self.effect
        who.health += self.effect
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свое максимальное здоровье на {str(self.effect)} до {str(who.health)}.'
    

class StrengthPotion(Potion):
    """ 
    Зелье увеличения максимальной силы.     
    """        
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
       
    
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья увеличения максимальной силы.
        """
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.stren.increase_base_die(self.effect)
        who.start_stren.increase_base_die(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свою силу на {self.effect} до {who.stren.text()}.'
    

class StrengtheningPotion(Potion):
    """ 
    Зелье временного увеличения силы.     
    """        
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            }
    
        
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья временного увеличения силы.
        """
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        who.stren.add_temporary(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'На время боя {who.name} увеличивает свою силу на {self.effect} до {who.stren.text()}.'


class DexterityPotion(Potion):
    """ 
    Зелье увеличения максимальной ловкости.     
    """        
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            }

    
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья увеличения максимальной ловкости.
        """
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.dext.increase_base_die(self.effect)
        who.start_dext.increase_base_die(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свою ловкость на {self.effect} до {who.dext.text()}.'


class EvasionPotion(Potion):
    """ 
    Зелье временного увеличения ловкости.     
    """        
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            }
        
     
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья временного увеличения ловкости.
        """
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        who.dext.add_temporary(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'На время боя {who.name} увеличивает свою ловкость на {self.effect} до {who.dext.text()}.'
    
    
class IntelligencePotion(Potion):
    """ 
    Зелье увеличения максимального интеллекта.     
    """
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            }
        
    
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья увеличения максимального интеллекта.
        """
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.intel.increase_base_die(self.effect)
        who.start_intel.increase_base_die(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свой интеллект на {self.effect} до {who.intel.text()}.'
    

class EnlightmentPotion(Potion):
    """ 
    Зелье временного увеличения интеллекта.     
    """        
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": True,
                "in_darkness": True,
                "duration": 1
                },
            }
        
    
    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования зелья временного увеличения интеллекта.
        """
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        who.intel.add_temporary(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'На время боя {who.name} увеличивает свой интеллект на {self.effect} до {who.intel.text()}.'


class Antidote(Potion):
    """ 
    Противоядие.     
    """        
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions |= {
            "пить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "выпить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            "попить": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 1
                },
            }


    def use(self, who, in_action:bool=False) -> str:
        """ 
        Метод использования противоядия.
        """
        if not who.poisoned and who.fear == 0:
            return f'{who.name} не чувствует никакого недомогания и решает приберечь зелье на попозже.'
        who.poisoned = False
        who.fear = 0
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.'
