from src.functions.functions import howmany, randomitem, tprint
from random import randint as dice


class Potion:
    
    def __init__(self, game):
        self.game = game
        self.empty = False
        self.owner = None
        self.hero_actions = {
            "пить": "use",
            "выпить": "use",
            "попить": "use"
            }

    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')
    
    
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
    
    def __init__(self, game):
        super().__init__(game)
        
    
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
        owner.backpack.remove(self)
        return True
    

class HealthPotion(Potion):

    def __init__(self, game):
        super().__init__(game)
    
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.start_health += self.effect
        self.owner.health += self.effect
        tprint(self.game, f'{self.owner.name} увеличивает свое максимальное здоровье на {str(self.effect)} до {str(self.owner.health)}.')
        self.owner.backpack.remove(self)
        return True
    

class StrengthPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
       
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.stren.increase_base_die(self.effect)
        self.owner.start_stren.increase_base_die(self.effect)
        tprint(self.game, f'{self.owner.name} увеличивает свою силу на {self.effect} до {self.owner.stren.text()}.')
        self.owner.backpack.remove(self)
        return True
    

class StrengtheningPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
    
        
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.stren.add_temporary(self.effect)
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свою силу на {self.effect} до {self.owner.stren.text()}.')
        self.owner.backpack.remove(self)
        return True


class DexterityPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)

    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.dext.increase_base_die(self.effect)
        self.owner.start_dext.increase_base_die(self.effect)
        tprint(self.game, f'{self.owner.name} увеличивает свою ловкость на {self.effect} до {self.owner.dext.text()}.')
        self.owner.backpack.remove(self)
        return True


class EvasionPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        
     
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.dext.add_temporary(self.effect)
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свою ловкость на {self.effect} до {self.owner.dext.text()}.')
        self.owner.backpack.remove(self)
        return True
    
    
class IntelligencePotion(Potion):
    
    def __init__(self, game):
        super().__init__(game)
        
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.intel.increase_base_die(self.effect)
        self.owner.start_intel.increase_base_die(self.effect)
        tprint(self.game, f'{self.owner.name} увеличивает свой интеллект на {self.effect} до {self.owner.intel.text()}.')
        self.owner.backpack.remove(self)
        return True
    

class EnlightmentPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        
    
    def use(self, who_using, in_action:bool) -> bool:
        if not self.owner or not self.check_if_can_be_used(in_action):
            return False
        self.owner.intel.add_temporary(self.effect)
        tprint(self.game, f'На время боя {self.owner.name} увеличивает свой интеллект на {self.effect} до {self.owner.intel.text()}.')
        self.owner.backpack.remove(self)
        return True


class Antidote(Potion):
            
    def __init__(self, game):
        super().__init__(game)

        
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
        tprint(self.game, f'{self.owner.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.')
        self.owner.backpack.remove(self)
        return True
