from src.functions.functions import randomitem

class Rune:
    
    """ Класс Руна. """
    
    _glowing_elements = (1, 2, 4)
    """Массив стихий, которые заставляют оружие светиться в темноте"""
    
    _elements_dictionary = {1: 'огня',
                        2: 'пламени',
                        3: 'воздуха',
                        4: 'света',
                        6: 'ветра',
                        7: 'земли',
                        8: 'лавы',
                        10: 'пыли',
                        12: 'воды',
                        13: 'пара',
                        14: 'камня',
                        15: 'дождя',
                        19: 'грязи',
                        24: 'потопа'}
    """Словарь стихий."""
      
    def __init__(self, game):
        self.game = game
        self.empty = False
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
         
    
    def __str__(self) -> str:
        """ 
        Метод строкового представления руны.
        """
        return f'{self.name} {Rune._elements_dictionary[self.element]} - ' \
            f'урон + {str(self.damage)} или защита + {str(self.defence)}'
    
    
    def __format__(self, format:str) -> str:
        """ 
        Метод форматирования руны.
        """
        return self.lexemes.get(format, '')

      
    def check_name(self, message:str) -> bool:
        """ 
        Метод проверки, относится ли сообщение к руне.
        """
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None, room=None) -> list:
        """ 
        Метод получения списка имен руны для распознавания команд.
        """
        names_list = ['руна', 'руну']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def on_create(self):
        """ 
        Метод вызывается после создания экземпляра класса. Ничего не делает. 
        """
        return True

    
    def place(self, floor, room=None) -> bool:
        """ 
        Метод раскидывания рун по этажу замка. 
        """
        if not room:
            secret = self.game.secret_places_controller.get_random_secret_by_floor(floor)
            if secret:
                secret.loot.add(self)
                return True
            else:
                room = randomitem(floor.plan)
        return self.place_in_room(room)
          
        
    def place_in_room(self, room) -> bool:
        """ 
        Метод раскидывания руны по комнате замка. 
        1. Если в комнате есть секретное место, руна помещается туда. 
        """    
        secret = self.game.secret_places_controller.get_random_secret_by_room(room)
        if secret:
            secret.loot.add(self)
            return True
        if room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
            return True
        room.loot.add(self)
        room.action_controller.add_actions(self)
        return True

    
    def element(self) -> int:
        """ 
        Метод возвращает элемент руны в виде целого числа. 
        """
        return int(self.element)

    
    def take(self, who, in_action:bool=False) -> str:
        """ 
        Метод вызывается когда кто-то забирает руну себе. 
        """
        if who.backpack.no_backpack:
            return f'{who.name} не может взять рунУ потому что {who.g('ему', 'ей')} некуда ее положить.'
        who.put_in_backpack(self)
        return f'{who.name} забирает {self:accus} себе.'

    
    def show(self) -> str:
        """ 
        Метод возвращает описание руны в виде строки. 
        """
        return f'{self.description} - урон + {str(self.damage)} или защита + {str(self.defence)}'.capitalize()

    
    def drop(self, who, in_action:bool=False) -> str:
        """
        Метод выбрасывания руны.
        """
        room = who.current_position
        room.loot.add(self)
        who.backpack.remove(item=self, place=room)
        room.action_controller.add_actions(self)
        who.action_controller.delete_actions_by_item(self)
        return f'{who.name} бросает {self:accus} на пол.'
