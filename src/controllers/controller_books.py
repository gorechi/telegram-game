from dataclasses import dataclass

from src.class_book import Book, ThrustingWeaponBook, CuttingWeaponBook, BluntgWeaponBook, TrapsBook, WisdomBook, ShieldsBook, ArmorBook
from src.class_controller import Controller
from src.functions.functions import randomitem

class BooksController(Controller):
    """Класс для управления книгами."""

    @dataclass
    class Template():
        class_name: str
        decoration: str
        base_price: int
        price_dice: dict
        texts: list
        can_use_in_fight: bool
        examine_text: str      
    
    
    _classes = {
        "Book": Book,
        "ThrustingWeaponBook": ThrustingWeaponBook,
        "CuttingWeaponBook": CuttingWeaponBook,
        "BluntgWeaponBook": BluntgWeaponBook,
        "TrapsBook": TrapsBook,
        "WisdomBook": WisdomBook,
        "ShieldsBook": ShieldsBook,
        "ArmorBook": ArmorBook
    }
    
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
    
    def __init__(self, game):
        self.game = game
        self.how_many = 0
        self.templates = self.load_templates('json/books.json')
        self.all_objects = []
    
    
    def additional_actions(self, object) -> bool:
        """
        Выполняет дополнительные действия с объектом после его создания.
        """
        self.decorate(object)
        self.define_price(object)
        return True
    
    
    def decorate(self, book):
        """
        Украшает книгу, создавая её имя и текст.
        """
        description_dict = randomitem(BooksController._descriptions)
        name_dict = BooksController._names
        book.lexemes = {}
        for lexeme in name_dict:
            book.lexemes[lexeme] = f'{description_dict[lexeme]} {name_dict[lexeme]} {book.decoration}'
        book.name = book.lexemes['nom']
        book.text = randomitem(book.texts)
        return True
    
    
    def define_price(self, book):
        """
        Определяет цену книги, используя базовую цену и бросок кубика.
        """
        book.base_price += book.price_dice.roll()