from functions import *
from class_castle import Castle
from class_hero import Hero
from class_weapon import Weapon
from class_protection import Shield, Armor
from class_items import Potion, Rune, Book, Matches, Map, Key, Spell
from class_monsters import Monster, Shapeshifter, Vampire, Berserk, Walker, Plant
from class_room import Furniture

classes = { 'монстр': Monster,
            'герой': Hero,
            'оружие': Weapon,
            'щит': Shield,
            'доспех': Armor,
            'притворщик': Shapeshifter,
            'мебель': Furniture,
            'вампир': Vampire,
            'берсерк': Berserk,
            'ходок': Walker,
            'растение': Plant,
            'ключ': Key,
            'карта': Map,
            'спички': Matches,
            'книга': Book,
            'зелье': Potion,
            'руна': Rune,
            'заклинание': Spell,
            }


class Game():
    def __init__(self, chat_id, bot, howMany=0, hero=None):
        self.state = 0
        # state - текущее состояние игры.
        # 0 - обычное состояние. Персонаж ходит, исследует и т.п.
        # 1 - происходит бой
        # 2 - персонаж что-то улучшает
        # 3 - персонаж поднимает уровень
        self.selectedItem = ''
        self.gameIsOn = False
        self.chat_id = chat_id
        self.bot = bot
        self.newCastle = Castle(self, 5, 5)  # Генерируем замок
        if howMany == 0:
            self.howMany = {'монстры': 10,
                            'оружие': 10,
                            'щит': 5,
                            'доспех': 5,
                            'зелье': 10,
                            'мебель': 10,
                            'книга': 5,
                            'руна': 10}  # Количество всяких штук, которые разбрасываются по замку
        else:
            self.howMany = howMany
        if not hero:
            self.player = Hero(self, 'Артур', 'Артура', 'male', 10, 2, 1, 25, '', '',
                                'бьет,калечит,терзает,протыкает')  # Создаем персонажа
        else:
            self.player = hero
        # Создаем мебель и разбрасываем по замку
        self.allFurniture = self.readobjects(file='furniture.json',
                                        howmany=self.howMany['мебель'],
                                        random=True)
        for furniture in self.allFurniture:
            furniture.place(castle=self.newCastle)
        # Читаем монстров из файла и разбрасываем по замку
        self.allMonsters = self.readobjects(file='monsters.json',
                                       howmany=self.howMany['монстры'])
        for monster in self.allMonsters:
            monster.place(self.newCastle)
        # Читаем оружие из файла и разбрасываем по замку
        self.allWeapon = self.readobjects(file='weapon.json',
                                     howmany=self.howMany['оружие'],
                                     object_class=Weapon)
        for weapon in self.allWeapon:
            weapon.place(self.newCastle)
        # Читаем щиты из файла и разбрасываем по замку
        self.allShields = self.readobjects(file='shields.json',
                                      howmany=self.howMany['щит'],
                                      object_class=Shield)
        for shield in self.allShields:
            shield.place(self.newCastle)
        # Читаем доспехи из файла и разбрасываем по замку
        self.allArmor = self.readobjects(file='armor.json',
                                    howmany=self.howMany['доспех'],
                                    object_class=Armor)
        for armor in self.allArmor:
            armor.place(self.newCastle)
        # Читаем зелья из файла и разбрасываем по замку
        self.allPotions = self.readobjects(file='potions.json',
                                      howmany=self.howMany['зелье'],
                                      object_class=Potion)
        for potion in self.allPotions:
            potion.place(self.newCastle)
        # Создаем руны и разбрасываем по замку
        self.allRunes = [Rune(self) for i in range(self.howMany['руна'])]
        for rune in self.allRunes:
            rune.place(self.newCastle)
        # Создаем книги и разбрасываем по замку
        self.allBooks = self.readobjects(file='books.json',
                                    howmany=self.howMany['книга'],
                                    random=True,
                                    object_class=Book)
        for book in self.allBooks:
            book.place(self.newCastle)
        self.newCastle.lockDoors()  # Создаем запертые комнаты
        map = Map(self)
        map.place(self.newCastle)  # Создаем и прячем карту
        matches = Matches(self)
        matches.place(self.newCastle)  # Создаем и прячем спички
        self.newCastle.plan[0].visited = '+'  # Делаем первую комнату посещенной
        newKey = Key(self)  # Создаем ключ
        self.player.pockets.append(newKey)  # Отдаем ключ игроку
        self.gameIsOn = False  # Выключаем игру для того, чтобы игрок запустил ее в Телеграме
        shield = self.readobjects(file='shields.json',
                                           howmany=1,
                                           object_class=Shield)
        self.allShields.append(shield)
        self.player.shield = shield[0]
        self.noWeapon = Weapon(self, empty=True)
        self.noShield = Shield(self, empty=True)
        self.noArmor = Armor(self, empty=True)

    def __del__ (self):
        print("="*40)
        print('Игра удалена')
        print("=" * 40)

    def readobjects(self, file=None, howmany=None, object_class=None, random=False):
        objects = []
        if file:
            with open(file, encoding='utf-8') as read_data:
                parsed_data = json.load(read_data)
            if not random:
                for i in parsed_data:
                    object = classes[i['class']](self)
                    for param in i:
                        vars(object)[param] = i[param]
                    object.on_create()
                    objects.append(object)
            else:
                for n in range(howmany):
                    i = randomitem(parsed_data, False)
                    object = classes[i['class']](self)
                    for param in i:
                        vars(object)[param] = i[param]
                    object.on_create()
                    objects.append(object)
        if howmany:
            while len(objects) > howmany:
                spareObject = randomitem(objects, False)
                objects.remove(spareObject)
            if object_class:
                while len(objects) < howmany:
                    newObject = object_class(self, 0)
                    objects.append(newObject)
        return objects
