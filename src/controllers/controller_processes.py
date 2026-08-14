from src.processes.process_enchantment import EnchantmentProcess
from src.processes.process_trade import TradeProcess, BuyProcess, SellProcess

class ProcessesController():
    """
    Класс для управления процессами.
    """    

    process_types = {
        'enchantment': EnchantmentProcess,
        'trade': TradeProcess,
        'buy': BuyProcess,
        'sell': SellProcess
    }
    
    def __init__(self, game):
        self.game = game
        self.queue = list()

    
    def create_process(
            self,
            owner,
            type: str,
            request_text: str = None,
            **kwargs
            ) -> None:
        process_class = ProcessesController.process_types[type]
        new_process = process_class.__new__(process_class)
        self.register_process(new_process)
        try:
            new_process.__init__(
                game = self.game,
                owner = owner,
                init_text = request_text,
                **kwargs
            )
        except Exception:
            self.terminate_process(new_process)
            raise
    

    def register_process(self, process):
        self.queue.append(process)

    
    def get_current_process(self):
        if self.queue:
            return self.queue[-1]
        return None
    

    def terminate_current_process(self) -> bool:
        if self.queue:
            self.queue.pop()
            return True
        return False


    def terminate_process(self, process) -> bool:
        if process in self.queue:
            self.queue.remove(process)
            return True
        return False