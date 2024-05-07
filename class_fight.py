from functions import tprint, cprint
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
        self.exp:int = 0
        self.light = self.check_light()
        print(f'Light: {self.light}')
        self.queue = self.create_queue()
        self.hero_in_fight = self.check_hero_in_fight()
        print(self)
    
    
    def __repr__(self) -> str:
        return f'Схватка: {self.fighters}, начал {self.who_started}'
    
    
    def tprint(self, message:str|list[str]) -> None:
        if self.hero:
            tprint(self.game, message, 'fight')
            return
        cprint(message)
        
    
    def check_light(self) -> bool:
        for fighter in self.fighters:
            if fighter.check_light():
                return True
        return False    
    
    
    def create_queue(self) -> None:
        queue = deque()
        fighters = self.fighters.copy()
        fighters.remove(self.who_started)
        fighters.sort(key = lambda fighter: fighter.generate_initiative())
        fighters.append(self.who_started)
        fighters.reverse()
        self.fighters = fighters
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
        for index, fighter in enumerate(self.queue):
            message.append(fighter.generate_in_fight_description(index+1))
        self.tprint(message)
    
    
    def to_the_end_of_the_queue(self, fighter) -> None:
        self.queue.append(fighter)
        self.queue.popleft()
    
    
    def sequence(self):
        while self.queue[0] != self.hero:
            fighter = self.queue[0]
            message = fighter.attack(self)
            self.tprint(message)
            self.check_for_losses()
            self.to_the_end_of_the_queue(fighter)
            if self.check_for_the_end():
                return
    
    
    def check_for_the_end(self) -> bool:
        if len(self.fighters) > 1:
            if self.hero:
                return False
            for fighter in self.fighters:
                if not fighter == self.hero and fighter.choose_target(self):
                    return False
        return True
        
    
    def remove_fighter(self, fighter) -> bool:
        self.fighters.remove(fighter)
        if fighter == self.hero:
            self.hero.current_fight = None
            self.hero.state = state_enum.NO_STATE
            self.hero = None
        self.queue.remove(fighter)
        self.show_sides()
        return True            


    def start(self):
        if self.hero:
            self.hero.state = state_enum.FIGHT
            self.hero.current_fight = self
        self.show_sides()
        self.sequence()
        
    
    def continue_after_hero(self):
        self.to_the_end_of_the_queue(self.hero)
        self.show_sides()
        self.sequence()
    
    
    def check_for_losses(self):
        for fighter in self.fighters:
            if fighter == self.hero and fighter.health <= 0:
                self.hero_loses()
            if not fighter == self.hero and fighter.health <= 0:
                self.monster_loses(fighter)
        if self.check_for_the_end():
            self.end()
                     
        
    def hero_loses(self) -> bool:
        self.tprint(self.hero.lose(self))
        return self.remove_fighter(self.hero)
    
    
    def monster_loses(self, fighter) -> bool:
        self.tprint(fighter.lose(self))
        if fighter.last_attacker == self.hero:
            self.accumulate_experience(fighter)
        return self.remove_fighter(fighter)
    
    
    def accumulate_experience(self, fighter) -> None:
        self.exp += fighter.exp
        print(f'exp = {self.exp}')
        
    
    def get_strongest_fighter(self, who=None):
        filtered_fighters = [fighter for fighter in self.fighters if fighter != who]
        return max(self.fighters, key=lambda fighter: fighter.stren) if filtered_fighters else False
    
    
    def get_healthiest_fighter(self, who=None):
        filtered_fighters = [fighter for fighter in self.fighters if fighter != who]
        return max(self.fighters, key=lambda fighter: fighter.health) if filtered_fighters else False
    
    
    def get_targets(self, who) ->list:
        return [fighter for fighter in self.fighters if fighter != who]