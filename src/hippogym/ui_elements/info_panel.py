from typing import TYPE_CHECKING
from hippogym.ui_elements.ui_element import UIElement

if TYPE_CHECKING:
    from multiprocessing import Queue


class InfoPanel(UIElement):
    def __init__(self, queue: "Queue", text: str = None, items=None, key_value=None):
        super().__init__(queue)
        self.text = text
        self.items = items if items is not None else []
        self.key_value = key_value if key_value is not None else {}

    def dict(self) -> dict:
        info_panel = {"InfoPanel": None}
        if self.text or len(self.items) != 0 or len(self.key_value) != 0:
            info_panel = {
                "InfoPanel": {
                    "text": self.text,
                    "items": self.items,
                    "kv": self.key_value,
                }
            }
        return info_panel
