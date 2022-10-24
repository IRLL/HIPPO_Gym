import logging
from enum import Enum

from typing import TYPE_CHECKING, Any, Dict, List, Union


if TYPE_CHECKING:
    from hippogym.message_handler import MessageHandler
    from multiprocessing import Queue

LOGGER = logging.getLogger(__name__)


class EventTopic(Enum):
    UI = "ui"
    KEYBOARD = "ui.KeyboardEvent"
    MOUSE = "ui.MouseEvent"
    BUTTON = "ui.ButtonEvent"
    WINDOW = "ui.WindowEvent"
    SLIDER = "ui.SliderEvent"
    TEXT = "ui.TextEvent"
    GRID = "ui.GridEvent"
    USER = "user"


_key_to_topic = {
    "KeyboardEvent": EventTopic.KEYBOARD,
    "MouseEvent": EventTopic.MOUSE,
    "ButtonEvent": EventTopic.BUTTON,
    "WindowEvent": EventTopic.WINDOW,
    "SliderEvent": EventTopic.SLIDER,
    "TextEvent": EventTopic.TEXT,
    "GridEvent": EventTopic.GRID,
}


class EventHandler:
    def __init__(self, in_q: "Queue", out_q: "Queue") -> None:
        self.in_q = in_q
        self.out_q = out_q
        self.message_handlers: List["MessageHandler"] = []

    def register(self, message_handler: "MessageHandler"):
        """Register the given MessageHandler to dispatch events into it.

        Args:
            message_handler (MessageHandler): MessageHandler to register.
        """
        self.message_handlers.append(message_handler)

    def send(self, message: Any) -> None:
        """Send message into the output Queue.

        Args:
            message (Any): Message sent into the output Queue.

        """
        self.out_q.put_nowait(message)

    def recv(self) -> None:
        """Recieve and emit all events cached events in the input queue."""
        while not self.in_q.empty():
            message = self.in_q.get()
            self.emit(message)

    def trigger_events(self):
        """Trigger cached events in the input queue."""
        self.recv()

    def dispatch(self, topic: EventTopic, event_type: str, content: Any):
        """Dispatch the given event to the given topic to all registered message handlers.

        Args:
            topic (EventTopic): The topic on which to send the event.
            event_type (str): The type of event.
            content (Any): Additional content data of the event.
        """
        for message_handler in self.message_handlers:
            message_handler.emitter.emit(topic, event_type, content)

    def emit(self, message: Dict[str, Any]):
        """Pass the given to all message handlers with correct topic."""
        for key, event in message.items():
            events = self._find_events(key, event)
            for topic, event_type, content in events:
                self.dispatch(topic, event_type, content)

    @staticmethod
    def _find_events(key: str, event: Any):
        events = []
        if key in _key_to_topic:
            topic = _key_to_topic[key]
            if isinstance(event, dict):
                for event_type, content in event.items():
                    event_message = (topic.value, event_type, content)
                    events.append(event_message)
        return events


UIEvent = Union[
    "ButtonEvent",
    "KeyboardEvent",
    "MouseEvent",
    "TextEvent",
    "GridEvent",
    "WindowEvent",
    "SliderEvent",
    "UserEvent",
]
