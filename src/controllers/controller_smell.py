from dataclasses import dataclass
from collections import deque

class SmellController():
    """
    Класс для управления вонью в замке.
    """    
    @dataclass
    class Source():
        source: object
        rooms: dict
        smell_type: str


    _smell_types = [
        'monster',
        'dead'
    ]
    

    def __init__(self, game):
        self.game = game
        self.smells = list()


    def create_smell_source(self, 
                     room: object,
                     source: object,
                     intensity: int,
                     smell_type: str,
                     ) -> None:
        """
        Создает новый источник вони.
        """
        if not smell_type in SmellController._smell_types:
            raise ValueError(f'При создании источника запаха передан несуществующий тип {smell_type}')
        new_source = SmellController.Source(
            source = source,
            smell_type = smell_type,
            rooms = self.distribute_smell(room = room, intensity = intensity)
        )
        self.smells.append(new_source)


    def distribute_smell(self, room: object, intensity:int) -> dict:
        rooms = dict()
        self.add_room(rooms, room, intensity, None)
        return rooms    


    def add_room(self, rooms:dict, room: object, intensity:int, source_room: object) -> None:
        stored = rooms.get(room)
        if not stored or intensity > stored['intensity']:
            rooms[room] = {
                'intensity': intensity, 
                'source_room': source_room
                }
        if intensity > 1:
            self.spread_smell(rooms, room, intensity, source_room)


    def spread_smell(self, rooms:dict, room: object, intensity:int, source_room: object) -> None:
        available_rooms = room.get_rooms_around()
        for next_room in available_rooms:
            if not next_room == source_room:
                self.add_room(rooms, next_room, intensity - 1, room)