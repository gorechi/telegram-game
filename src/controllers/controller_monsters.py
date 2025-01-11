from dataclasses import dataclass

from src.class_monsters import Monster, Plant, Vampire, Corpse, Animal, WalkingDead, Skeleton, Berserk, Human, Demon
from src.class_controller import Controller
from src.class_basic import Money
from src.functions.functions import randomitem

class MonstersController(Controller):
    """Класс для управления монстрами."""

    @dataclass
    class Template():
        class_name: str
        name: str
        lexemes: dict
        stren: dict
        health: dict
        hit_chance: dict
        parry_chance: dict
        can_hide: bool
        can_run: bool
        actions: list
        state: str
        frightening: bool
        aggressive: bool
        carry_weapon: bool
        carry_shield: bool
        poison_level: dict
        poison_protection: dict
        gender: int
        size: dict
        corpse: bool
        monster_type: str
        initiative: dict
        min_floor: int
        max_floor: int
        specific_floors: list
        wear_armor: bool
        preferred_weapon: str
        stink: bool
        can_resurrect: bool
        weakness: dict
        carry_money: bool
        money: int
        boss: bool
    
    
    _classes = {
        "Monster": Monster,
        "Plant": Plant,
        "Vampire": Vampire,
        "Animal": Animal,
        "Corpse": Corpse,
        "WalkingDead": WalkingDead,
        "Skeleton": Skeleton,
        "Berserk": Berserk,
        "Human": Human,
        "Demon": Demon
    }    
    
    
    def __init__(self, game):
        """
        Иницииирует экземпляр контроллера монстров
        """
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/monsters.json')
        self.all_objects = []
    
    
    def additional_actions(self, monster:Monster) -> bool:
        """
        Выполняет дополнительные действия при создании нового монстра
        """
        self.generate_money(monster)
        return True
    
    
    def generate_money(self, monster:Monster) -> None:
        """
        Генерирует деньги для монстра
        """

        if not isinstance(monster, Monster):
            raise TypeError(f"Параметр 'monster' должен быть экземпляром класса Monster, а передан {type(monster)} {monster}.")
        if monster.carry_money:
            money = Money(self.game, monster.money)
            monster.loot.add(money)
        monster.money = None
        return True
    
    
    def get_templates_by_floor(self, floor:int) -> list[Template]:
        """
        Возвращает список всех шаблонов монстров, подходящих по этажу
        """
        
        if not isinstance(floor, int):
            raise TypeError(f"Параметр 'floor' должен быть целым числом, а передан {type(floor)} {floor}.")
        templates_list = []
        for template in self.templates:
            if ((template.min_floor <= floor <= template.max_floor) or floor in template.specific_floors) and not template.boss:
                templates_list.append(template)
        return templates_list
    
    
    def get_random_boss_template(self) -> Template:
        """
        Возвращает случайный шаблон монстра-босса
        """
        boss_templates = [template for template in self.templates if template.boss]
        if not boss_templates:
            raise ValueError("Нет шаблонов монстров-боссов.")
        return randomitem(boss_templates)
    
    
    def get_random_templates_by_floor(self, floor:int, how_many:int=1) -> list[Template]:
        """
        Возвращает список случайных шаблоны монстров по этажу
        """
        if not isinstance(floor, int):
            raise TypeError(f"Параметр 'floor' должен быть целым числом, а передан {type(floor)} {floor}.")
        templates_list = []
        floor_templates = self.get_templates_by_floor(floor)
        for _ in range(how_many):
            templates_list.append(randomitem(floor_templates))
        return templates_list
        
    
    def create_monsters_by_floor(self, floor) -> list[Monster]:
        """
        Создает список монстров для этажа
        """
        how_many = floor.how_many['монстры']
        floor_number = floor.floor_number
        templates_list = self.get_random_templates_by_floor(floor_number, how_many)
        monsters_list = []
        for template in templates_list:
            new_monster = self.create_object_from_template(template)
            monsters_list.append(new_monster)
        if floor.boss:
            monsters_list.append(self.create_random_boss())
        return monsters_list
    
    
    def create_random_boss(self) -> Monster:
        """
        Создает случайного монстра-босса
        """
        boss_template = self.get_random_boss_template()
        new_boss = self.create_object_from_template(boss_template)
        return new_boss
     
    
    def kill_monster(self, monster:Monster) -> bool:
        """
        Убивает монстра
        """
        if not isinstance(monster, Monster):
            raise TypeError(f"Параметр 'monster' должен быть экземпляром класса Monster, а передан {type(monster)} {monster}.")
        self.how_many_monsters -= 1
        self.all_monsters.remove(monster)
        return True
        
    
    def resurect_monster(self, monster:Monster) -> bool:
        """
        Воскрешает монстра
        """
        if not isinstance(monster, Monster):
            raise TypeError(f"Параметр 'monster' должен быть экземпляром класса Monster, а передан {type(monster)} {monster}.")
        self.how_many_monsters += 1
        self.all_monsters.append(monster)
        return True
    
    
    def check_endgame(self) -> bool:
        """
        Проверяет, достигнут ли конец игры, связанный с монстрами
        """
        return self.how_many == 0