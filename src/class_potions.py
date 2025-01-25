from src.functions.functions import howmany, randomitem, tprint
from random import randint as dice


class Potion:
    
    def __init__(self, game):
        self.game = game
        self.empty = False
        self.owner = None
        self.room_actions = {
            "взять": {
                "method": "take",
                "batch": True,
                "in_combat": False,
                "in_darkness": False
                },
            "брать": {
                "method": "take",
                "batch": True,
                "in_combat": False,
                "in_darkness": False
                },
            "собрать": {
                "method": "take",
                "batch": True,
                "in_combat": False,
                "in_darkness": False
                }
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
        room.action_controller.add_actions(self)
        return True

       
    def take(self, who, in_action:bool=False):
        if who.backpack.no_backpack:
            return f'{who.name} не может взять зелье потому что {who.g('ему', 'ей')} некуда его положить.'
        who.put_in_backpack(self)
        return f'{who.name} забирает {self:accus} себе.'
    
    
    def check_if_can_be_used(self, in_action: bool) -> bool:
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
    
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
        
    
    def use(self, who, in_action:bool=False) -> str:
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

    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
    
    
    def use(self, who, in_action:bool=False) -> str:
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.start_health += self.effect
        who.health += self.effect
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свое максимальное здоровье на {str(self.effect)} до {str(who.health)}.'
    

class StrengthPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
       
    
    def use(self, who, in_action:bool=False) -> str:
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.stren.increase_base_die(self.effect)
        who.start_stren.increase_base_die(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свою силу на {self.effect} до {who.stren.text()}.'
    

class StrengtheningPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
    
        
    def use(self, who, in_action:bool=False) -> str:
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        who.stren.add_temporary(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'На время боя {who.name} увеличивает свою силу на {self.effect} до {who.stren.text()}.'


class DexterityPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }

    
    def use(self, who, in_action:bool=False) -> str:
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.dext.increase_base_die(self.effect)
        who.start_dext.increase_base_die(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свою ловкость на {self.effect} до {who.dext.text()}.'


class EvasionPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
        
     
    def use(self, who, in_action:bool=False) -> str:
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        who.dext.add_temporary(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'На время боя {who.name} увеличивает свою ловкость на {self.effect} до {who.dext.text()}.'
    
    
class IntelligencePotion(Potion):
    
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
        
    
    def use(self, who, in_action:bool=False) -> str:
        if in_action:
            return 'Это зелье нельзя использовать в бою!'
        who.intel.increase_base_die(self.effect)
        who.start_intel.increase_base_die(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} увеличивает свой интеллект на {self.effect} до {who.intel.text()}.'
    

class EnlightmentPotion(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": True,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }
        
    
    def use(self, who, in_action:bool=False) -> str:
        if not in_action:
            return 'Это зелье можно использовать только в бою!'
        who.intel.add_temporary(self.effect)
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'На время боя {who.name} увеличивает свой интеллект на {self.effect} до {who.intel.text()}.'


class Antidote(Potion):
            
    def __init__(self, game):
        super().__init__(game)
        self.hero_actions = {
            "пить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выпить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "попить": {
                "method": "use",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "бросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "выбросить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            "оставить": {
                "method": "drop",
                "batch": False,
                "in_combat": False,
                "in_darkness": True
                },
            }


    def use(self, who, in_action:bool=False) -> str:
        if not who.poisoned and who.fear == 0:
            return f'{who.name} не чувствует никакого недомогания и решает приберечь зелье на попозже.'
        who.poisoned = False
        who.fear = 0
        who.backpack.remove(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} излечивается от отравления, избавляется от всех страхов и теперь прекрасно себя чувствует.'
