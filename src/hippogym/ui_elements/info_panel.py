from typing import Dict, List

from hippogym.ui_elements.ui_element import UIElement


class InfoPanel(UIElement):
    def __init__(
        self,
        text: str = None,
        items: List[str] = None,
        key_value: Dict[str, str] = None,
    ):
        super().__init__("InfoPanel")
        self.text = text
        self.items = items if items is not None else []
        self.key_value = key_value if key_value is not None else {}

    def params_dict(self) -> dict:
        return {
            "text": self.text,
            "items": self.items,
            "kv": self.key_value,
        }
