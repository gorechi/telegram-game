from functions import howmany, randomitem, tprint, roll
from random import randint as dice


class Potion:
     
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        self.game = game
        self.name = name
        self.effect = effect
        self.can_use_in_fight = can_use_in_fight
        self.empty = False
        self.owner = None

    
    def __str__(self):
        return self.description

    
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
            tprint(self.game, f'{who.name} забирает {self.lexemes["accus"]} себе.')
            return True
        return False


class HealPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
        
    
    def on_create(self):
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        owner = self.owner
        if not owner or not self.check_if_can_be_used(in_action):
            return False
        if (owner.start_health - owner.health) < self.effect:
            heal = dice(1, (owner.start_health - owner.health))
        else:
            heal = dice(1, self.effect)
        owner.health += heal
        text = f'{owner.lexemes["nom"]} восполняет {howmany(heal, "единицу жизни,единицы жизни,единиц жизни")}'
        if owner.poisoned:
            owner.poisoned = False
            text += ' и излечивается от отравления'
        tprint(self.game, text)
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if not in_action:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        return True
    

class HealthPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None

        
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if in_action:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.start_health += self.effect
        self.owner.health += self.effect
        tprint(
            self.game, f'{self.owner.name} увеличивает свое максимальное здоровье на {str(self.effect)} до {str(self.owner.health)}.')
        return True
    

class StrengthPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
        
    
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if in_action:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.stren += self.effect
        self.owner.start_stren += self.effect
        tprint(
            self.game, f'{self.owner.name} увеличивает свою силу на {str(self.effect)} до {str(self.owner.stren)}.')
        return True
    

class StrengtheningPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
    
    
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if not in_action:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.stren += self.effect
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свою силу на {str(self.effect)} до {str(self.owner.stren)}.')
        return True


class DexterityPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
        
    
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if in_action:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.dext += self.effect
        self.owner.start_dext += self.effect
        tprint(
            self.game, f'{self.owner.name} увеличивает свою ловкость на {str(self.effect)} до {str(self.owner.dext)}.')
        return True


class EvasionPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
    
    
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if not in_action:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.dext += self.effect
        tprint(
            self.game, f'На время боя {self.owner.name} увеличивает свою ловкость на {str(self.effect)} до {str(self.owner.dext)}.')
        return True
    
    
class IntelligencePotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
        
    
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if in_action:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.intel += self.effect
        self.owner.start_intel += self.effect
        tprint(self.game, f'{self.owner.name} увеличивает свой интеллект на {str(self.effect)} до {str(self.owner.intel)}.')
        return True
    

class EnlightmentPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
    
    
    def on_create(self):
        return True
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        if not in_action:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        return True
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.intel += self.effect
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свой интеллект на {str(self.effect)} до {str(self.owner.intel)}.')
        return True


class Antidote(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, can_use_in_fight=True):
        super().__init__(game, name, effect, can_use_in_fight)
        self.empty = False
        self.owner = None
    
    
    def on_create(self):
        return True
    
    
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
