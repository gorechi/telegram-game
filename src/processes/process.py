from src.functions.functions import tprint

class Process():
    """Базовый класс процесса."""
         
    _termination_commands = [
        'отмена', 
        'выход', 
        'закончить'
        ]

    _termination_statuses = []
    """Статусы процесса, при достижении которых процесс завершается."""

    _message_generators = {}
    """Словарь соответствия статусов процесса и методов генерации сообщений."""

    
    def __init__(self, game, owner, init_text=None):
        self.game = game
        self.owner = owner
        self.init_text = init_text
        
    
    def terminate(self, termination_text:str | list):
        self.game.processes_controller.terminate_process(self)
        tprint(self.game, termination_text)
        return
    

    def set_status(self, new_status):
        """
        Устанавливает новый статус процесса.

        Аргументы:
            new_status (status_enum): Новый статус, который нужно установить.
        """
        self.status = new_status
    
    
    def check_termination(self, request_text):
        """
        Проверяет, содержит ли запрос команду для завершения процесса.

        Аргументы:
            request_text (str): Текст запроса, который нужно проверить.
        """
        return request_text in Process._termination_commands


    def set_owner_status(self) -> bool:
        """
        Проверяет состояние владельца процесса.
        Если владельцу слишком темно или он напуган, устанавливает
        соответствующий статус и возвращает False.

        Возвращает:
            bool: True, если владелец может продолжать процесс, иначе False.
        """
        if not self.owner.check_light():
            self.set_status(self.status_enum.TOO_DARK)
            return False
        if self.owner.check_fear():
            self.set_status(self.status_enum.FEAR)
            return False
        return True


    def send_message(self):
        """
        Отправляет пользователю сообщение, соответствующее текущему статусу процесса.
        Если текущий статус является завершающим, процесс завершается.
        """
        message = self.generate_message()
        if self.status in self._termination_statuses:
            self.terminate(message)
            return
        tprint(self.game, message)


    def generate_message(self) -> list[str]:
        """
        Генерирует текстовое сообщение для пользователя в зависимости от текущего статуса процесса.
        Возвращает:
            list[str]: Сообщение или список сообщений, соответствующих текущему этапу взаимодействия.
        """
        method_name = self._message_generators[self.status]
        return getattr(self, method_name)()
