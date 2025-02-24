from src.functions.functions import randomitem, roll

class Trap:
    """
    Класс, представляющий ловушку.

    Атрибуты:
        game (Game): Экземпляр игры, связанный с ловушкой.
        activated (bool): Указывает, активирована ли ловушка.

    Методы:
        __init__(game): Инициализирует ловушку с данным экземпляром игры.
        deactivate() -> bool: Обезвреживает ловушку и возвращает True.
    """
    
    types = [
        'intel',
        'stren',
        'dex',
        'armor',
        #'weapon',
        #'backpack'
    ]
    
    detection_texts = [
        'Сбоку отчетливо виден какой-то странный механизм.',
        'Тоненький волосок прикреплен к крышке.',
        'Изнутри слышно какое-то странное пощелкивание.',
        'В щели между крышкой и корпусом видно натянутую нитку.',
        'Кто-то явно что-то делал с крышкой - щель с одной стороны шире, чем с другой.'
    ]
    
    
    def __init__(self, game, where=None, limit=0):
        self.game = game
        self.activated = False
        self.seen = False
        self.triggered = False
        self.difficulty = self.set_difficulty(limit)
        self.detection_text = None
        self.where = where
        self.actions = {
            'intel': self.damage_intel,
            'stren': self.damage_stren,
            'dex': self.damage_dex,
            'armor': self.damage_armor,
            #'weapon': self.damage_weapon,
            #'backpack': self.damage_backpack
        }
    
    
    def get_detection_text(self) -> str:
        if self.detection_text:
            return self.detection_text
        texts = Trap.detection_texts
        text = randomitem(texts)
        self.detection_text = text
        return text     
    
    
    def set_difficulty(self, limit:int):
        self.difficulty = roll([limit])
        

    def get_disarm_difficulty(self) -> int:
        return self.difficulty * 2
    
    
    def deactivate(self) -> bool:
        if not self.activated:
            return False
        self.activated = False
        return True
    
    
    def activate(self) -> bool:
        if self.activated:
            return False
        self.activated = True
        return True
      
    
    def trigger(self, target) -> list[str]:
        """
        Активирует ловушку и применяет её эффекты к цели.

        Этот метод копирует список типов ловушек, выбирает случайный тип и применяет соответствующее действие к цели.
        Если у ловушки нет метода для выбранного типа, возбуждается исключение.
        После активации ловушка деактивируется, становится видимой и помечается как сработавшая.

        Args:
            target: Цель, к которой применяется эффект ловушки.

        Returns:
            Список строк с сообщениями о последствиях активации ловушки.
        """
        types = Trap.types.copy()
        message = ['От неловкого прикосновения в ловушка начинает противно щелкать, а потом взрывается.']
        while True:
            if not types:
                message.append(f'{target.name} настолько {target.g("некчемен", "некчемна")},' 
                               f' что ловушка не может причинить еще какой-то дополнительный урон.')
                return message
            action_type = randomitem(types)
            types.remove(action_type)
            action = self.actions.get(action_type, False)
            if not action:
                raise Exception(f'У ловушки нет метода для типа {action_type}')
            action_text = action(target)
            if action_text:
                message.append(action_text)
                self.deactivate()
                self.seen = True
                self.triggered = True
                return message
    
    
    def disarm(self) -> list[str]:
        self.deactivate()
        self.seen = True
        self.triggered = False
        return ['Ловушка тихонько щелкает и больше не издает ни звука. Похоже, она больше не опасна.']
    
    
    def damage_intel(self, target) -> str:
        return target.intel_wound()
    
    
    def damage_stren(self, target) -> str:
        return target.stren_wound()
      
    
    def damage_dex(self, target) -> str:
        return target.dex_wound()
        

    def damage_armor(self, target) -> bool|str:
        if target.armor.empty:
            return False
        return True


"""     def damage_weapon(self, target) -> bool|str:
        if target.weapon.empty:
            return False
        return True
 """

"""     def damage_backpack(self, target) -> bool|str:
        if target.backpack.empty:
            return False
        return True
 """        