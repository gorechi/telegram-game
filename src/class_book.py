from src.functions.functions import randomitem, tprint, roll

class Book:
        
    def __init__(self, game):
        self.game = game
        self.empty = False


    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def __str__(self):
        return self.name
    
    
    def on_create(self):
        return True
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['книга', 'книгу', 'книжка', 'книжку']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list

            
    def place(self, floor, room=None):
        if not room:
            room = floor.get_random_room_with_furniture()
        furniture = randomitem(room.furniture)
        furniture.put(self)
        return True
    
    
    def show(self):
        return self.lexemes['nom']
    
    
    def use(self, who, in_action:bool=False) -> list[str]:
        message = [self.text]
        message.append(self.increase_mastery(who))
        message.append(f'{who.g("Он", "Она")} решает больше не носить книгу с собой и оставляет ее в незаметном месте.')
        self.increase_mastery(who)
        return message

    
    def take(self, who):
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')
            return True
        return False
    

class ThrustingWeaponBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.weapon_mastery['колющее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать колющее оружие.'


class CuttingWeaponBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.weapon_mastery['рубящее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать рубящее оружие.'
    
    
class BluntgWeaponBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.weapon_mastery['ударное']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать ударное оружие.'


class TrapsBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.trap_mastery += 1
        return f'{who.name} теперь немного лучше разбирается в том, как обезвреживать ловушки.'
    
    
class WisdomBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.intel.increase_modoficator(1)
        who.base_intel.increase_modoficator(1)
        return f'{who.name} чувствует, что {who.g("стал", "стала")} немного умнее'