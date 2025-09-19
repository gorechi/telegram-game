from src.functions.functions import randomitem

class Book:
    """
    Класс книги.    
    """    
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
        """
        Метод форматирования имени книги в различных падежах.
        """
        return self.lexemes.get(format, '')

    
    def __str__(self):
        """
        Метод возвращает представление книги в виде строки.
        """
        return self.name
    
    
    def on_create(self):
        """
        Метод выполняет дополнительные действия при создании книги.
        """
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
        """
        Метод проверяет, соответствует ли полученная строка имени книги.
        """
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """
        Метод возвращает список имен книги в различных падежах.
        """
        names_list = ['книга', 'книгу', 'книжка', 'книжку']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list

            
    def place(self, floor, room=None):
        """
        Метод помещает книгу в комнату определенного этажа.
        """
        if not room:
            room = floor.get_random_room_with_furniture()
        furniture = randomitem(room.furniture)
        furniture.put(self)
        return True
    
    
    def examine(self, who) -> list[str]:
        """
        Метод осмотра книги.
        """
        can_examine, message = who.check_if_can_examine()
        if can_examine:
            message = [f'{who.name} держит в руках {self:accus}. {self.examine_text}']
        return message

    
    def show(self):
        """
        Метод возвращает имя книги для отображения в инвентаре.
        """
        return self.lexemes['nom']
    
    
    def use(self, who, in_action:bool=False) -> list[str]:
        """
        Метод использования книги.
        """
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
        """
        Метод позволяет герою или монстру взять книгу из комнаты.
        """
        if who.backpack.no_backpack:
            return f'{who.name} не может взять книгу потому что {who.g('ему', 'ей')} некуда ее положить.'
        who.put_in_backpack(self)
        return f'{who.name} забирает {self:accus} себе.'
    

class ThrustingWeaponBook(Book):
    """
    Класс книги по колющему оружию.    
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает навык героя по колющему оружию.
        """
        who.mastery['колющее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать колющее оружие.'


class CuttingWeaponBook(Book):
    """
    Класс книги по рубящему оружию.    
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает навык героя по рубящему оружию.
        """
        who.mastery['рубящее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать рубящее оружие.'
    
    
class BluntgWeaponBook(Book):
    """
    Класс книги по ударному оружию.    
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает навык героя по ударному оружию.
        """
        who.mastery['ударное']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать ударное оружие.'


class TrapsBook(Book):
    """
    Класс книги по ловушкам.    
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает знания героя о ловушках.
        """
        who.trap_mastery += 1
        return f'{who.name} теперь немного лучше разбирается в том, как обезвреживать ловушки.'
    
    
class WisdomBook(Book):
    """
    Класс книги по развитию интеллекта.    
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает интеллект героя.
        """
        who.intel.increase_modifier(1)
        who.start_intel.increase_modifier(1)
        return f'{who.name} чувствует, что {who.g("стал", "стала")} немного умнее'
    

class ShieldsBook(Book):
    """
    Класс книги по щитам.    
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает знания героя о щитах.
        """
        who.mastery['щит']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать щиты.'
    

class ArmorBook(Book):
    """
    Класс книги по доспехам.        
    """
    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        """
        Метод увеличивает знания героя о доспехах.
        """
        who.mastery['доспехи']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как пользоваться доспехами.'

