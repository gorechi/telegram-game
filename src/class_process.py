from enum import Enum

class Process:
    """Базовый класс для процессов в игре."""
    
    def __init__(self, game, owner):
        self.game = game
        self.owner = owner

    
    def start(self):
        return
    
    
    def terminate(self):
        return


class EnchantmentProcess(Process):
    """Процесс улучшения предмета."""

    class status_enum(Enum):
        """
        Статусы процесса улучшения предмета:
        - WAITING_FOR_ITEM: ожидание выбора предмета для улучшения
        - WAITING_FOR_RUNE: ожидание выбора руны для улучшения
        - START: процесс готов к выполнению
        """
        WAITING_FOR_ITEM = 0
        WAITING_FOR_RUNE = 1
        START = 2

    
    def __init__(self, game, owner, init_text=None):
        super().__init__(game, owner)
        self.init_text = init_text
        self.item = None
        self.rune = None
        self.items_list = self.get_items_list()
        

    def get_items_list(self) -> list:
        """
        Возвращает список предметов, доступных для наложения чар.

        Метод формирует список предметов владельца в следующем порядке:
        1. Если у владельца есть оружие (weapon), оно добавляется в список.
        2. Если у владельца есть щит (shield), он добавляется в список.
            Если щита нет, но есть снятый щит (removed_shield), добавляется снятый щит.
        3. Если у владельца есть броня (armor), она добавляется в список.
        4. Если у владельца есть рюкзак (backpack) и он не пуст, к списку добавляются все предметы из рюкзака, подходящие для наложения чар (метод get_items_to_enchant).

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
        return items_list