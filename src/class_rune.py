from src.functions.functions import randomitem, tprint

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
        
         
    
    def __str__(self) -> str:
        return f'{self.name} {Rune._elements_dictionary[self.element]} - ' \
            f'урон + {str(self.damage)} или защита + {str(self.defence)}'
    
    
    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

      
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['руна', 'руну']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    
    
    def on_create(self):
        
        """ Метод вызывается после создания экземпляра класса. Ничего не делает. """
        
        return True

    
    def place(self, castle, room=None) -> bool:
        
        """ Метод раскидывания рун по замку. """
        
        rooms_with_secrets = castle.secret_rooms()
        if not room:
            rooms = castle.plan
            room = randomitem(rooms)
        if room in rooms_with_secrets:
            room.secret_loot.add(self)
        elif room.furniture:
            furniture = randomitem(room.furniture)
            furniture.put(self)
        else:
            room.loot.add(self)
        return True

    
    def element(self) -> int:
        
        """ Метод возвращает элемент руны в виде целого числа. """
        
        return int(self.element)

    
    def take(self, who):
        
        """ Метод вызывается когда кто-то забирает руну себе. """
        
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')

    
    def show(self) -> str:
        
        """ Метод возвращает описание руны в виде строки. """
        
        return f'{self.description} - урон + {str(self.damage)} или защита + {str(self.defence)}'.capitalize()

    
    def use(self, who_is_using, in_action:bool=False) -> str:
        
        """ 
        Метод использования руны. Возвращает строку ответа и ничего не делает 
        так как руну использовать нельзя.
        
        """
        
        tprint(self.game, f'{who_is_using.name} не знает, как использовать такие штуки.')