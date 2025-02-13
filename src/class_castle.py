from src.class_items import Map, Matches
from src.class_room import Room, Ladder
from src.class_allies import Trader
from src.functions.functions import randomitem


class Floor:
            
    def __init__(self, game):
        """
        Инициирует экземпляр класса Floor
        """
        self.game = game
        self.monsters_in_rooms = {}
                
    
    def on_create(self):
        """
        Выполняет дополнительные действия после инициации экземпляра класса Floor
        """
        return True
    
    
    # def get_rooms_around(self, room:Room, ladders:bool=True) -> list[Room]:
    #     """
    #     Возвращает список всех комнат, в которые можно перейти из заданной комнаты.
    #     """
    #     available_rooms = []
    #     for door in room.doors:
    #         if door and not door.locked and not door.empty:
    #             available_rooms.append(door.get_another_room(room))
    #     if ladders:
    #         if room.ladder_down and not room.ladder_down.locked:
    #             available_rooms.append(room.ladder_down.room_down)
    #         if room.ladder_up and not room.ladder_up.locked:
    #             available_rooms.append(room.ladder_up.room_up)
    #     return available_rooms
    
    
    def create_ladders(self, next_floor) -> bool:
        """
        Создает лестницы между этажами.
        """
        for _ in range(self.how_many['лестницы']):
            room = self.get_room_to_place_ladder_up()
            room_to_go = next_floor.get_room_to_place_ladder_down()
            new_ladder = Ladder(room, room_to_go)
            room_to_go.enter_point = True
        return True
    
    
    def get_room_to_place_ladder_up(self) -> Room:
        """
        Возвращает случайную комнату, в которую можно поставить лестницу вверх.
        """
        rooms = [room for room in self.plan if not room.ladder_up]
        return randomitem(rooms)
    
    
    def get_room_to_place_ladder_down(self) -> Room:
        """
        Возвращает случайную комнату, в которую можно поставить лестницу вниз.
        """
        rooms = [room for room in self.plan if not room.ladder_down]
        return randomitem(rooms)
    
    
    def inhabit(self):
        
        """
        Функция населяет этаж замка всякими монстрами и штуками. 
        Отвечает за наполнение этажа всем содержимым.
        """    
        
        # Создаем мебель и разбрасываем по замку
        self.place_furniture()
        
        # Создаем очаги и разбрасываем по замку
        self.place_rest_places()
        
        # Создаем торговцев и рассаживаем по этажу
        self.place_traders()
        
        # Читаем монстров из файла и разбрасываем по замку
        self.place_monsters()
        
        # Читаем оружие из файла и разбрасываем по замку
        self.place_weapons()
        
        # Читаем щиты из файла и разбрасываем по замку
        self.place_shields()
        
        # Читаем доспехи из файла и разбрасываем по замку
        self.place_armor()
        
        # Читаем зелья из файла и разбрасываем по замку
        self.place_potions()
        
        # Создаем руны и разбрасываем по замку
        self.place_runes()
        
        # Создаем книги и разбрасываем по замку
        self.place_books()
        
        # Помещаем на этаж карту
        self.place_map() 
        
        # Помещаем на этаж спички
        self.place_matches()

     
    def place_matches(self):
        """
        Раскидывает по этажу спички
        """
        matches = Matches(self.game)
        matches.place(self)

    
    def place_traders(self):
        """
        Рассаживает по этажу торговцев
        """
        for _ in range(self.how_many['торговец']):
            trader = Trader.random_trader(self.game, self)
            trader.place()
    
    
    def place_map(self):
        """
        Раскидывает по этажу карты
        """
        new_map = Map(self.game, self)
        new_map.place()

    
    def place_books(self):
        """
        Раскидывает по этажу книги
        """
        for _ in range(self.how_many['книга']):
            new_book = self.game.books_controller.get_random_object_by_filters()
            new_book.place(self)

    
    def place_runes(self):
        """
        Раскидывает по этажу руны
        """
        for _ in range(self.how_many['руна']):
            new_rune = self.game.runes_controller.get_random_object_by_filters()
            new_rune.place(self)
    
    
    def activate_traps(self):
        """
        Активирует на этаже ловушки
        """
        all_furnitures = [f for f in self.all_furniture if f.can_contain_trap and not f.trap.activated]
        furnitures = randomitem(all_furnitures, how_many=self.how_many['ловушка'])
        for f in furnitures:
            f.trap.activate()
            f.trap.set_difficulty(self.traps_difficulty)

    
    def place_potions(self):
        """
        Раскидывает по этажу зелья
        """
        self.all_potions = [] 
        for _ in range(self.how_many['зелье']):
            new_potion = self.game.potions_controller.get_random_object_by_filters()
            self.all_potions.append(new_potion)
            new_potion.place(self)

    
    def place_armor(self):
        """
        Раскидывает по этажу доспехи
        """
        self.all_armor = self.game.protection_controller.get_random_objects_by_class_name(
            class_name = 'Armor',
            how_many=self.how_many['доспех'],
        )
        for armor in self.all_armor:
            armor.place(self)

    
    def place_shields(self):
        """ 
        Раскидывает по этажу щиты 
        """
        self.all_shields = self.game.protection_controller.get_random_objects_by_class_name(
            class_name = 'Shield',
            how_many=self.how_many['щит'],
        )
        for shield in self.all_shields:
            shield.place(self)

    
    def place_weapons(self):
        """
        Раскидывает по этажу оружие
        """
        self.all_weapon = self.game.weapon_controller.get_random_objects_by_class_name(
            class_name = 'Weapon',
            how_many=self.how_many['оружие'],
        )
        for weapon in self.all_weapon:
            weapon.place(self)
            print(weapon)

    
    def place_monsters(self):
        """
        Создает монстров на этаже.
        """
        self.all_monsters = self.game.monsters_controller.create_monsters_by_floor(self)
        for monster in self.all_monsters:
            monster.place(self)

    
    def place_rest_places(self):
        """
        Создает на этаже места отдыха
        """
        rest_places_number = self.how_many['очаг']
        enter_points = self.get_enter_points()
        for enter_point in enter_points:
            rest_place = self.game.furniture_controller.get_random_object_by_filters(can_rest=True)
            rest_place.place(self, room_to_place=enter_point)
            rest_places_number -= 1
        if rest_places_number > 0:
            for _ in range(rest_places_number):
                rest_place = self.game.furniture_controller.get_random_object_by_filters(can_rest=True)
                rest_place.place(self)

    
    def place_furniture(self):
        """
        Расставляет по этажу мебель
        """
        for _ in range(self.how_many['мебель']):
            new_furniture = self.game.furniture_controller.get_random_object_by_filters(can_rest=False)
            new_furniture.place(self)

    
    def secret_rooms(self):
        """
        Возвращает список комнат, в которых есть секретные тайные места
        """
        return [i for i in self.plan if i.secret_word]
    
    
    # def stink(self, room:Room, stink_level:int):
    #     """
    #     Функция распространения вони по замку.\n
    #     Распространяет вонь через открытые и закрытые двери, постепенно уменьшая уровень.\n
    #     Уровень вони записывается в параметр stink комнаты.
    #     """
    #     if room.stink >= stink_level:
    #         return True
    #     else:
    #         room.stink = stink_level
    #     available_rooms = self.get_rooms_around(room)
    #     if stink_level > 1:
    #         for next_room in available_rooms:
    #             self.stink(next_room, stink_level - 1)
    #     return True

    
    def stink_map(self):
        
        """
        Генерирует карту вони этажа замка. 
        Нужна в основном для отладки, но может потом и понадобится.
        """
        for i in range(self.rows):
            floor = ''
            for j in range(self.rooms):
                floor = f'{floor + str(self.plan[i*self.rooms + j].stink)} '

    
    def get_random_room_with_furniture(self) -> Room:
    
        """ 
        Возвращает случайную комнату с мебелью. 
        """
        rooms = [a for a in self.plan if a.furniture]
        return randomitem(rooms)
    
    
    def get_random_unlocked_room(self) -> Room:
        
        """
        Возвращает случайную незапертую комнату.
        """
        rooms = [a for a in self.plan if (not a.locked)]
        return randomitem(rooms)
    
    
    def get_enter_points(self) -> list[Room]:
        """
        Возвращает список точек входа на этаж.
        """
        return [room for room in self.plan if room.enter_point]
