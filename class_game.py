import json

from class_castle import Floor
from class_hero import Hero
from class_items import Book, Key, Map, Matches, Rune, Spell
from class_potions import Potion, HealPotion, HealthPotion, StrengtheningPotion, StrengthPotion, IntelligencePotion, EnlightmentPotion, DexterityPotion, EvasionPotion, Antidote
from class_monsters import Berserk, Monster, Plant, Shapeshifter, Vampire, Corpse, Animal, WalkingDead
from class_protection import Armor, Shield
from class_room import Furniture
from class_weapon import Weapon
from class_allies import Trader
from class_backpack import Backpack
from functions import randomitem, tprint
from settings import *


class Empty():
    
    """
    Класс пустого объекта. Используется вместо объектов игры, 
    таких, как мечи, щиты, защита, монстры, чтобы обозначить, что их нет.
    
    """
    
    def __init__(self):
        self.empty = True
        self.frightening = False
        self.agressive = False


class Game():
    
    """
    Класс игры. 
    Хранит состояния игры. 
    Содержит методы создания объектов игры, а также методы обработки комманд игрока.
    
    """
    
    def __init__(self, chat_id:str, bot, hero:Hero=None):
        self.classes = { 
            'монстр': Monster,
            'мертвец': WalkingDead,
            'герой': Hero,
            'оружие': Weapon,
            'щит': Shield,
            'доспех': Armor,
            'притворщик': Shapeshifter,
            'мебель': Furniture,
            'вампир': Vampire,
            'берсерк': Berserk,
            'растение': Plant,
            'животное': Animal,
            'труп': Corpse,
            'ключ': Key,
            'карта': Map,
            'спички': Matches,
            'книга': Book,
            'зелье': Potion,
            'руна': Rune,
            'заклинание': Spell,
            'торговец': Trader,
            'рюкзак': Backpack,
            'зелье исцеления': HealPotion,
            'зелье здоровья': HealthPotion,
            'зелье силы': StrengthPotion,
            'зелье усиления': StrengtheningPotion,
            'зелье ловкости': DexterityPotion,
            'зелье увертливости': EvasionPotion,
            'зелье ума': IntelligencePotion,
            'зелье просветления': EnlightmentPotion,
            'противоядие': Antidote,
            }
        self.empty_thing = Empty()
        self.how_many_monsters = 0
        self.state = 0
        """
        Текущее состояние игры:
        - 0 - обычное состояние. Персонаж ходит, исследует и т.п.
        - 1 - происходит бой
        - 2 - персонаж что-то улучшает
        - 3 - персонаж поднимает уровень
        - 4 - персонадж использует вещь во время боя
        
        TODO: Перевести параметр на ENUM. 
        """
        self.selected_item = self.empty_thing
        self.chat_id = chat_id
        self.bot = bot
        self.all_corpses = []
        self.no_weapon = Weapon(self, empty=True)
        self.no_shield = Shield(self, empty=True)
        self.no_armor = Armor(self, empty=True)
        self.no_backpack = Backpack(self, no_backpack=True)
        self.castle_floors = self.create_floors()
        self.current_floor = self.castle_floors[0]
        self.player = self.check_hero(hero=hero)
        self.player.current_position = self.current_floor.plan[0]
        self.current_floor.plan[0].visited = '+'
        new_key = Key(self)
        self.player.backpack + new_key
        self.game_is_on = False
        

    def trigger_on_movement(self):
        self.raise_dead()
        
    
    def raise_dead(self):
        for corpse in self.all_corpses: 
            if corpse.can_resurrect:
                corpse.try_to_rise()
    
    
    def check_hero(self, hero:Hero) -> Hero:
        
        """
        Функция проверяет, передан ли в игру герой. 
        Если не передан, то создает нового героя с настройками по умолчанию.
        
        """
        
        if not hero:
            hero = self.create_objects_from_json('hero.json')[0]
        return hero
    
    
    def create_floors(self) -> list[Floor]:
        
        """Функция создает этажи замка"""
        
        floors = []
        for i in s_castle_floors_sizes:
            floor = Floor(self, i[0], i[1], i[2])
            floors.append(floor)
        return floors
    
    
    def __del__ (self):
        print("=" * 40)
        print('Игра удалена')
        print("=" * 40)

    
    def create_objects_from_json(self, file:str, random:bool=False, how_many:int=None, obj_class:str=None) -> list:
        
        """
        Функция создает список объектов из файла JSON. 
        Получает на вход следующие параметры:
        - file - имя файла, содержащего данные;
        - random - нужно ли создавать случайный набор объектов из прочитанных данных?
        - how_many - сколько объектов нужно прочитать из файла и вернуть?
        
        Очевидно, что передавать random без how_many не имеет смысла.
        
        """
        
        objects = []
        with open(file, encoding='utf-8') as read_data:
            parsed_data = json.load(read_data)
        if obj_class and isinstance(obj_class, str):
            parsed_data = [i for i in parsed_data if i['class'] == obj_class]
        if random:
            for _ in range(how_many):
                i = randomitem(parsed_data, False)
                new_game_object = self.object_from_json(json_object=i)
                objects.append(new_game_object)
        else:
            for i in parsed_data:
                new_game_object = self.object_from_json(json_object=i)
                objects.append(new_game_object)
        return objects
    
          
    def create_random_weapon(self, how_many:int=1, weapon_type:str=None) -> Weapon | list[Weapon]:
        objects = []
        with open('weapon.json', encoding='utf-8') as read_data:
            parsed_data = json.load(read_data)
        if weapon_type:
            parsed_data = [i for i in parsed_data if i['type'] == weapon_type]
        for _ in range(how_many):
            i = randomitem(parsed_data, False)
            new_game_object = self.object_from_json(json_object=i)
            objects.append(new_game_object)
        if len(objects) == 1:
            return objects[0]
        return objects
    
    
    def object_from_json(self, json_object:object) -> object:
        
        """Функция создания одного объекта игры из объекта JSON."""
        
        new_object = self.classes[json_object['class']](self)
        for param in json_object:
            vars(new_object)[param] = json_object[param]
        new_object.on_create()
        return new_object
    
    
    def action(self, command:str, message:str):
        
        """Функция обработки комманд от игрока."""
        
        answer = message.lower()
        player = self.player
        if command in s_game_common_commands and self.state == 0:
            if not player.game_over('killall'):
                player.do(message.lower())
            return True
        elif command in s_game_level_up_commands and self.state == 3:
            player.levelup(command)
            return True
        elif self.state == 2:
            return self.rune_actions(answer=answer)
        elif self.state == 4:
            return self.in_fight_actions(answer=answer)
        elif command in s_game_fight_commands and self.state == 1:
            return self.fight_actions(answer=answer)
        tprint (self, f'{player.name} такого не умеет.', 'direction')

    
    def rune_actions(self, answer:str) -> bool:
        
        """
        Функция обрабатывает команды игрока когда он улучшает предметы при помощи рун.
        
        Возвращает:
        - True - если удалось улучшить предмет
        - False - если предмет по любой причине не улучшился
        
        """
        
        player = self.player
        rune_list = self.player.backpack.get_items_by_class(Rune)
        if answer == 'отмена':
            self.state = 0
            return False
        elif answer.isdigit() and int(answer)  <= len(rune_list):
            chosen_rune = rune_list[int(answer) - 1]
            if self.selected_item.enchant(chosen_rune):
                tprint(self, f'{player.name} улучшает {self.selected_item.lexemes["occus"]} новой руной.', 'direction')
                player.backpack.remove(chosen_rune)
                self.state = 0
                return True
            else:
                tprint(self, f'Похоже, что {player.name} не может вставить руну в {self.selected_item.lexemes["occus"]}.', 'direction')
                self.state = 0
                return False
        else:
            tprint(self, f'{player.name} не находит такую руну у себя в карманах.', 'direction')
        return True
    
    
    def in_fight_actions(self, answer:str) -> bool:
        
        """
        Функция обрабатывает команды игрока когда он что-то использует во время боя.
        
        Возвращает:
        - True - если удалось использовать предмет
        - False - если предмет по любой причине не был использован
        
        """

        player = self.player
        can_use = self.selected_item
        if answer == 'отмена':
            self.state = 1
            tprint(self, f'{player.name} продолжает бой.', 'fight')
            return False
        elif answer.isdigit() and int(answer) - 1 < len(can_use):
            item = can_use[int(answer) - 1]
            if item.use(who_using=self.player, in_action=True):
                self.selected_item.remove(item)
                return True
            else:
                tprint(self, f'Похоже, что {player.name} не может использовать {item.lexemes["occus"]}.', 'fight')
                self.state = 1
                return False
        else:
            tprint(self, f'{player.name} не находит такую вкщь у себя в карманах.', 'fight')
        return True
    
    
    def fight_actions(self, answer:str) -> bool:
        
        """
        Функция обрабатывает команды игрока когда он дерется с монстром.
                
        """

        player = self.player
        enemy = self.player.current_position.monsters('first')
        tprint(self, player.attack(enemy, answer))
        if player.run:
            player.run = False
            player.look()
            self.state = 0
        elif enemy.run:
            self.state = 0
        elif enemy.health > 0 and self.state == 1:
            enemy.attack(player)
        elif self.state == 1:
            tprint(self, f'{player.name} побеждает в бою!', 'off')
            self.state = 0
            enemy.lose(player)
            player.win(enemy)
        return True
    
    
    def monsters(self):
        return self.how_many_monsters
    
    
    def test(self, hero:Hero):
        floor = self.current_floor
        rooms = [room for room in floor.plan if room.position in [1, 5, 6]]
        for room in rooms:
            monster = self.create_objects_from_json('monsters.json', True, 1, 'мертвец')[0]
            floor.all_monsters.append(monster)
            floor.monsters_in_rooms[room] = []
            monster.place(floor, room)
            tprint(self, [monster.name, monster.stren, monster.health])
            monster.become_a_zombie()
            