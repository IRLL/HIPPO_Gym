import asyncio
import logging
from enum import Enum

from typing import TYPE_CHECKING, Any, Dict, Union
from pymitter import EventEmitter

from threading import Thread


if TYPE_CHECKING:
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
        self.emitter = EventEmitter()
        event_thread = Thread(target=self.run)
        event_thread.start()

    def send(self, message: Any) -> None:
        """Send message into the output Queue.

        Args:
            message (Any): Message sent into the output Queue.

        """
        self.out_q.put_nowait(message)

    def run(self):
        asyncio.run(self.producer_handler())

    async def producer_handler(self):
        done = False
        while not done:
            message = await self.recv()
            self.emit(message)
            await asyncio.sleep(0.01)

    async def recv(self) -> list:
        while self.in_q.empty():
            await asyncio.sleep(0.01)
        return self.in_q.get()

    def emit(self, message: Dict[str, Any]):
        """Emit the given message in relevant topic."""
        for key, event in message.items():
            if key in _key_to_topic:
                topic = _key_to_topic[key]
                if isinstance(event, dict):
                    for event_type, content in event.items():
                        self.emitter.emit(topic.value, event_type, content)
                else:
                    raise NotImplementedError


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
