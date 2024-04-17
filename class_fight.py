from functions import tprint

class Fight:
    
    def __init__(
        self,
        game,
        who_started,
        fighters:list
    ):
        self.game = game
        self.who_started = who_started
        self.fighters = fighters
        self.create_queue()
        self.hero_in_fight = self.check_hero_in_fight()
    
    
    def tprint(self, message:str|list[str]) -> None:
        if self.hero_in_fight:
            tprint(self.game, message)
        
    
    def create_queue(self) -> None:
        return
    
    
    def check_hero_in_fight(self) -> bool:
        for fighter in self.fighters:
            if fighter.is_hero():
                return True
            return False
    
    
    def showsides(self) -> list:
        message = ['В схватке участвуют:']
        for fighter in self.fighters:
            message.append(fighter.generate_in_fight_description())
        self.tprint(message)