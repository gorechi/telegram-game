
class SecretPlace:
    """ 
    Класс серетов, которые могут быть размещены в комнате и скрыты в е описании    
    """
    def __init__(self, game):
        self.game = game
        self.name = None
        self.lexemes = None
        self.room = None
        self.floor = None
        self.loot = None
        self.trap = None
        self.revealed = False
        self.room_actions = {
            "обыскать": {
                "method": "search",
                "bulk": False,
                "in_combat": False,
                "in_darkness": False,
                "hidden": "is_not_revealed",
                "duration": 2
                },
        }

    
    def __format__(self, format:str) -> str:
        """ 
        Обрабатывает запрос на отображение экземпляра класса в виде форматированной строки 
        """
        return self.lexemes.get(format, '')

    
    def is_not_revealed(self):
        """ 
        Возвращает True если секрет еще ни разу не обыскивали
        """
        return not self.revealed

    
    def check_name(self, message:str) -> bool:
        """ 
        Отрабатывает запрос на проверку имени экземпляра класса
        """
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    

    def get_names_list(self, cases:list=None, room=None) -> list:
        """ 
        Возвращает список имен экземпляра класса
        """
        names_list = list()
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
    

    def on_create(self):
        """ 
        Метод вызывается после создания экземпляра класса. Ничего не делает. 
        """
        return True
    

    def search(self, who, in_action:bool=False) -> list[str]:
        """
        Метод обыскивания секретного места.
        """
        room = who.current_position
        if self.loot == 0:
            return self.empty_text
        message = [f'{who.name} осматривает {self:accus} и находит:']
        message += self.loot.show_sorted()
        self.loot.reveal(room)
        message.append('Все, что было спрятано, теперь лежит на виду.')
        self.revealed = True
        return message


    def place(self, room):
        """ 
        Размещает секрет в комнате
        """
        self.room = room
        self.floor = room.floor
        room.secrets.append(self)
        room.action_controller.add_actions(self)