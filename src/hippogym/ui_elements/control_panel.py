from queue import Queue
from typing import Any, List, Union

from hippogym.ui_elements.button import Button, standard_controls


class ControlPanel:
    def __init__(self, pipe: Queue, buttons=None, sliders=None, keys=False):
        self.buttons: List[Button] = ensure_list_type(buttons, Button)
        self.sliders = sliders if type(sliders) == list else []
        self.keys = keys if type(keys) == bool else False
        self.pipe = pipe

    def send(self):
        self.pipe.put_nowait(self.dict())

    def get_buttons(self):
        return self.buttons

    def get_sliders(self):
        return self.sliders

    def get_keys(self):
        return self.keys

    def update(self, buttons=None, sliders=None, keys=None):
        if buttons and type(buttons) == list:
            self.buttons = buttons
        if sliders and type(sliders) == list:
            self.sliders = sliders
        if keys and type(keys) == bool:
            self.keys = keys
        self.send()

    def add_button(
        self,
        text=None,
        icon=None,
        image=None,
        color=None,
        bgcolor=None,
        value=None,
        confirm=False,
    ):
        button = dict(
            text=text,
            icon=icon,
            image=image,
            color=color,
            bgcolor=bgcolor,
            value=value,
            confirm=confirm,
        )
        self.buttons.append({"Button": button})
        return button, len(self.buttons) - 1

    def remove_button(self, index):
        if type(index) == int:
            button = self.buttons.pop(index)
            return button
        else:
            return {"Error": "Index not of type int"}

    def reset_buttons(self):
        self.buttons = []

    def add_slider(self, title=None, id=None, min=1, max=100, value=50):
        slider = dict(title=title, id=id, min=min, max=max, value=value)
        self.sliders.append(slider)
        return slider

    def remove_slider(self, index):
        if type(index) == int:
            slider = self.sliders.pop(index)
            return slider
        else:
            return {"Error": "Index not of type int"}

    def reset_sliders(self):
        self.sliders = []

    def set_slider_value(self, slider_id, value):
        for slider in self.sliders:
            if slider_id == slider.get("Slider", {}).get("id", None):
                slider["Slider"]["value"] = value

    def set_keys(self, setting):
        if type(setting) == bool:
            self.keys = setting
        return self.keys

    def use_standard_buttons(self):
        self.buttons = standard_controls

    def use_image_sliders(self):
        self.sliders = image_sliders

    def reset(self):
        self.reset_buttons()
        self.reset_sliders()
        self.keys = False
        self.send()

    def dict(self) -> dict:
        return {
            "ControlPanel": {
                "Buttons": [button.dict() for button in self.buttons],
                "Sliders": self.sliders,
                "Keys": self.keys,
            }
        }


def ensure_list_type(
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


brightness_slider = {
    "Slider": {
        "title": "Brightness",
        "icon": "BsFillBrightnessHighFill",
        "id": "brightness",
        "min": 0,
        "max": 1000,
        "value": 100,
    }
}

contrast_slider = {
    "Slider": {
        "title": "Contrast",
        "icon": "IoContrast",
        "id": "contrast",
        "min": 0,
        "max": 500,
        "value": 100,
    }
}

saturation_slider = {
    "Slider": {
        "title": "Saturation",
        "icon": "BsDropletHalf",
        "id": "saturation",
        "min": 0,
        "max": 100,
        "value": 100,
    }
}

hue_slider = {
    "Slider": {
        "title": "Hue",
        "icon": "IoColorPaletteOutline",
        "id": "hue",
        "min": 0,
        "max": 360,
        "value": 0,
    }
}

image_sliders = [brightness_slider, contrast_slider, saturation_slider, hue_slider]
