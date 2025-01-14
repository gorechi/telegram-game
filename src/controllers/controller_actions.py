from dataclasses import dataclass
from typing import Protocol

class ItemProtocol(Protocol):
    """
    Протокол для объектов, которые можно использовать.
    """
    
    def get_names_list(self, cases:list=None) -> list:
        ...
    
    name: str
    hero_actions: list


class ActionController():  
    
    @dataclass
    class Item():
        item: ItemProtocol
        names: list
        action: object
        name:str
    
    
    def __init__(self, game, hero=None, room=None):
        self.game = game
        self.hero = hero
        self.room = room
        self.actions = {}
        self.items = []
        
    
    def add_actions(self, item:ItemProtocol) -> bool:
        item_name = item.name
        item_names = item.get_names_list(['nom', "accus"])
        actions = item.hero_actions
        for action, value in actions.items():
            method = getattr(item, value)
            new_item = self.Item(
                item = item, 
                names = item_names, 
                action = method, 
                name = item_name
                )
            self.items.append(new_item)
            if not self.actions.get(action, None):
                self.actions[action] = []
            self.actions[action].append(new_item)
        print(f'actions: {self.actions}')
        return True
    
    
    # def add_actions(self, actions:dict) -> bool:
    #     """
    #     Добавляеет новые действия в контроллер.
    #     :param actions: Словарь, где ключи - названия действий, а значения - словари с параметрами действий.
    #     """
    #     if not isinstance(actions, dict):
    #         raise ValueError("Значение параметра actions должено быть словарем, но получено: {actions}")
    #     for key, value in actions.items():
    #         print(f'key: {key}, value: {value}')
    #         if not self.actions.get(key, None):
    #             self.actions[key] = {}
    #         for key2, value2 in value.items():
    #             self.actions[key][key2] = value2
    #     print(f'В контроллер добавлены новые действия: {self.actions}')
    #     return True
    
    
    # def delete_actions_by_item(self, item) -> bool:
    #     """
    #     Удаляет действия из контроллера для определенного предмета.
    #     """
    #     for key, value in self.actions.items():
    #         if item in value:
    #             del self.actions[key][item]    
    #     print(f'Из контроллера удалены действия: {self.actions}')
    #     return True
    
    
    def delete_actions_by_item(self, item) -> bool:
        """
        Удаляет действия из контроллера для определенного предмета.
        """
        items_to_delete = self.get_items_by_filters(item=item)
        for key, value in self.actions.items():
            self.actions[key] = [item for item in value if item not in items_to_delete]
        print('-'*40)
        print(f'actions: {self.actions}')
        return True
    
    
    def get_items_by_action(self, action: str, item: str=None) -> list:
        """
        Возвращает список экземпляров дата-класса Item, которые могут быть использованы для выполнения действия.
        """
        if item:
            items = self.get_items_by_filters()
        return self.actions.get(action, [])
    
    
    def get_items_by_filters(self, **filters) -> list:
        """Возвращает случайный объект, удовлетворяющий заданным фильтрам"""
        return [item for item in self.items if all(getattr(item, key) == value for key, value in filters.items())]
    
    
    def get_items_by_action_and_name(self, action:str, name: str=None) -> list:
        """
        Возвращает список экземпляров дата-класса Item, которые имеют заданное имя.
        """
        items_list = self.actions[action]
        if name:
            return [item for item in items_list if name.lower() in item.names]
        return items_list