from functions import howmany, randomitem, tprint
from random import randint as dice


class Potion:
    
    
    @classmethod
    def random_potion(cls, game) -> 'Potion':
        potion_class = randomitem(cls.__subclasses__())
        new_potion = potion_class(game)
        return new_potion
    
     
    def __init__(self, game):
        self.game = game
        self.name = self.get_name()
        self.effect = self.get_effect()
        self.can_use_in_fight = self.get_in_fight_permition()
        self.empty = False
        self.owner = None

    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
    def __str__(self):
        return self.description

    
    def get_name(self):
        return self.__class__._name
    
    
    def get_effect(self):
        return self.__class__._effect
    
    
    def get_in_fight_permition(self):
        return self.__class__._can_use_in_fight
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['зелье', 'напиток']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def on_create(self):
        return True

    
    def show(self):
        return self.description

    
    def place(self, castle, room=None):
        if not room:
            rooms = castle.plan
            room = randomitem(rooms)
        if room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

       
    def take(self, who):
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            self.owner = who
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')
            return True
        return False
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if not in_action and self.can_use_in_fight:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        if in_action and not self.can_use_in_fight:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True



class HealPotion(Potion):
    
    _name:str = "Зелье исцеления"
    
    _effect:int = 10
    
    _can_use_in_fight:bool = True

            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Лечебное зелье, лечит раны и восстанавливает некоторое количество единиц здоровья."
        self.lexemes:dict[str, str] = {
            "nom": "зелье исцеления",
            "accus": "зелье исцеления",
            "gen": "зелья исцеления",
            "dat": "зелью исцеления",
            "prep": "зелье исцеления",
            "inst": "зельем исцеления"
        }
        self.base_price = 10
        
    
    def use(self, who_using, in_action:bool) -> bool:
        owner = self.owner
        if not owner or not self.check_if_can_be_used(in_action):
            return False
        if (owner.start_health - owner.health) < self.effect:
            heal = dice(1, (owner.start_health - owner.health))
        else:
            heal = dice(1, self.effect)
        owner.health += heal
        text = f'{owner:nom} восполняет {howmany(heal, ["единицу жизни", "единицы жизни", "диниц жизни"])}'
        if owner.poisoned:
            owner.poisoned = False
            text += ' и излечивается от отравления'
        tprint(self.game, text)
        return True
    

class HealthPotion(Potion):
    
    _name:str = "Зелье здоровья"
    
    _effect:int = 1
    
    _can_use_in_fight:bool = False


    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье здоровья увеличивает максимальный запас здоровья персонажа."
        self.lexemes:dict[str, str] = {
            "nom": "зелье здоровья",
            "accus": "зелье здоровья",
            "gen": "зелья здоровья",
            "dat": "зелью здоровья",
            "prep": "зелье здоровья",
            "inst": "зельем здоровья"
        }
        self.base_price = 20
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.start_health += self.effect
        self.owner.health += self.effect
        tprint(
            self.game, f'{self.owner.name} увеличивает свое максимальное здоровье на {str(self.effect)} до {str(self.owner.health)}.')
        return True
    

class StrengthPotion(Potion):
    
    _name:str = "Зелье силы"
    
    _effect:int = 1
    
    _can_use_in_fight:bool = False
      
            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье силы увеличивает максимальное значение силы персонажа."
        self.lexemes:dict[str, str] = {
            "nom": "зелье силы",
            "accus": "зелье силы",
            "gen": "зелья силы",
            "dat": "зелью силы",
            "prep": "зелье силы",
            "inst": "зельем силы"
        }
        self.base_price = 30
       
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.stren += self.effect
        self.owner.start_stren += self.effect
        tprint(
            self.game, f'{self.owner.name} увеличивает свою силу на {str(self.effect)} до {str(self.owner.stren)}.')
        return True
    

class StrengtheningPotion(Potion):
    
    _name:str = "Зелье усиления"
    
    _effect:int = 5
    
    _can_use_in_fight:bool = True
      
            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье усиления временно добавляет персонажу силы."
        self.lexemes:dict[str, str] = {
            "nom": "зелье усиления",
            "accus": "зелье усиления",
            "gen": "зелья усиления",
            "dat": "зелью усиления",
            "prep": "зелье усиления",
            "inst": "зельем усиления"
        }
        self.base_price = 15

        
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.stren += self.effect
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свою силу на {str(self.effect)} до {str(self.owner.stren)}.')
        return True


class DexterityPotion(Potion):
    
    _name:str = "Зелье ловкости"
    
    _effect:int = 1
    
    _can_use_in_fight:bool = False

            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье ловкости увеличивает максимальное значение ловкости персонажа."
        self.lexemes:dict[str, str] = {
            "nom": "зелье ловкости",
            "accus": "зелье ловкости",
            "gen": "зелья ловкости",
            "dat": "зелью ловкости",
            "prep": "зелье ловкости",
            "inst": "зельем ловкости"
        }
        self.base_price = 20

    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.dext += self.effect
        self.owner.start_dext += self.effect
        tprint(
            self.game, f'{self.owner.name} увеличивает свою ловкость на {str(self.effect)} до {str(self.owner.dext)}.')
        return True


class EvasionPotion(Potion):
    
    _name:str = "Зелье увертливости"
    
    _effect:int = 5
    
    _can_use_in_fight:bool = True
    
            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье увертливости временно добавляет персонажу ловкости."
        self.lexemes:dict[str, str] = {
            "nom": "зелье увертливости",
            "accus": "зелье увертливости",
            "gen": "зелья увертливости",
            "dat": "зелью увертливости",
            "prep": "зелье увертливости",
            "inst": "зельем увертливости"
        }
        self.base_price = 15
        
     
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.dext += self.effect
        tprint(
            self.game, f'На время боя {self.owner.name} увеличивает свою ловкость на {str(self.effect)} до {str(self.owner.dext)}.')
        return True
    
    
class IntelligencePotion(Potion):
    
    _name:str = "Зелье ума"
    
    _effect:int = 1
    
    _can_use_in_fight:bool = False
            
    
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье ума увеличивает максимальное значение силы интеллекта."
        self.lexemes:dict[str, str] = {
            "nom": "зелье ума",
            "accus": "зелье ума",
            "gen": "зелья ума",
            "dat": "зелью ума",
            "prep": "зелье ума",
            "inst": "зельем ума"
        }
        self.base_price = 25
        
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.intel += self.effect
        self.owner.start_intel += self.effect
        tprint(self.game, f'{self.owner.name} увеличивает свой интеллект на {str(self.effect)} до {str(self.owner.intel)}.')
        return True
    

class EnlightmentPotion(Potion):
    
    _name:str = "Зелье просветления"
    
    _effect:int = 5
    
    _can_use_in_fight:bool = True
    
            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Зелье просветления временно добавляет персонажу интеллекта."
        self.lexemes:dict[str, str] = {
            "nom": "зелье просветления",
            "accus": "зелье просветления",
            "gen": "зелья просветления",
            "dat": "зелью просветления",
            "prep": "зелье просветления",
            "inst": "зельем просветления"
        }
        self.base_price = 10
        
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.intel += self.effect
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свой интеллект на {str(self.effect)} до {str(self.owner.intel)}.')
        return True


class Antidote(Potion):
    
    _name:str = "Противоядие"
    
    _effect:int = 1
    
    _can_use_in_fight:bool = True

            
    def __init__(self, game):
        super().__init__(game)
        self.description:str = "Противоядие лечит отравление и прочие отрицательные эффекты. На основе алкоголя."
        self.lexemes:dict[str, str] = {
            "nom": "противоядие",
            "accus": "противоядие",
            "gen": "противоядия",
            "dat": "противоядию",
            "prep": "противоядие",
            "inst": "противоядием"
        }
        self.base_price = 5

        
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if not self.owner.poisoned and self.owner.fear == 0:
            tprint(game, f'{self.owner.name} не чувствует никакого недомогания и решает приберечь зелье на попозже.')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.poisoned = False
        self.owner.fear = 0
        tprint(
            self.game, f'{self.owner.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.')
        return True
