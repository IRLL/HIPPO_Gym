from typing import Any, List, Optional, Union

from hippogym.ui_elements.building_blocks.button import Button
from hippogym.ui_elements.building_blocks.slider import Slider
from hippogym.ui_elements.ui_element import UIElement


class ControlPanel(UIElement):
    """A control panel with buttons to press and sliders to slide."""

    def __init__(
        self,
        buttons: Optional[List[Button]] = None,
        sliders: Optional[List[Slider]] = None,
    ) -> None:
        super().__init__("ControlPanel")
        self.buttons: List[Button] = _ensure_list_type(buttons, Button)
        self.sliders: List[Slider] = _ensure_list_type(sliders, Slider)

    def update(self, **kwargs: Any) -> None:
        """Update the control panel with given values.

        Non given values will not stay the same.

        Args:
            buttons (List[Button], optional): List of new buttons. Defaults to None.
            sliders (List[Slider], optional): List of new sliders. Defaults to None.
            keys (bool, optional): New value for keys. Defaults to None.

        Raises:
            TypeError: If given values were not in expected type.
        """
        buttons: Optional[List[Button]] = kwargs.get("buttons")
        sliders: Optional[List[Slider]] = kwargs.get("sliders")
        if buttons is not None:
            self.buttons = _ensure_list_type(buttons, Button)
        if sliders is not None:
            self.sliders = _ensure_list_type(sliders, Slider)
        self.send()

    def set_slider_value(self, slider_title: str, value: float) -> None:
        for slider in self.sliders:
            if slider_title == slider.title:
                slider.value = value
                return
        raise ValueError(f"Could not find slider {slider_title}")

    def on_button_event(self, event_type: "ButtonEvent", value: str):
        button_handlers = {
            "start": self.resume,
            "pause": self.pause,
            "end": self.end,
        }
        handler = button_handlers.get(value, None)
        if handler is not None:
            handler()

    def resume(self) -> None:
        if hasattr(self.trialstep, "running"):
            self.trialstep.running = True

    def pause(self) -> None:
        if hasattr(self.trialstep, "running"):
            self.trialstep.running = False

    def end(self) -> None:
        if hasattr(self.trialstep, "stop"):
            self.trialstep.stop = True
        if hasattr(self.trialstep, "running"):
            self.trialstep.running = False

    def params_dict(self) -> dict:
        """Represent the control panel as a serialized dictionary"""
        return {
            "Buttons": [button.dict() for button in self.buttons],
            "Sliders": [slider.dict() for slider in self.sliders],
            "Keys": True,
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
