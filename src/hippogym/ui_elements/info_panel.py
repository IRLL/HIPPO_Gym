from typing import TYPE_CHECKING, Dict

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler
from hippogym.queue_handler import create_or_get_queue
from hippogym.ui_elements.ui_element import UIElement

if TYPE_CHECKING:
    from multiprocessing import Queue


class InfoPanel(UIElement):
    def __init__(
        self,
        queues: Dict[EventsQueues, "Queue"],
        text: str = None,
        items=None,
        key_value=None,
    ):
        super().__init__("InfoPanel", MessageHandler(queues, EventsQueues.INFO_PANEL))
        self.text = text
        self.items = items if items is not None else []
        self.key_value = key_value if key_value is not None else {}

    def params_dict(self) -> dict:
        return {
            "text": self.text,
            "items": self.items,
            "kv": self.key_value,
        }
