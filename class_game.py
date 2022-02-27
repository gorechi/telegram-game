import json

from class_castle import Castle
from class_hero import Hero
from class_items import Book, Key, Map, Matches, Potion, Rune, Spell
from class_monsters import Berserk, Monster, Plant, Shapeshifter, Vampire
from class_protection import Armor, Shield
from class_room import Furniture
from class_weapon import Weapon
from functions import randomitem, tprint
from settings import *


class Empty():
    def __init__(self):
        self.empty = True
        self.frightening = False
        self.agressive = False

class Game():
    def __init__(self, chat_id, bot, how_many=0, hero=None):
        self.classes = { 'монстр': Monster,
            'герой': Hero,
            'оружие': Weapon,
            'щит': Shield,
            'доспех': Armor,
            'притворщик': Shapeshifter,
            'мебель': Furniture,
            'вампир': Vampire,
            'берсерк': Berserk,
            'растение': Plant,
            'ключ': Key,
            'карта': Map,
            'спички': Matches,
            'книга': Book,
            'зелье': Potion,
            'руна': Rune,
            'заклинание': Spell,
            }
        self.empty_thing = Empty()
        self.state = 0
        # state - текущее состояние игры.
        # 0 - обычное состояние. Персонаж ходит, исследует и т.п.
        # 1 - происходит бой
        # 2 - персонаж что-то улучшает
        # 3 - персонаж поднимает уровень
        # 4 - персонадж использует вещь во время боя
        self.selected_item = self.empty_thing
        self.game_is_on = False
        self.chat_id = chat_id
        self.bot = bot
        self.no_weapon = Weapon(self, empty=True)
        self.no_shield = Shield(self, empty=True)
        self.no_armor = Armor(self, empty=True)
        self.new_castle = Castle(self, 5, 5)  # Генерируем замок
        if how_many == 0:
            self.how_many = s_how_many
        else:
            self.how_many = how_many
        if not hero:
            self.player = Hero(self,
                               s_hero_name,
                               s_hero_name1,
                               s_hero_gender,
                               s_hero_strength,
                               s_hero_dexterity,
                               s_hero_intelligence,
                               s_hero_health,
                               s_hero_actions)  # Создаем персонажа
        else:
            self.player = hero
        # Создаем мебель и разбрасываем по замку
        self.all_furniture = self.readobjects(file='furniture.json',
                                        howmany=self.how_many['мебель'],
                                        random=True)
        for furniture in self.all_furniture:
            furniture.place(castle=self.new_castle)
        
        # Создаем очаги и разбрасываем по замку
        self.all_rest_places = self.readobjects(file='furniture-rest.json',
                                        howmany=self.how_many['очаг'],
                                        random=False)
        self.all_rest_places[0].place(castle=self.new_castle, room_to_place=self.new_castle.plan[0])
        for rest_place in self.all_rest_places[1:]:
            rest_place.place(self.new_castle)
        
        # Читаем монстров из файла и разбрасываем по замку
        self.all_monsters = self.readobjects(file='monsters.json',
                                       howmany=self.how_many['монстры'])
        for monster in self.all_monsters:
            monster.place(self.new_castle)
        
        # Читаем оружие из файла и разбрасываем по замку
        self.all_weapon = self.readobjects(file='weapon.json',
                                     howmany=self.how_many['оружие'],
                                     object_class=Weapon)
        for weapon in self.all_weapon:
            weapon.place(self.new_castle)
        
        # Читаем щиты из файла и разбрасываем по замку
        self.all_shields = self.readobjects(file='shields.json',
                                      howmany=self.how_many['щит'],
                                      object_class=Shield)
        for shield in self.all_shields:
            shield.place(self.new_castle)
        
        # Читаем доспехи из файла и разбрасываем по замку
        self.all_armor = self.readobjects(file='armor.json',
                                    howmany=self.how_many['доспех'],
                                    object_class=Armor)
        for armor in self.all_armor:
            armor.place(self.new_castle)
        
        # Читаем зелья из файла и разбрасываем по замку
        self.all_potions = self.readobjects(file='potions.json',
                                      howmany=self.how_many['зелье'],
                                      object_class=Potion)
        for potion in self.all_potions:
            potion.place(self.new_castle)
        
        # Создаем руны и разбрасываем по замку
        self.all_runes = [Rune(self) for _ in range(self.how_many['руна'])]
        for rune in self.all_runes:
            rune.place(self.new_castle)
            print(rune.poison)
        # Создаем книги и разбрасываем по замку
        
        self.all_books = self.readobjects(file='books.json',
                                    howmany=self.how_many['книга'],
                                    random=True,
                                    object_class=Book)
        for book in self.all_books:
            book.place(self.new_castle)
        self.new_castle.lock_doors()  # Создаем запертые комнаты
        new_map = Map(self)
        new_map.place(self.new_castle)  # Создаем и прячем карту
        matches = Matches(self)
        matches.place(self.new_castle)  # Создаем и прячем спички
        self.new_castle.plan[0].visited = '+'  # Делаем первую комнату посещенной
        new_key = Key(self)  # Создаем ключ
        self.player.pockets.append(new_key)  # Отдаем ключ игроку
        self.game_is_on = False  # Выключаем игру для того, чтобы игрок запустил ее в Телеграме

    
    def __del__ (self):
        print("="*40)
        print('Игра удалена')
        print("=" * 40)

    
    def readobjects(self, file=None, howmany=None, object_class=None, random=False, object_type=None):
        objects = []
        if file:
            with open(file, encoding='utf-8') as read_data:
                parsed_data = json.load(read_data)
            if not random:
                for i in parsed_data:
                    new_object = self.classes[i['class']](self)
                    for param in i:
                        vars(new_object)[param] = i[param]
                    new_object.on_create()
                    objects.append(new_object)
            else:
                for _ in range(howmany):
                    i = randomitem(parsed_data, False)
                    new_object = self.classes[i['class']](self)
                    for param in i:
                        vars(new_object)[param] = i[param]
                    new_object.on_create()
                    objects.append(new_object)
        if object_type:
            for obj in objects:
                if obj.type != object_type:
                    objects.remove(obj)
        if howmany:
            while len(objects) > howmany:
                spare_object = randomitem(objects, False)
                objects.remove(spare_object)
            if object_class:
                while len(objects) < howmany:
                    if object_type:
                        new_object = object_class(self, 0, weapon_type=object_type)
                    else:
                        new_object = object_class(self, 0)
                    objects.append(new_object)
        if len(objects)>0:
            return objects
        else:
            return False

    def action(self, command, message):
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
            rune_list = self.player.inpockets(Rune)
            if answer == 'отмена':
                self.state = 0
                return True
            elif answer.isdigit() and int(answer) - 1 < len(rune_list):
                if self.selected_item.enchant(rune_list[int(answer) - 1]):
                    tprint(self, f'{player.name} улучшает {self.selected_item.name1} новой руной.', 'direction')
                    player.pockets.remove(rune_list[int(answer) - 1])
                    self.state = 0
                    return True
                else:
                    tprint(self, f'Похоже, что {player.name} не может вставить руну в {self.selected_item.name1}.', 'direction')
                    self.state = 0
                    return False
            else:
                tprint(self, f'{player.name} не находит такую руну у себя в карманах.', 'direction')
            return True
        elif self.state == 4:
            can_use = self.selected_item
            if answer == 'отмена':
                self.state = 1
                tprint(self, f'{player.name} продолжает бой.', 'fight')
                return True
            elif answer.isdigit() and int(answer) - 1 < len(can_use):
                item = can_use[int(answer) - 1]
                if item.use(who_using=self.player, in_action=True):
                    self.selected_item.remove(item)
                    return True
                else:
                    tprint(self, f'Похоже, что {player.name} не может использовать {item.name1}.', 'fight')
                    self.state = 1
                    return False
            else:
                tprint(self, f'{player.name} не находит такую вкщь у себя в карманах.', 'fight')
            return True
        elif command in s_game_fight_commands and self.state == 1:
            enemy = self.new_castle.plan[self.player.current_position].monster()
            tprint(self, player.attack(enemy, message))
            if player.run:
                player.run = False
                player.look()
                self.state = 0
                return True
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
        tprint (self, f'{player.name} такого не умеет.', 'direction')