
class SecretPlace:
    
    def __init__(self, game):
        self.game = game
        self.name = None
        self.lexemes = None
        self.room = None
        self.floor = None
        self.loot = None
        self.trap = None

    
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