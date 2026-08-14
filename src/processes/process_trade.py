from enum import Enum
from src.functions.functions import split_actions
from src.processes.process import Process

class TradeProcess(Process):
    """Процесс торговли."""
   
    class status_enum(Enum):
        """
        Статусы процесса торговли:
        - WAITING_FOR_ACTION: ожидание выбора покупать или продавать будет герой
        - TOO_DARK: слишком темно чтобы торговать
        - FEAR: герой напуган
        """
        WAITING_FOR_ACTION = 0
        TOO_DARK = 1
        FEAR = 2

    _termination_statuses = [
            status_enum.TOO_DARK,
            status_enum.FEAR,
            ]

    _message_generators = {
            status_enum.WAITING_FOR_ACTION: 'generate_actions_message',
            status_enum.TOO_DARK: 'generate_too_dark_message',
            status_enum.FEAR: 'generate_fear_message',
            }
    
    def __init__(self, game, owner, trader, init_text=None):
        super().__init__(game, owner, init_text)
        self.trader = trader
        self.status = TradeProcess.status_enum.WAITING_FOR_ACTION
        self.set_owner_status()
        self.proceed()


    def proceed(self, request_text:str=None):
        
        if self.check_termination(request_text):
            self.terminate(f"{self.owner.name} {self.owner.g('передумал', 'передумала')} торговать. Есть дела поважнее.")
            return
        if self.status == TradeProcess.status_enum.WAITING_FOR_ACTION and request_text:
            action, target = split_actions(request_text)
            if action in ['купить', 'покупать', '1']:
                self.start_buy(target)
                return
            if action in ['продать', 'продавать', '2']:
                self.start_sell(target)
                return
        self.send_message()


    def start_buy(self, request_text:str=None) -> bool:
        self.game.processes_controller.create_process(
            owner = self.owner,
            type = 'buy',
            request_text = request_text,
            trader = self.trader,
        )
        return True


    def start_sell(self, request_text:str=None) -> bool:
        self.game.processes_controller.create_process(
            owner = self.owner,
            type = 'sell',
            request_text = request_text,
            trader = self.trader,
        )
        return True

    
    def generate_too_dark_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} думает, что торговать в такой темноте - плохая идея.')
        return message
    

    def generate_fear_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} не думает ни о чем кроме борьбы за жизнь. {self.owner.g('Ему', 'Ей')} сейчас не до торговли')
        return message
    

    def generate_actions_message(self) -> list[str]:
        message = list()
        message.append(f'У этого торговца {self.owner.name} может делать все то же, что и любых других торговцев:')
        message.append('(1) КУПИТЬ что-нибудь полезное')
        message.append('(2) ПРОДАТЬ что-нибудь бесполезное')
        message.append('Или УЙТИ подобру-поздорову')
        return message


class BuyProcess(Process):
    """Процесс покупки предмета у торговца."""

    class status_enum(Enum):
        """
        Статусы процесса покупки:
        - WAITING_FOR_ITEM: ожидание выбора товара для покупки
        - NO_AVAILABLE_ITEMS: у торговца нет товаров для продажи
        - TOO_DARK: слишком темно чтобы торговать
        - FEAR: герой напуган
        """
        WAITING_FOR_ITEM = 0
        NO_AVAILABLE_ITEMS = 1
        TOO_DARK = 2
        FEAR = 3

    _termination_statuses = [
            status_enum.NO_AVAILABLE_ITEMS,
            status_enum.TOO_DARK,
            status_enum.FEAR,
            ]

    _message_generators = {
            status_enum.WAITING_FOR_ITEM: 'generate_item_message',
            status_enum.NO_AVAILABLE_ITEMS: 'generate_no_items_message',
            status_enum.TOO_DARK: 'generate_too_dark_message',
            status_enum.FEAR: 'generate_fear_message',
            }

    def __init__(self, game, owner, trader, init_text=None):
        super().__init__(game, owner, init_text)
        self.trader = trader
        self.status = BuyProcess.status_enum.WAITING_FOR_ITEM
        self.items_list = self.get_items_list()
        self.set_owner_status()
        if init_text:
            self.buy_item(init_text)
        self.proceed()


    def get_items_list(self) -> list:
        """
        Возвращает список товаров, которые торговец может продать герою.
        Если торговать нечем, устанавливается статус NO_AVAILABLE_ITEMS.

        Возвращаемое значение:
            list: Список товаров торговца (ItemInShop).
        """
        items_list = list(self.trader.shop)
        if not items_list:
            self.set_status(BuyProcess.status_enum.NO_AVAILABLE_ITEMS)
        return items_list


    def proceed(self, request_text:str=None):
        
        if self.check_termination(request_text):
            self.terminate(f"{self.owner.name} {self.owner.g('передумал', 'передумала')} покупать. Есть дела поважнее.")
            return
        if self.status == BuyProcess.status_enum.WAITING_FOR_ITEM and request_text:
            self.buy_item(request_text)
        self.send_message()


    def buy_item(self, request_text:str) -> bool:
        """
        Пытается купить у торговца товар по текстовому описанию или номеру.
        После попытки покупки (удачной или нет) герой остаётся в процессе
        и видит обновлённый список товаров.

        Аргументы:
            request_text (str): Номер или название товара.

        Возвращает:
            bool: True, если покупка удалась, иначе False.
        """
        result = self.trader.sell(request_text, self.owner)
        self.set_status(BuyProcess.status_enum.WAITING_FOR_ITEM)
        self.items_list = self.get_items_list()
        return result


    def generate_item_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} подходит к прилавку {self.trader:nom} и рассматривает товары.')
        message.extend(self.trader.generate_selling_text())
        message.append('Нужно назвать номер или название товара, чтобы купить его.')
        return message


    def generate_no_items_message(self) -> list[str]:
        message = list()
        message.append(f'{self.trader:nom} с сожалением разводит руками: на прилавке пусто и продавать нечего.')
        return message


    def generate_too_dark_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} думает, что покупать в такой темноте - плохая идея.')
        return message


    def generate_fear_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} не думает ни о чем кроме борьбы за жизнь. {self.owner.g('Ему', 'Ей')} сейчас не до покупок.')
        return message


class SellProcess(Process):
    """Процесс продажи предмета торговцу."""

    class status_enum(Enum):
        """
        Статусы процесса продажи:
        - WAITING_FOR_ITEM: ожидание выбора предмета для продажи
        - NO_AVAILABLE_ITEMS: торговцу нечего купить у героя
        - TOO_DARK: слишком темно чтобы торговать
        - FEAR: герой напуган
        """
        WAITING_FOR_ITEM = 0
        NO_AVAILABLE_ITEMS = 1
        TOO_DARK = 2
        FEAR = 3

    _termination_statuses = [
            status_enum.NO_AVAILABLE_ITEMS,
            status_enum.TOO_DARK,
            status_enum.FEAR,
            ]

    _message_generators = {
            status_enum.WAITING_FOR_ITEM: 'generate_item_message',
            status_enum.NO_AVAILABLE_ITEMS: 'generate_no_items_message',
            status_enum.TOO_DARK: 'generate_too_dark_message',
            status_enum.FEAR: 'generate_fear_message',
            }

    def __init__(self, game, owner, trader, init_text=None):
        super().__init__(game, owner, init_text)
        self.trader = trader
        self.status = SellProcess.status_enum.WAITING_FOR_ITEM
        self.items_list = self.get_items_list()
        self.set_owner_status()
        if init_text:
            self.sell_item(init_text)
        self.proceed()


    def get_items_list(self) -> list:
        """
        Оценивает предметы в рюкзаке героя и возвращает список того,
        что торговец готов купить.
        Если покупать нечего, устанавливается статус NO_AVAILABLE_ITEMS.

        Возвращаемое значение:
            list: Список товаров (ItemInShop).
        """
        self.trader.evaluate_items(self.owner.backpack)
        items_list = list(self.trader.goods_to_buy)
        if not items_list:
            self.set_status(SellProcess.status_enum.NO_AVAILABLE_ITEMS)
        return items_list


    def proceed(self, request_text:str=None):
        
        if self.check_termination(request_text):
            self.terminate(f"{self.owner.name} {self.owner.g('передумал', 'передумала')} продавать. Есть дела поважнее.")
            return
        if self.status == SellProcess.status_enum.WAITING_FOR_ITEM and request_text:
            self.sell_item(request_text)
        self.send_message()


    def sell_item(self, request_text:str) -> bool:
        """
        Пытается продать торговцу предмет по текстовому описанию или номеру.
        После попытки продажи (удачной или нет) герой остаётся в процессе
        и видит обновлённое предложение торговца.

        Аргументы:
            request_text (str): Номер или название предмета.

        Возвращает:
            bool: True, если продажа удалась, иначе False.
        """
        result = self.trader.buy(request_text, self.owner)
        self.set_status(SellProcess.status_enum.WAITING_FOR_ITEM)
        self.items_list = self.get_items_list()
        return result


    def generate_item_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} открывает рюкзак и предлагает {self.trader:dat} свои вещи.')
        message.extend(self.trader.generate_buying_text())
        message.append('Нужно назвать номер или название предмета, чтобы продать его.')
        return message


    def generate_no_items_message(self) -> list[str]:
        message = list()
        message.append(f'{self.trader:nom} смотрит на содержимое рюкзака {self.owner:gen} и разводит руками: брать нечего.')
        return message


    def generate_too_dark_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} думает, что продавать в такой темноте - плохая идея.')
        return message


    def generate_fear_message(self) -> list[str]:
        message = list()
        message.append(f'{self.owner.name} не думает ни о чем кроме борьбы за жизнь. {self.owner.g('Ему', 'Ей')} сейчас не до продаж.')
        return message
