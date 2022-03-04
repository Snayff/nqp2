from __future__ import annotations

import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict

__all__ = []


class EventHub:
    """
    Event hub to handle the interactions between events and subscribers
    """

    def __init__(self):
        self.events: List[Event] = []
        self.subscribers: Dict = {}

    def post(self, event: Event):
        """
        Log an event ready for notifying subscribers.
        """
        self.events.append(event)

    def subscribe(self, event_type: EventType, subscriber: Subscriber):
        """
        Register a subscriber with an EventType
        """
        self.subscribers.setdefault(event_type, []).append(subscriber)

    def unsubscribe(self, event_type: EventType, subscriber: Subscriber):
        """
        Remove a subscribers registration to an EventType
        """
        self.subscribers[event_type].remove(subscriber)

    def peek(self, event):
        """
        Check if an event exists in the queue.
        Return None if nothing is found so the result can be used as a bool.
        """
        found_events = []
        for e in self.events:
            if isinstance(e, event):  # type: ignore
                found_events.append(e)

        if found_events != []:
            return found_events

        return None

    def update(self):
        """
        Notify subscribers of their registered event.
        """

        # loop every event and notify every subscriber
        while self.events:
            event = self.events.pop(0)

            for sub in self.subscribers.get(event.event_type, []):
                sub.process_event(event)


event_hub = EventHub()


class Subscriber(ABC):
    """
    Class to set default behaviour for handlers listening for events
    """

    def __init__(self, name: str):
        self.name: str = name
        self.event_hub: EventHub = event_hub

    def subscribe(self, event_type: EventType):
        self.event_hub.subscribe(event_type, self)

    def unsubscribe(self, event_type: EventType):
        self.event_hub.unsubscribe(event_type, self)

    @abstractmethod
    def process_event(self, event: Event):
        """
        Process game events.
        """
        pass


class Event(ABC):
    """
    Events to cause top level actions to take place
    """

    def __init__(self, event_type: EventType):
        """
        Base class for events
        """
        self.event_type = event_type


###############
# event classes
################

class ExitMenuEvent(Event):
    def __init__(self, menu: UIElement):
        super().__init__(EventType.GAME)

        self.menu: UIElement = menu


class NewGameEvent(Event):
    def __init__(self):
        super().__init__(EventType.GAME)


class StartGameEvent(Event):
    def __init__(self, player_data: ActorData):
        super().__init__(EventType.GAME)

        self.player_data: ActorData = player_data


class LoadGameEvent(Event):
    def __init__(self):
        super().__init__(EventType.GAME)


class ExitGameEvent(Event):
    def __init__(self):
        super().__init__(EventType.GAME)