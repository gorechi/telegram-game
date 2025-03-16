from dataclasses import dataclass
from collections import deque

class EventsController():
    
    @dataclass
    class Event():
        event_subject: object
        subject_method_name: str
        counter: int = 0
        parameters: dict = None
        event_object: object = None
    
    def __init__(self, game):
        self.game = game
        self.queue = deque()
        self.pending_events = list()


    def check_pending_events(self, counter:int) -> None:
        for event in self.pending_events:
            event.counter -= counter
            if event.counter <= 0:
                self.queue.append(event)
                self.pending_events.remove(event)
    

    def create_event(self, 
                     event_subject: object,
                     method_name: str,
                     event_object: object = None,
                     counter: int = 0,
                     parameters: dict = None
                     ) -> None:
        new_event = EventsController.Event(
            event_subject=event_subject,
            event_object=event_object,
            subject_method_name=method_name,
            counter=counter,
            parameters=parameters
        )
        if counter > 0:
            self.pending_events.append(new_event)
        else:
            self.queue.append(new_event)

    
    def execute_all_events(self, counter:int) -> None:
        self.check_pending_events(counter)
        while self.queue:
            event = self.queue.popleft()
            self.excecute_event(event)

    
    def execute_event(self, event) -> None:
        method = getattr(event.subject, event.subject_method_name, None)
        if method and callable(method):
            method(event.object)

    
    def delete_pending_events_by_subject(self, subject:object) -> None:
        new_list = [event for event in self.pending_events if event.subject is not subject]
        self.pending_events = new_list