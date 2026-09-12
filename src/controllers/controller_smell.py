from dataclasses import dataclass
from collections import deque

class SmellController():
    """
    Класс для управления вонью в замке.
    """    
    @dataclass
    class Source():
        """
        Dataclass источника вони в замке.
        """
        source: object
        rooms: dict
        smell_type: str


    _smell_types = [
        'monster',
        'dead'
    ]
    

    def __init__(self, game):
        """
        Инициирует экземпляр класса SmellController.
        """
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
        Проверяет существование типа вони и записывает карту ее распространения.
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
        """
        Распределяет вонь от указанной комнаты по графу замка с убыванием интенсивности.
        Возвращает словарь комнат с уровнем вони и комнатой-предшественником.
        """
        rooms = dict()
        self.add_room(rooms, room, intensity, None)
        return rooms    


    def add_room(self, rooms:dict, room: object, intensity:int, source_room: object) -> None:
        """
        Добавляет комнату в словарь вони, сохраняя максимальную интенсивность.
        При интенсивности выше единицы распространяет вонь в соседние комнаты.
        """
        stored = rooms.get(room)
        if not stored or intensity > stored['intensity']:
            rooms[room] = {
                'intensity': intensity, 
                'source_room': source_room
                }
        if intensity > 1:
            self.spread_smell(rooms, room, intensity, source_room)


    def spread_smell(self, rooms:dict, room: object, intensity:int, source_room: object) -> None:
        """
        Распространяет вонь из комнаты в соседние, не возвращаясь в комнату, откуда она пришла.
        """
        available_rooms = room.get_rooms_around()
        for next_room in available_rooms:
            if not next_room == source_room:
                self.add_room(rooms, next_room, intensity - 1, room)


    def decrease_intensity(self, source:Source, intensity_delta:int) -> bool:
        """
        Уменьшает интенсивность вони всех комнат источника на величину дельты.
        Удаляет записи с интенсивностью ниже единицы.
        Возвращает True при успешном уменьшении.
        """
        if not isinstance(intensity_delta, int):
            raise TypeError(f'При уменьшении вони от источника {source.source} в метод передана дельта {intensity_delta} с типом, отличным от int.')
        to_delete = list()
        for key, value in source.rooms.items():
            source.rooms[key]['intensity'] -= intensity_delta
            if source.rooms[key]['intensity'] < 1:
                to_delete.append(key)
        for room in to_delete:
            source.rooms.pop(room)
        return True


    def increase_intensity(self, source:Source, intensity_delta:int) -> bool:
        """
        Увеличивает интенсивность вони всех комнат источника на величину дельты.
        До-распространяет вонь от границы распространения в новые комнаты.
        Возвращает True при успешном увеличении.
        """
        if not isinstance(intensity_delta, int):
            raise TypeError(f'При увеличении вони от источника {source.source} в метод передана дельта {intensity_delta} с типом, отличным от int.')
        to_spread = list()
        for key, value in source.rooms.items():
            if source.rooms[key]['intensity'] == 1:
                to_spread.append(key)
            source.rooms[key]['intensity'] += intensity_delta
        for room in to_spread:
            rooms = source.rooms
            intensity = source.rooms[room]['intensity']
            source_room = source.rooms[room]['source_room']
            self.spread_smell(rooms, room, intensity, source_room)
        return True


    def get_smell_by_smell_type(self, room:object, smell_type:str) -> int:
        """
        Возвращает максимальную интенсивность вони указанного типа в комнате.
        """
        smell_intensity = 0
        for source in self.smells:
            if source.smell_type == smell_type:
                smell = source.rooms.get(room, None)
                if smell and smell['intensity'] > smell_intensity:
                    smell_intensity = smell['intensity']
        return smell_intensity


    def get_max_smells(self, room:object) -> dict:
        """
        Возвращает словарь типов вони с максимальной интенсивностью для указанной комнаты.
        """
        smells_dic = dict()
        for source in self.smells:
            smell = source.rooms.get(room, None)
            if smell:
                smell_level_to_compare = smells_dic.get(source.smell_type, 0)
                if smell['intensity'] > smell_level_to_compare:
                    smells_dic[source.smell_type] = smell['intensity']
        return smells_dic


    def get_max_smell_objects_by_smell_type(self, room:object, smell_type:str) -> list[object]:
        """
        Возвращает список источников вони указанного типа с максимальной интенсивностью в комнате.
        """
        smell_intensity = 0
        smells_list = list()
        for source in self.smells:
            if source.smell_type == smell_type:
                smell = source.rooms.get(room, None)
                if smell and smell['intensity'] > smell_intensity:
                    smells_list = []
                    smells_list.append(source)
                    smell_intensity = smell['intensity']
                elif smell and smell['intensity'] == smell_intensity:
                    smells_list.append(source)
        return smells_list