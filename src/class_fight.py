from src.functions.functions import tprint, cprint
from src.enums import state_enum

from collections import deque


class Fight:
    """
    Класс схватки.    
    """
    
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
        self.room = self.hero.current_position
        self.finished = False
        self.exp:int = 0
        self.light:bool = self.check_light()
        self.queue = self.create_queue()
        self.hero_in_fight:bool = self.check_hero_in_fight()
        print(self)
    
    
    def __repr__(self) -> str:
        """
        Метод возвращает строковое представление схватки.
        """
        return f'Схватка: {self.fighters}, начал {self.who_started}'
    
    
    def tprint(self, message:str|list[str]) -> None:
        """
        Метод печатает сообщение в зависимости от наличия героя в схватке.
        """
        if self.hero:
            tprint(self.game, message, 'fight')
            return
        cprint(message)
        
    
    def check_light(self) -> bool:
        """
        Метод проверяет, есть ли свет в комнате схватки.
        """
        for fighter in self.fighters:
            if fighter.check_light():
                return True
        return False    
    
    
    def create_queue(self) -> None:
        """
        Метод создает очередь ходов для схватки.
        """
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
        """
        Метод проверяет, участвует ли герой в схватке.
        """
        for fighter in self.fighters:
            if fighter.is_hero():
                return True
        return False
    
    
    def show_sides(self) -> list:
        """
        Метод показывает стороны, участвующие в схватке.
        """
        message = ['В схватке участвуют:']
        for index, fighter in enumerate(self.queue):
            message.append(fighter.generate_in_fight_description(index+1))
        self.tprint(message)
    
    
    def to_the_end_of_the_queue(self, fighter) -> None:
        """
        Метод перемещает бойца в конец очереди.
        """
        self.queue.append(fighter)
        self.queue.popleft()
    
    
    def sequence(self) -> None:
        """
        Метод управляет последовательностью ходов в схватке.
        """
        while self.queue[0] != self.hero:
            fighter = self.queue[0]
            message = fighter.attack(self)
            self.tprint(message)
            self.check_for_losses()
            self.to_the_end_of_the_queue(fighter)
            if self.check_for_the_end():
                return
    
    
    def check_for_the_end(self) -> bool:
        """
        Метод проверяет, закончилась ли схватка.
        """
        if len(self.fighters) > 1:
            if self.hero:
                return False
            for fighter in self.fighters:
                if not fighter == self.hero and fighter.choose_target(self):
                    return False
        return True
        
    
    def remove_fighter(self, fighter) -> bool:
        """
        Метод удаляет бойца из схватки.
        """
        self.fighters.remove(fighter)
        if fighter == self.hero:
            self.hero.current_fight = None
            self.hero.state = state_enum.NO_STATE
            self.hero = None
        self.queue.remove(fighter)
        self.show_sides()
        return True            

    
    def gather_enemies(self) -> None:
        """
        Метод собирает всех врагов в комнате для участия в схватке.
        """
        enemies_in_room = self.room.monsters()
        for enemy in enemies_in_room:
            if enemy not in self.fighters and enemy.want_to_fight(self):
                self.add_fighter(enemy)


    def add_fighter(self, fighter) -> None:
        """
        Метод добавляет бойца в схватку.
        """
        self.fighters.append(fighter)
    
    
    def start(self):
        """
        Метод начинает схватку.
        """
        if self.hero:
            self.hero.state = state_enum.FIGHT
            self.hero.current_fight = self
        self.gather_enemies()
        self.show_sides()
        self.sequence()
        
    
    def continue_after_hero(self):
        """
        Метод продолжает схватку после хода героя.
        """
        self.to_the_end_of_the_queue(self.hero)
        self.show_sides()
        self.sequence()
    
    
    def check_for_losses(self):
        """
        Метод проверяет, есть ли погибшие бойцы.
        """
        for fighter in self.fighters:
            if fighter == self.hero and fighter.health <= 0:
                self.hero_loses()
            if not fighter == self.hero and fighter.health <= 0:
                self.monster_loses(fighter)
        if self.check_for_the_end():
            self.end()
                     
        
    def hero_loses(self) -> bool:
        """
        Метод обрабатывает проигрыш героя.
        """
        self.tprint(self.hero.lose(self))
        return self.remove_fighter(self.hero)
    
    
    def monster_loses(self, fighter) -> bool:
        """
        Метод обрабатывает проигрыш монстра.
        """
        self.tprint(fighter.lose(self))
        if fighter.last_attacker == self.hero:
            self.accumulate_experience(fighter)
        return self.remove_fighter(fighter)
    
    
    def accumulate_experience(self, fighter) -> None:
        """
        Метод накапливает опыт за побежденного монстра.
        """
        self.exp += fighter.exp
        print(f'exp = {self.exp}')
        
    
    def get_fighter_by_strength(self, who=None, exclude:list[str]=[], mode:str='Max'):
        """
        Метод возвращает бойца по силе.
        """
        filtered_fighters = [fighter for fighter in self.fighters if fighter != who and type(fighter).__name__ not in exclude]
        if mode == 'Max':
            return max(self.fighters, key=lambda fighter: fighter.stren) if filtered_fighters else False
        if mode == 'Min':
            return min(self.fighters, key=lambda fighter: fighter.stren) if filtered_fighters else False
        return False
    
    
    def get_fighter_by_health(self, who=None, exclude:list[str]=[], mode:str='Max'):
        """
        Метод возвращает бойца по здоровью.
        """
        filtered_fighters = [fighter for fighter in self.fighters if fighter != who and type(fighter).__name__ not in exclude]
        if mode == 'Max':
            return max(self.fighters, key=lambda fighter: fighter.health) if filtered_fighters else False
        if mode == 'Min':
            return min(self.fighters, key=lambda fighter: fighter.health) if filtered_fighters else False
        return False
    
    
    def get_targets(self, who) -> list:
        """
        Метод возвращает всех бойцов, кроме указанного.
        """
        return [fighter for fighter in self.fighters if fighter != who]
    
    
    def get_targets_exclude_classes(self, classes:list[str]) -> list:
        """
        Метод возвращает всех бойцов, кроме указанных классов.
        """
        return [fighter for fighter in self.fighters if type(fighter).__name__ not in classes]
    
    
    def get_targets_by_class(self, classes:list[str]) -> list:
        """
        Метод возвращает всех бойцов указанных классов.
        """
        return [fighter for fighter in self.fighters if type(fighter).__name__ in classes]