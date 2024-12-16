import json
from dataclasses import dataclass

from src.class_monsters import Monster, Plant, Vampire, Corpse, Animal, WalkingDead, Skeleton, Berserk, Human
from src.functions.functions import randomitem

class MonstersController:
    """Класс для управления монстрами."""

    @dataclass
    class MonsterTemplate():
        class_name: str
        name: str
        lexemes: dict
        stren: int
        health: int
        hit_chance: int
        parry_chance: int
        can_hide: bool
        can_run: bool
        actions: list
        state: str
        frightening: bool
        agressive: bool
        carry_weapon: bool
        carry_shield: bool
        venomous: int
        gender: int
        size: int
        corpse: bool
        monster_type: str
        initiative: int
        min_floor: int
        max_floor: int
        specific_floors: list
        wear_armor: bool
        prefered_weapon:str
        stink:bool
        can_resurrect:bool
        weakness:dict
    
    
    _classes = {
        "Monster": Monster,
        "Plant": Plant,
        "Vampire": Vampire,
        "Animal": Animal,
        "Corpse": Corpse,
        "WalkingDead": WalkingDead,
        "Skeleton": Skeleton,
        "Berserk": Berserk,
        "Human": Human
    }    
    
    
    def __init__(self, game):
        self.game = game
        self.how_many_monsters = 0
        self.templates = self.load_templates()
        self.all_monsters = []
    
   
    def load_templates(self):
        """Загружает шаблоны монстров из файла"""
        
        file = 'json/monsters.json'
        with open(file, encoding='utf-8') as read_data:
            parsed_data = json.load(read_data)
        if not parsed_data:
            raise FileExistsError(f'Не удалось прочитать данные из файла {file}')
        templates = []
        for i in parsed_data:
            new_monster_template = MonstersController.MonsterTemplate(**{k: v for k, v in i.items()})
            templates.append(new_monster_template)
        return templates
    
    
    def get_templates_by_class_name(self, class_name:str) -> list[MonsterTemplate]:
        """Возвращает список шаблонов монстров по классу"""

        if not isinstance(class_name, str):
            raise TypeError("Параметр 'class_name' должен быть строкой.")
        return [template for template in self.templates if template.class_name == class_name]
    
    
    def get_template_by_name(self, name:str) -> MonsterTemplate:
        """Возвращает шаблон монстра по его имени"""

        if not isinstance(name, str):
            raise TypeError("Параметр 'name' должен быть строкой.")
        for template in self.templates:
            if template.name == name:
                return template
        raise ValueError(f"Шаблон с именем '{name}' не найден.")

    
    def get_templates_by_floor(self, floor:int) -> list[MonsterTemplate]:
        """Возвращает список всех шаблонов монстров, подходящих по этажу"""
        
        if not isinstance(floor, int):
            raise TypeError("Параметр 'floor' должен быть целым числом.")
        templates_list = []
        for template in self.templates:
            if (template.min_floor <= floor <= template.max_floor) or floor in template.specific_floors:
                templates_list.append(template)
        return templates_list
    
    
    def get_random_templates_by_floor(self, floor:int, how_many:int=1) -> list[MonsterTemplate]:
        """Возвращает список случайных шаблоны монстров по этажу"""
        
        if not isinstance(floor, int):
            raise TypeError("Параметр 'floor' должен быть целым числом.")
        templates_list = []
        floor_templates = self.get_templates_by_floor(floor)
        for _ in range(how_many):
            templates_list.append(randomitem(floor_templates))
        return templates_list
    
    
    def create_monster_from_template(self, template:MonsterTemplate) -> Monster:
        """Создает монстра из шаблона"""

        if not isinstance(template, MonstersController.MonsterTemplate):
            raise TypeError("Параметр 'template' должен быть экземпляром класса MonsterTemplate.")
        monster_class = MonstersController._classes[template.class_name]
        new_monster = monster_class(game=self.game)
        for param in template.__dict__:
            vars(new_monster)[param] = template.__dict__[param]
        new_monster.on_create()
        self.how_many_monsters += 1
        self.all_monsters.append(new_monster)
        return new_monster
    
    
    def create_monsters_by_floor(self, floor:int, how_many:int=1) -> list[Monster]:
        """Создает список монстров для этажа"""
        
        templates_list = self.get_random_templates_by_floor(floor, how_many)
        monsters_list = []
        for template in templates_list:
            new_monster = self.create_monster_from_template(template)
            monsters_list.append(new_monster)
        return monsters_list
    
    
    def create_monster_by_name(self, name:str) -> Monster:
        """Создает монстра по имени"""
        template = self.get_template_by_name(name)
        if not template:
            raise ValueError(f"Шаблон с именем '{name}' не найден.")
        return self.create_monster_from_template(template)
    
    
    def kill_monster(self, monster:Monster) -> bool:
        """Убивает монстра"""
        if not isinstance(monster, Monster):
            raise TypeError("Параметр 'monster' должен быть экземпляром класса Monster.")
        self.how_many_monsters -= 1
        self.all_monsters.remove(monster)
        return True
        
    
    def resurect_monster(self, monster:Monster) -> bool:
        """Воскрешает монстра"""
        if not isinstance(monster, Monster):
            raise TypeError("Параметр 'monster' должен быть экземпляром класса Monster.")
        self.how_many_monsters += 1
        self.all_monsters.append(monster)
        return True
    
    
    def check_endgame(self) -> bool:
        """Проверяет, достигнут ли конец игры"""
        return self.how_many_monsters == 0