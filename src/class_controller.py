import json
from random import randint

from src.class_dice import Dice
from src.functions.functions import randomitem

class Controller:
    """Базовый класс контроллера чего-либо"""

    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates()
        self.all_controllers = []


    def load_templates(self, path:str) -> list:
        """Загружает шаблоны контроллеров из файла"""

        with open(path, encoding='utf-8') as read_data:
            parsed_data = json.load(read_data)
        if not parsed_data:
            raise FileExistsError(f'Не удалось прочитать данные из файла {path}')
        templates = []
        for i in parsed_data:
            new_template = self.__class__.Template(**{k: v for k, v in i.items()})
            templates.append(new_template)
        return templates


    def get_random_objects_by_class_name(self, class_name:str, how_many:int=1) -> list:
        templates = self.get_templates_by_class_name(class_name)
        objects = []
        for _ in range(how_many):
            template = randomitem(templates)
            new_object = self.create_object_from_template(template)
            objects.append(new_object)
        return objects
    
    
    def get_templates_by_class_name(self, class_name:str) -> list:
        """Возвращает список шаблонов по классу"""

        if not isinstance(class_name, str):
            raise TypeError(f"Параметр 'class_name' должен быть строкой, а передан {type(class_name)} {class_name}.")
        return [template for template in self.templates if template.class_name == class_name]


    def get_template_by_name(self, name:str):
        """Возвращает шаблон по его имени"""

        if not isinstance(name, str):
            raise TypeError(f"Параметр 'name' должен быть строкой, а передан {type(name)} {name}.")
        for template in self.templates:
            if template.name == name:
                return template
        raise ValueError(f"Шаблон с именем '{name}' не найден.")
    
    
    def create_object_from_template(self, template):
        """Создает монстра из шаблона"""

        if not isinstance(template, self.__class__.Template):
            raise TypeError(f"Параметр 'template' должен быть экземпляром класса Template, а передан {type(template)} {template}.")
        object_class = self.__class__._classes[template.class_name]
        if not object_class:
            raise ValueError(f"Класс '{template.class_name}' не найден.")
        new_object = object_class(game=self.game)
        template_dict = template.__dict__
        for param, data in template_dict.items():
            setattr(new_object, param, self.generate_value(data))
        new_object.on_create()
        self.how_many += 1
        self.all_objects.append(new_object)
        self.additional_actions(new_object)
        return new_object

    
    def additional_actions(self, item) -> bool:
        return True
    

    def generate_value(self, data):
        """Генерирует значение для параметра"""
        
        if not isinstance(data, dict):
            return data
        rand = data.get('random')
        dice = data.get('dice')
        value = data.get('value')
        if rand:
            value = randint(value[0], value[1])
            if dice:
                return Dice([value])
            return value
        if dice:
            return Dice([value])    
        return data
    

    def create_object_by_name(self, name:str):
        """Создает монстра по имени"""
        
        template = self.get_template_by_name(name)
        if not template:
            raise ValueError(f"Шаблон с именем '{name}' не найден.")
        return self.create_object_from_template(template)
    
    
    def check_endgame(self) -> bool:
        """Проверяет, достигнут ли конец игры"""
        
        return False

    def get_empty_object_by_class_name(self, class_name:str):
        new_class = self.__class__._classes[class_name]
        new_object = new_class(game=self.game)
        new_object.empty = True
        return new_object
    
    
    def get_random_object_by_filters(self, **filters):
        """Возвращает случайный объект, удовлетворяющий заданным фильтрам"""
        
        template = self.get_random_template_by_filters(filters)
        return self.create_object_from_template(template)
    
    
    def get_random_template_by_filters(self, filters:dict):
        """Возвращает случайный шаблон, удовлетворяющий заданным фильтрам"""

        filtered_templates = [template for template in self.templates if all(getattr(template, key) == value for key, value in filters.items())]
        if not filtered_templates:
            raise ValueError("Нет подходящих шаблонов.")
        return randomitem(filtered_templates)
