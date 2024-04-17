from functions import tprint

class Fight:
    
    def __init__(
        self,
        game,
        fighters:list
    ):
        self.game = game
        self.fighters = fighters
    
    
    def tprint(self, message:str|list[str]) -> None:
        tprint(self.game, message)