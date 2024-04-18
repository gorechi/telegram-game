from functions import tprint
from collections import deque
from enums import state_enum

class Fight:
    
    def __init__(
        self,
        game,
        hero,
        who_started,
        fighters:list
    ):
        self.game = game
        self.hero = hero
        self.who_started = who_started
        self.fighters = fighters
        self.finished = False
        self.queue = self.create_queue()
        self.hero_in_fight = self.check_hero_in_fight()
    
    
    def tprint(self, message:str|list[str]) -> None:
        if self.hero:
            tprint(self.game, message)
        
    
    def create_queue(self) -> None:
        queue = deque()
        fighters = self.fighters.copy()
        queue.append(self.who_started)
        fighters.remove(self.who_started)
        fighters.sort(key = lambda fighter: fighter.generate_initiative(), reverse=True)
        for fighter in fighters:
            queue.append(fighter)
        return queue
    
    
    def check_hero_in_fight(self) -> bool:
        for fighter in self.fighters:
            if fighter.is_hero():
                return True
            return False
    
    
    def show_sides(self) -> list:
        message = ['В схватке участвуют:']
        for fighter in self.fighters:
            message.append(fighter.generate_in_fight_description())
        self.tprint(message)
        
        
    def start(self) -> None:
        self.hero.current_fight = self
        self.hero.state = state_enum.FIGHT
        message = ['Начинается жестокая схватка!']
        message.extend(self.show_sides())
        self.tprint(message)
        self.sequence()
    
    
    def sequence(self):
        while self.queue[0] != self.hero:
            fighter = self.queue[0]
            targets = self.fighters.copy().remove(fighter)
            if not targets:
                return
            fighter.fight(targets)
    
    
    def remove_fighter(self, fighter) -> bool:
        self.fighters.remove(fighter)
        if fighter == self.hero:
            self.hero = None
        self.queue.remove(fighter)
        return True            