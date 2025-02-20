from src.functions.functions import randomitem

class Book:
        
    def __init__(self, game):
        self.game = game
        self.empty = False
        self.hero_actions = {
            "читать": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 5
                },
            "прочитать": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": True,
                "duration": 5
                },
            "почитать": {
                "method": "use",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "duration": 5
                },
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
        return self.lexemes.get(format, '')

    
    def __str__(self):
        return self.name
    
    
    def on_create(self):
        return True
    
    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания книги.
        """
        room = who.current_position
        room.loot.add(self)
        who.backpack.remove(item=self, place=room)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} аккуратно кладет {self.name} в укромное местечко.'
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
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
    
    
    def examine(self, who) -> list[str]:
        can_examine, message = who.check_if_can_examine()
        if can_examine:
            message = [f'{who.name} держит в руках {self:accus}. {self.examine_text}']
        return message

    
    def show(self):
        return self.lexemes['nom']
    
    
    def use(self, who, in_action:bool=False) -> list[str]:
        can_read, message = who.check_if_can_read()
        if can_read: 
            message = [f'{who.name} читает {self:accus}.']
            message.append(self.text)
            message.append(self.increase_mastery(who))
            message.append(f'{who:pronoun} решает больше не носить книгу с собой и оставляет ее в незаметном месте.'.capitalize())
            who.backpack.remove(self)
            who.action_controller.delete_actions_by_item(self)
        return message

    
    def take(self, who):
        if who.backpack.no_backpack:
            return f'{who.name} не может взять книгу потому что {who.g('ему', 'ей')} некуда ее положить.'
        who.put_in_backpack(self)
        return f'{who.name} забирает {self:accus} себе.'
    

class ThrustingWeaponBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.mastery['колющее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать колющее оружие.'


class CuttingWeaponBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.mastery['рубящее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать рубящее оружие.'
    
    
class BluntgWeaponBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.mastery['ударное']['level'] += 1
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
        who.intel.increase_modifier(1)
        who.start_intel.increase_modifier(1)
        return f'{who.name} чувствует, что {who.g("стал", "стала")} немного умнее'
    

class ShieldsBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.mastery['щит']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать щиты.'
    

class ArmorBook(Book):
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.mastery['доспехи']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как пользоваться доспехами.'

