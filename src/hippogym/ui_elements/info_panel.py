from typing import TYPE_CHECKING
from hippogym.ui_elements.ui_element import UIElement
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from multiprocessing import Queue


class InfoPanel(UIElement):
    def __init__(
        self,
        queue: "Queue",
        out_q: "Queue",
        text: str = None,
        items=None,
        key_value=None,
    ):
        super().__init__(MessageHandler(queue), out_q=out_q)
        self.text = text
        self.items = items if items is not None else []
        self.key_value = key_value if key_value is not None else {}

    def dict(self) -> dict:
        info_panel = {"InfoPanel": None}
        if self.text or self.items or self.key_value:
            info_panel = {
                "InfoPanel": {
                    "text": self.text,
                    "items": self.items,
                    "kv": self.key_value,
                }
            }
        return info_panel
