from typing import TYPE_CHECKING, Any, Dict, List, Union

from hippogym.message_handlers.control import ControlMessageHandler
from hippogym.ui_elements.building_blocks.button import Button
from hippogym.ui_elements.building_blocks.slider import Slider
from hippogym.ui_elements.ui_element import UIElement

if TYPE_CHECKING:
    from multiprocessing import Queue

    from hippogym.event_handler import EventsQueues


class ControlPanel(UIElement):
    """A control panel with buttons to press and sliders to slide."""

    def __init__(
        self,
        queues: Dict["EventsQueues", "Queue"],
        hippo,
        buttons=None,
        sliders=None,
        keys=False,
    ):
        super().__init__("ControlPanel", ControlMessageHandler(self, queues, hippo))
        self.buttons: List[Button] = _ensure_list_type(buttons, Button)
        self.sliders: List[Slider] = _ensure_list_type(sliders, Slider)
        self.keys = keys if isinstance(keys, bool) else False

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

    def params_dict(self) -> dict:
        """Represent the control panel as a serialized dictionary"""
        return {
            "Buttons": [button.dict() for button in self.buttons],
            "Sliders": [slider.dict() for slider in self.sliders],
            "Keys": self.keys,
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
