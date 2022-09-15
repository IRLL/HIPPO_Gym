from queue import Queue
from typing import Any, List, Union

from hippogym.ui_elements.control_panel.button import Button
from hippogym.ui_elements.control_panel.slider import Slider


class ControlPanel:
    """A control panel with buttons to press and sliders to slide."""

    def __init__(self, pipe: Queue, buttons=None, sliders=None, keys=False):
        self.buttons: List[Button] = _ensure_list_type(buttons, Button)
        self.sliders: List[Slider] = _ensure_list_type(sliders, Slider)
        self.keys = keys if isinstance(keys, bool) else False
        self.pipe = pipe

    def send(self):
        self.pipe.put_nowait(self.dict())

    def update(
        self,
        buttons: List[Button] = None,
        sliders: List[Slider] = None,
        keys: bool = None,
    ):
        """Update the control panel with given values.

        Non given values will not stay the same.

        Args:
            buttons (List[Button], optional): List of new buttons. Defaults to None.
            sliders (List[Slider], optional): List of new sliders. Defaults to None.
            keys (bool, optional): New value for keys. Defaults to None.

        Raises:
            TypeError: If given values were not in expected type.
        """
        if buttons is not None:
            self.buttons = _ensure_list_type(buttons, Button)
        if sliders is not None:
            self.sliders = _ensure_list_type(sliders, Slider)
        if keys is not None:
            if not isinstance(keys, bool):
                raise TypeError("Keys must be a bool")
            self.keys = keys
        self.send()

    def set_slider_value(self, slider_title: str, value: float):
        for slider in self.sliders:
            if slider_title == slider.title:
                slider.value = value
                return
        raise ValueError(f"Could not find slider {slider_title}")

    def dict(self) -> dict:
        """Represent the control panel as a serialized dictionary"""
        return {
            "ControlPanel": {
                "Buttons": [button.dict() for button in self.buttons],
                "Sliders": [slider.dict() for slider in self.sliders],
                "Keys": self.keys,
            }
        }


def _ensure_list_type(
    values: Union[list, Any],
    expected_type: type,
    default: Any = None,
) -> list:
    """Ensures that values are a list of the given type.

    Will creating a wrapping list if only one value of the good type is given.

    Args:
        values (Union[list, Any]): List of values to check, or single value to wrap in a list.
        expected_type (type): Expected type of every values in values.
        default (Any, optional): Default return if values is None. Defaults to an empty list.

    Returns:
        list: List of values of the given expected type.
    """
    if default is None:
        default = []
    if values is None:
        values = default
    elif isinstance(values, expected_type):
        values = [values]
    for value in values:
        assert isinstance(value, expected_type)
    return values