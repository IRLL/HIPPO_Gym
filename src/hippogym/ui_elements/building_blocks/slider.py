from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Slider:
    """Slider for the control panel"""

    title: str
    min_value: float
    max_value: float
    init_value: float
    icon: Optional[str] = field(default=None)

    def __post_init__(self):
        self._value = self.clip(self.init_value)

    def dict(self) -> Dict[str, Any]:
        """Convert Slider to a dict"""
        dataclass_dict = asdict(self)
        dataclass_dict.update({"value": self.value})
        return {"Slider": dataclass_dict}

    @property
    def value(self) -> float:
        """Current value of the slider"""
        return self._value

    @value.setter
    def value(self, new_value: float) -> None:
        self._value = self.clip(new_value)

    def clip(self, value: float) -> float:
        """Clip the given value within allowed range.

        Args:
            value (float): Value to clip

        Returns:
            float: Clipped value
        """
        return min(self.max_value, max(self.min_value, value))


brightness_slider = Slider(
    title="Brightness",
    icon="BsFillBrightnessHighFill",
    min_value=0,
    max_value=1000,
    init_value=100,
)

contrast_slider = Slider(
    title="Contrast",
    icon="IoContrast",
    min_value=0,
    max_value=500,
    init_value=100,
)

saturation_slider = Slider(
    title="Saturation",
    icon="BsDropletHalf",
    min_value=0,
    max_value=100,
    init_value=100,
)

hue_slider = Slider(
    title="Hue",
    icon="IoColorPaletteOutline",
    min_value=0,
    max_value=360,
    init_value=0,
)

image_sliders = [brightness_slider, contrast_slider, saturation_slider, hue_slider]
