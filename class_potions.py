from functions import howmany, randomitem, tprint, roll
from random import randint as dice


class Potion:
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        self.game = game
        self.name = name
        self.effect = effect
        self.type = potion_type
        self.can_use_in_fight = can_use_in_fight
        self.empty = False
        self.owner = None

    
    def __str__(self):
        return self.description

    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', 'accus'])
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
            room = randomitem(rooms, False)
        if room.furniture:
            furniture = randomitem(room.furniture, False)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    
    def check_if_can_be_used(self, in_action: bool) -> bool:
        game = self.game
        owner = self.owner
        if self.type == 8 and not owner.poisoned and owner.fear == 0:
            tprint(
                game, f'{owner.name} не чувствует никакого недомогания и решает приберечь зелье на попозже.')
            return False
        if not in_action and self.type in [0, 3, 5, 7]:
            tprint(game, 'Это зелье можно использовать только в бою!')
            return False
        if in_action and self.type in [1, 2, 4, 6]:
            tprint(game, 'Это зелье нельзя использовать в бою!')
            return False
        return True
    
    def use_type_6(self, who_using) -> bool:
        who_using.intel += self.effect
        who_using.start_intel += self.effect
        tprint(self.game, f'{who_using.name} увеличивает свой \
            интеллект на {str(self.effect)} до {str(who_using.intel)}.')
        return True

    
    def use_type_7(self, who_using) -> bool:
        who_using.intel += self.effect
        tprint(
            self.game, f'На время боя {who_using.name} увеличивает свой интеллект на {str(self.effect)} до {str(who_using.intel)}.')
        return True

    
    def use_type_8(self, who_using) -> bool:
        who_using.poisoned = False
        who_using.fear = 0
        tprint(
            self.game, f'{who_using.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.')
        return True

       
    def take(self, who):
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            self.owner = who
            tprint(self.game, f'{who.name} забирает {self.lexemes['accus']} себе.')
            return True
        return False


class HealPotion(Potion):
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False
        
    
    def use(self, who_using, in_action:bool) -> bool:
        owner = self.owner
        if not owner or not self.check_if_can_be_used(in_action):
            return False
        if (owner.start_health - owner.health) < self.effect:
            heal = dice(1, (owner.start_health - owner.health))
        else:
            heal = dice(1, self.effect)
        owner.health += heal
        text = f'{owner.lexemes['nom']} восполняет {howmany(heal, "единицу жизни,единицы жизни,единиц жизни")}'
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
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False

    
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
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False
        
    
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
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False
    
    
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
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False
        
    
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
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False
    
    
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
    
    def __init__(self, game, name='Зелье', effect=0, potion_type=0, can_use_in_fight=True):
        super().__init__(game, name, effect, potion_type, can_use_in_fight)
        self.empty = False
        
    
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