
class SecretPlace:
    
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
                "condition": "is_revealed",
                "duration": 2
                },
        }

    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    

    def get_names_list(self, cases:list=None) -> list:
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


    def is_revealed(self):
        return self.revealed
    

    def place(self, room):
        self.room = room
        self.floor = room.floor
        room.secrets.append(self)
        room.action_controller.add_actions(self)