from src.functions.functions import randomitem, tprint, roll

class Book:
    
    _names = {
        "nom": "книга",
        "accus": "книгу",
        "gen": "книги",
        "dat": "книге",
        "prep": "книге",
        "inst": "книгой"
      }
    
    _descriptions = (
        {
            "nom": "Старая",
            "accus": "Старую",
            "gen": "Старой",
            "dat": "Старой",
            "prep": "Старой",
            "inst": "Старой"
          },
          {
            "nom": "Древняя",
            "accus": "Древнюю",
            "gen": "Древней",
            "dat": "Древней",
            "prep": "Древней",
            "inst": "Древней"
          },
          {
            "nom": "Пыльная",
            "accus": "Пыльную",
            "gen": "Пыльной",
            "dat": "Пыльной",
            "prep": "Пыльной",
            "inst": "Пыльной"
          },
          {
            "nom": "Зачитанная",
            "accus": "Зачитанную",
            "gen": "Зачитанной",
            "dat": "Зачитанной",
            "prep": "Зачитанной",
            "inst": "Зачитанной"
          },
          {
            "nom": "Новая",
            "accus": "Новую",
            "gen": "Новой",
            "dat": "Новой",
            "prep": "Новой",
            "inst": "Новой"
          },
          {
            "nom": "Потрепанная",
            "accus": "Потрепанную",
            "gen": "Потрепанной",
            "dat": "Потрепанной",
            "prep": "Потрепанной",
            "inst": "Потрепанной"
          },
          {
            "nom": "Красивая",
            "accus": "Красивую",
            "gen": "Красивой",
            "dat": "Красивой",
            "prep": "Красивой",
            "inst": "Красивой"
          },
          {
            "nom": "Большая",
            "accus": "Большую",
            "gen": "Большой",
            "dat": "Большой",
            "prep": "Большой",
            "inst": "Большой"
          }
    )
    
    _base_price = 7
    
    _base_price_die = [8]
    
    @classmethod
    def random_book(cls, game) -> 'Book':
        book_class = randomitem(cls.__subclasses__())
        new_book = book_class(game)
        return new_book
        
    
    def __init__(self, game):
        self.game = game
        self.empty = False
        self.create_description()
        self.name = self.lexemes['nom']
        self.text = randomitem(self.__class__._texts)
        self.can_use_in_fight = False
        self.base_price = self.define_base_price()


    def __format__(self, format:str) -> str:
        return self.lexemes.get(format, '')

    
    def __str__(self):
        return self.name
    
    
    def check_name(self, message:str) -> bool:
        names_list = self.get_names_list(['nom', "accus"])
        return message.lower() in names_list
    
    
    def get_names_list(self, cases:list=None) -> list:
        names_list = ['книга', 'книгу', 'книжка', 'книжку']
        for case in cases:
            names_list.append(self.lexemes.get(case, '').lower())
        return names_list
            
    
    def define_base_price(self) -> int:
        return self.__class__._base_price + roll(self.__class__._base_price_die)
               
   
    def create_description(self):
        description_dict = randomitem(Book._descriptions)
        name_dict = Book._names
        self.lexemes = {}
        for lexeme in name_dict:
            self.lexemes[lexeme] =f'{description_dict[lexeme]} {name_dict[lexeme]} {self.__class__._decoration}'
        return True
        
    
    def place(self, floor, room=None):
        if not room:
            room = floor.get_random_room_with_furniture()
        furniture = randomitem(room.furniture)
        furniture.put(self)
        return True
    
    
    def show(self):
        return self.lexemes['nom']
    
    
    def use(self, who, in_action:bool=False) -> list[str]:
        message = [self.text]
        message.append(self.increase_mastery(who))
        message.append(f'{who.g("Он", "Она")} решает больше не носить книгу с собой и оставляет ее в незаметном месте.')
        self.increase_mastery(who)
        return message

    
    def take(self, who):
        if not who.backpack.no_backpack:
            who.backpack.append(self)
            tprint(self.game, f'{who.name} забирает {self:accus} себе.')
            return True
        return False
    

class ThrustingWeaponBook(Book):
    
    _texts = (
        "Книга повествует о временах мастеров-фехтовальщиков. Тогда величайшим достижением считалось заколоть соперника в честном поединке на шпагах.",
        "В книге во всех красках описывается история двух друзей-авантюристов, которые берутся за любое, даже самое опасное дело. Попав в беду они всегда чудом избегают гибели благодаря их умениям в бою на шпагах.",
        "Это история о молодой девушке, отец которой считает, что она добьется всего сама, если будет обладать характером и умением фехтовать. Уроки отца девушки описаны подробно и основательно, что позволяет читателю почерпнуть много нового."
    )
    
    _decoration = "о мушкетерах"
    
    _base_price = 7
    
    _base_price_die = [8]

    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.weapon_mastery['колющее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать колющее оружие.'


class CuttingWeaponBook(Book):
    
    _texts = (
        "Книга рассказывает о злобных пиратах под предводительством знаменитого капитана Рыжая (с проседью) Борода, который был великим мастером сабли.",
        "Повествование в книге ведется от лица боцмана пиратской шхуны, бороздившей южные моря. Команда корабля не гнушалась любой добычи и нападала на любые проходящие мимо суда. Не сгинуть в морской пучине главному герою помогает его мастерское владение саблей.",
        "Автор книги провел несколько лет в пиратском логове в качестве врача. Наблюдая за жизнью пиратов, за их тренировками, он составил подробное описание боевого стиля пиратских воинов.",
    )
    
    _decoration = "о пиратах"
    
    _base_price = 7
    
    _base_price_die = [8]

    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.weapon_mastery['рубящее']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать рубящее оружие.'
    
    
class BluntgWeaponBook(Book):
    
    _texts = (
        "В книге описывается жизнь вождя викингов Олафа, который ходил в походы на соседние земли и прославился тем, что дрался только своей любимой дубиной.",
        "Книга представляет собой вольное изложение легенд северных народов с особым упором на ратные подвиги героев и их умения в применении ударного оружия.",
        "История кузница в норвежской деревне начинается мирно и размеренно, но резко превращается в абсолютный кошмар после эпизода убийства его семьи воинами соседнего племени. Бросив кузницу и вооружившись лишь своим молотом герой отправляется мстить.",
    )
    
    _decoration = "о викингах"
    
    _base_price = 7
    
    _base_price_die = [8]

    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.weapon_mastery['ударное']['level'] += 1
        return f'{who.name} теперь немного лучше знает, как использовать ударное оружие.'


class TrapsBook(Book):
    
    _texts = (
        "Книга рассказывает про команду взломщиков сейфов, которая сталкивается с самым сложным вызовом в своей карьере, пытаясь проникнуть в неприступное хранилище, охраняемое страшными ловушками.",
        "Книга описывает мир, где заклинания могут открывать любые двери. Группа храбрых плутов бросает вызов забытому замку, полному магических загадок и смертельных ловушек, чтобы обнаружить сокровище, способное изменить судьбы.",
        "В книге описывается как в зачарованном лесу, где каждое дерево и камень хранит свои тайны, молодой вор предпринимает опасное путешествие к сердцу древнего лабиринта, полного мистических ловушек и неизведанных опасностей, в поисках затерянного сокровища великих магов."
    )
    
    _decoration = "о взломщиках"
    
    _base_price = 7
    
    _base_price_die = [8]

    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.trap_mastery += 1
        return f'{who.name} теперь немного лучше разбирается в том, как обезвреживать ловушки.'
    
    
class WisdomBook(Book):
    
    _texts = (
        "Книга представляет собой энциклопедию. Автор - монах из скрытого от посторонних глаз монастыря - кропотливо и во всех подробностях описывает вещи и явления из самых разных сфер жизни.",
        "Книгу написал дипломат, служивший при дворе заморских королей. Книга полна изречений мудрых правителей, их мыслей по поводу всего на свете.",
        "Книга описывает жизненный путь великого ученого мужа, закончившего свои дни в обсерватории в Северных горах. За свою долгую жизнь этот умнейший человек интересовался разнообразными вопросами и достиг глубокого понимания природы вещей."
    )
    
    _decoration = "об ученых"
    
    _base_price = 20
    
    _base_price_die = [15]

    
    def __init__(self, game):
        super().__init__(game)
    
            
    def increase_mastery(self, who) -> str:
        who.intel += 1
        return f'{who.name} чувствует, что {who.g("стал", "стала")} немного умнее'