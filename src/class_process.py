from enum import Enum
from src.functions.functions import tprint

class Process:
    """Базовый класс для процессов в игре."""
    
    termination_commands = [
        'отмена', 
        'выход', 
        'закончить'
        ]
    
    def __init__(self, game, owner):
        self.game = game
        self.owner = owner

    
    def check_termination(self, request_text):
        """
        Проверяет, содержит ли запрос команду для завершения процесса.

        Аргументы:
            request_text (str): Текст запроса, который нужно проверить.
        """
        return request_text in Process.termination_commands
    
    
    def terminate(self, termination_text:str | list):
        tprint(self.game, termination_text)
        return
    

    def set_status(self, new_status):
        """
        Устанавливает новый статус процесса наложения чар.

        Аргументы:
            new_status (status_enum): Новый статус, который нужно установить.
        """
        self.status = new_status


class EnchantmentProcess(Process):
    """Процесс улучшения предмета."""

    class status_enum(Enum):
        """
        Статусы процесса улучшения предмета:
        - WAITING_FOR_ITEM: ожидание выбора предмета для улучшения
        - WAITING_FOR_RUNE: ожидание выбора руны для улучшения
        - NO_AVAILABLE_ITEMS: нет доступных предметов для улучшения
        - NO_AVAILABLE_RUNES: нет доступных рун для улучшения
        - READY_TO_ENCHANT: готов к наложению чар
        - ENCHANTMENT_ERROR: ошибка при наложении чар
        - ENCHANTMENT_SUCCESS: успешное наложение чар
        """
        WAITING_FOR_ITEM = 0
        WAITING_FOR_RUNE = 1
        NO_AVAILABLE_ITEMS = 2
        NO_AVAILABLE_RUNES = 3
        READY_TO_ENCHANT = 4
        ENCHANTMENT_ERROR = 5
        ENCHANTMENT_SUCCESS = 6

    
    def __init__(self, game, owner, init_text=None):
        super().__init__(game, owner)
        self.status = EnchantmentProcess.status_enum.WAITING_FOR_ITEM
        self.init_text = init_text
        self.items_list = self.get_items_list()
        self.runes_list = self.get_runes_list()
        if self.status == EnchantmentProcess.status_enum.WAITING_FOR_ITEM and init_text:
            self.item = self.try_to_find_item(init_text)
        self.rune = None
        self.proceed()
        
    
    def get_items_list(self) -> list:
        """
        Возвращает список предметов, доступных для наложения чар.

        Метод формирует список предметов владельца в следующем порядке:
        1. Если у владельца есть оружие (weapon), оно добавляется в список.
        2. Если у владельца есть щит (shield), он добавляется в список.
            Если щита нет, но есть снятый щит (removed_shield), добавляется снятый щит.
        3. Если у владельца есть броня (armor), она добавляется в список.
        4. Если у владельца есть рюкзак (backpack) и он не пуст, к списку добавляются все предметы из рюкзака, подходящие для наложения чар (метод get_items_to_enchant).

        Если нет доступных предметов, устанавливается статус NO_AVAILABLE_ITEMS.

        Возвращаемое значение:
             list: Список предметов владельца, которые могут быть использованы для наложения чар.
        """
        items_list = []
        if not self.owner.weapon.empty:
            items_list.append(self.owner.weapon)
        if not self.owner.shield.empty:
            items_list.append(self.owner.shield)
        elif not self.owner.removed_shield.empty:
            items_list.append(self.owner.removed_shield)
        if not self.owner.armor.empty:
            items_list.append(self.owner.armor)
        if self.owner.check_backpack():
            items_list.extend(self.owner.backpack.get_items_to_enchant())
        if not items_list:
            self.set_status(EnchantmentProcess.status_enum.NO_AVAILABLE_ITEMS)
        return items_list
    
    
    def get_runes_list(self) -> list:
        """
        Возвращает список рун, доступных для наложения чар.

        Метод формирует список всех предметов класса 'Rune' в рюкзаке владельца, если рюкзак не пуст.

        Если нет доступных рун, устанавливается статус NO_AVAILABLE_RUNES.

        Возвращаемое значение:
             list: Список рун владельца, которые могут быть использованы для наложения чар.
        """
        runes_list = list()
        if self.owner.check_backpack():
            runes_list.extend(self.owner.backpack.get_items_by_class('Rune'))
        if not runes_list:
            self.set_status(EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES)
        return runes_list
    

    def try_to_find_item(self, request_text:str):
        """
        Пытается найти и вернуть предмет по заданному текстовому описанию.

        Аргументы:
            request_text (str): Текстовое описание предмета, который требуется найти. 
                Может быть названием типа предмета (например, 'оружие', 'щит', 'доспех', 'доспехи') 
                или числовым индексом в списке предметов.

        Возвращает:
            Объект предмета, если он найден по заданному описанию, иначе None.
        """
        found_item = None
        if hasattr(self.owner, 'weapon') and request_text == 'оружие' and not self.owner.weapon.empty:
            found_item = self.owner.weapon
        elif request_text == 'щит':
            if hasattr(self.owner, 'shield') and not self.owner.shield.empty:
                found_item = self.owner.shield
            elif hasattr(self.owner, 'removed_shield') and not self.owner.removed_shield.empty:
                found_item = self.owner.removed_shield
        elif request_text in ['доспех', 'доспехи'] and hasattr(self.owner, 'armor') and not self.owner.armor.empty:
            found_item = self.owner.armor
        elif request_text.isdigit() and 1 <= int(request_text) <= len(self.items_list):
            found_item = self.items_list[int(request_text)-1]
        else:
            for item in self.items_list:
                if item.check_name(request_text):
                    self.set_status(EnchantmentProcess.status_enum.WAITING_FOR_RUNE)
                    return item
        if found_item:
            self.set_status(EnchantmentProcess.status_enum.WAITING_FOR_RUNE)
            return found_item
        return None
    

    def try_to_find_rune(self, request_text:str):
        """
        Пытается найти и вернуть руну по заданному текстовому описанию.

        Аргументы:
            request_text (str): Текстовое описание руны, которую требуется найти. 
                Может быть названием руны 
                или числовым индексом в списке предметов.

        Возвращает:
            Объект руны, если он найден по заданному описанию, иначе None.
        """
        found_rune = None
        if request_text.isdigit() and 1 <= int(request_text) <= len(self.runes_list):
            found_rune = self.runes_list[int(request_text)-1]
        else:
            for rune in self.runes_list:
                if rune.check_name(request_text):
                    found_rune = rune
        if found_rune:
            self.set_status(EnchantmentProcess.status_enum.READY_TO_ENCHANT)
            return found_rune
        return None
    
    
    def proceed(self, request_text:str=None):
        
        if self.check_termination(request_text):
            self.terminate(f"{self.owner.name} {self.owner.g('передумал', 'передумала')} что-то улучшать. Есть дела поважнее.")
            return
        if self.status == EnchantmentProcess.status_enum.WAITING_FOR_ITEM and request_text:
            self.item = self.try_to_find_item(request_text)
        elif self.status == EnchantmentProcess.status_enum.WAITING_FOR_RUNE and request_text:
            self.rune = self.try_to_find_rune(request_text)
        if self.status == EnchantmentProcess.status_enum.READY_TO_ENCHANT:
            self.enchant_item()
        message = self.generate_message()
        if self.status in [EnchantmentProcess.status_enum.NO_AVAILABLE_ITEMS, EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES]:
            self.terminate(message)
            return
        tprint(self.game, message)


    def enchant_item(self):
        """
        Пытается наложить выбранную руну на выбранный предмет.
            self.set_status(EnchantmentProcess.status_enum.ENCHANTMENT_ERROR)
            return False
            bool: True, если руна успешно наложена на предмет, иначе False. 
                  В случае неудачи устанавливает статус ENCHANTMENT_ERROR.
        """
        rune_is_placed = self.item.enchant(self.rune)
        if not rune_is_placed:
            self.set_status(EnchantmentProcess.status_enum.ENCHANTMENT_ERROR)
            return False
        self.set_status(EnchantmentProcess.status_enum.ENCHANTMENT_SUCCESS)
        return True
    
    
    def generate_message(self) -> list[str]:
        """
        Генерирует текстовое сообщение для пользователя в зависимости от текущего статуса процесса зачарования.
        Возвращает:
            list[str]: Сообщение или список сообщений, соответствующих текущему этапу взаимодействия.
        """

        states = {
            EnchantmentProcess.status_enum.WAITING_FOR_ITEM: self.generate_item_message,
            EnchantmentProcess.status_enum.WAITING_FOR_RUNE: self.generate_rune_message,
            EnchantmentProcess.status_enum.NO_AVAILABLE_ITEMS: self.generate_no_items_message,
            EnchantmentProcess.status_enum.NO_AVAILABLE_RUNES: self.generate_no_runes_message,
            EnchantmentProcess.status_enum.ENCHANTMENT_ERROR: self.generate_error_message,
            EnchantmentProcess.status_enum.ENCHANTMENT_SUCCESS: self.generate_success_message
            }
        return states[self.status]()
    
    
    def generate_item_message(self) -> list[str]:
        message = list()
        message.append(f"{self.owner.name} может улучшить такие вещи:")
        for index, item in enumerate(self.items_list):
            description = f'{str(index + 1)}: {item.show()}'
            if type(item).__name__ == 'Weapon' and hasattr(self.owner, 'mastery'):
                mastery = self.owner.mastery[item.type]['level']
                if mastery > 0:
                    description += f', мастерство - {mastery}'
            message.append(description)
        message.append("Нужно выбрать вещь по номеру или крикнуть название типа предмета (например, 'оружие', 'щит', 'доспехи').")
        return message
    

    def generate_rune_message(self) -> list[str]:
        message = list()
        message.append(f"{self.owner.name} {self.owner.g('выбрал', 'выбрала')} для зачарования {self.item.show()}")
        message.append(f"Теперь {self.owner.g('ему', 'ей')} нужно выбрать руну для наложения на этот предмет:")
        for index, rune in enumerate(self.runes_list):
            message.append(f"{str(index + 1)}: {rune.show()}")
        message.append("Чтобы выбрать руну достаточно выкрикнуть ее номер.")
        return message
    

    def generate_error_message(self) -> list[str]:
        message = list()
        message.append(f"{self.owner.name} {self.owner.g('сунул', 'сунула')} что-то не то куда-то не туда и все сломалось. Может быть лучше заняться чем-то другим?")
        return message
    

    def generate_success_message(self) -> list[str]:
        message = list()
        message.append(f"{self.owner.name} успешно {self.owner.g('наложил', 'наложила')} {self.rune:accus} на {self.item:accus}")
        message.append("Теперь можно заняться чем-то другим.")
        return message
    

    def generate_no_items_message(self) -> list[str]:
        message = list()
        message.append(f"{self.owner.name} {self.owner.g('не нашел', 'не нашла')} у себя никаких штук, которые можно улучшить.")
        return message
    
    
    def generate_no_runes_message(self) -> list[str]:
        message = list()
        message.append(f"{self.owner.name} совсем {self.owner.g('забыл', 'забыла')}, что у {self.owner.g('него', 'нее')} нет никаких рун, так что и улучшать ничего нельзя.")
        return message
