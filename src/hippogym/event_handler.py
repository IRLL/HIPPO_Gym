import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict
from pymitter import EventEmitter

if TYPE_CHECKING:
    from multiprocessing import Queue

LOGGER = logging.getLogger(__name__)


class EventsQueues(Enum):
    """Events shared messages queues."""

    KEYBOARD = "keyboard_q"
    BUTTON = "button_q"
    WINDOW = "window_q"
    STANDARD = "standard_q"
    CONTROL = "control_q"
    TEXTBOX = "textbox_q"
    GRID = "grid_q"
    USER = "user_q"
    INFO_PANEL = "info_q"

    OUTPUT = "out_q"


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


class EventHandler:
    def __init__(self, in_q: "Queue", out_q: "Queue") -> None:
        self.in_q = in_q
        self.out_q = out_q
        self.emitter = EventEmitter()

    def parse(self, message: Dict[str, Any]) -> None:
        raise NotImplementedError

    def send(self, message: Any) -> None:
        """Send message into the output Queue.

        Args:
            message (Any): Message sent into the output Queue.

        """
        self.out_q.put_nowait(message)

    def emit(self, message: Dict[str, Any]):
        """Emit the given message in relevant topic."""
        for key, content in message.items():
            for topic in EventTopic:
                if key == topic.value.split(".")[-1]:
                    self.emitter.emit(topic.value, content)
