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
        in_combat: bool = False
        in_darkness: bool = False
        bulk: bool = False
        on_rest: bool = False
        presentation: object = None
        condition: object = None
          
    
    def __init__(self, game, hero=None, room=None, fight=None):
        self.game = game
        self.hero = hero
        self.room = room
        self.fight = fight
        self.actions = {}
        self.items = []
        
    
    def extract_actions(self, item:ItemProtocol) -> dict:
        """
        Извлекает действия из протокола предмета.
        """
        if self.hero and hasattr(item, 'hero_actions'):
            return item.hero_actions
        if self.room and hasattr(item, 'room_actions'):
            return item.room_actions
        if self.fight and hasattr(item, 'fight_actions'):
            return item.fight_actions
        return dict()
    
    
    def add_actions(self, item:ItemProtocol) -> bool:
        item_name = item.name
        item_names = item.get_names_list(['nom', "accus"])
        actions = self.extract_actions(item)
        for action, value in actions.items():
            method = getattr(item, value.get("method", ''))
            presentation_method = getattr(item, value.get("presentation", ''), None)
            condition_method = getattr(item, value.get("condition", ''), None)
            new_item = self.Item(
                item = item, 
                names = item_names, 
                action = method, 
                name = item_name,
                in_combat = value.get("in_combat", False),
                in_darkness = value.get("in_darkness", False),
                bulk = value.get("bulk", False),
                presentation = presentation_method,
                condition = condition_method,
                )
            print('='*40)
            print(f'Создан item {new_item}')
            print('='*40)
            self.items.append(new_item)
            if not self.actions.get(action, None):
                self.actions[action] = []
            self.actions[action].append(new_item)
        print(f'actions: {self.actions}')
        return True
    
    
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
        return self.actions.get(action, [])
    
    
    def get_items_by_filters(self, **filters) -> list:
        """Возвращает случайный объект, удовлетворяющий заданным фильтрам"""
        return [item for item in self.items if all(getattr(item, key) == value for key, value in filters.items())]
    
    
    def get_items_by_action_and_name(self, action:str, name:str=None, in_darkness:bool=False, in_combat:bool=False) -> list:
        """
        Возвращает список экземпляров дата-класса Item, которые имеют заданное имя.
        """
        items_list = self.actions.get(action, list())
        if name:
            return [item for item in items_list if (name.lower() in item.names)]
        if in_darkness:
            items_list = [item for item in items_list if item.in_darkness == True]
        if in_combat:
            items_list = [item for item in items_list if item.in_combat == True]
        final_list = list()
        for item in items_list:
            if item.condition and item.condition():
                final_list.append(item)
        return final_list