import base64
from io import BytesIO
from typing import Any, Optional, Tuple

from PIL import Image

from hippogym.log import get_logger
from hippogym.ui_elements.ui_element import UIElement

LOGGER = get_logger(__name__)


class GameWindow(UIElement):
    def __init__(
        self,
        width: int = 700,
        height: int = 600,
        mode: str = "responsive",
        image: Optional[str] = None,
        text: Optional[str] = None,
    ) -> None:
        super().__init__("GameWindow")
        self.width = width
        self.height = height
        self.mode = mode
        self.frame = image
        self.text = text
        self.frame_id: int = 0

    def on_window_event(self, event_type: "WindowEvent", content: Any):
        window_event_handlers = {
            "WINDOWRESIZED": self.resize,
        }
        handler = window_event_handlers[event_type]
        handler(content)

    def resize(self, size: Tuple[int, int]):
        self.set_size(*size)

    def params_dict(self) -> dict:
        return {
            "size": (self.width, self.height),
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "frame": self.frame,
            "frameId": self.frame_id,
        }

    def update(self, **kwargs: Any) -> None:
        text = kwargs.pop("text", None)
        image = kwargs.pop("image", None)
        if image is not None:
            if not isinstance(image, str):
                image = self.convert_numpy_array_to_base64(image)
            self.frame = image
            self.text = None
        elif text is not None:
            self.text = text
            self.frame = None
        if text or image:
            self.frame_id += 1
        super().update(**kwargs)

    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    # TODO: add functionality for RGBA array not just RGB
    def convert_numpy_array_to_base64(self, array):
        try:
            img = Image.fromarray(array)
            fp = BytesIO()
            img.save(fp, "JPEG")
            frame = base64.b64encode(fp.getvalue()).decode("utf-8")
            fp.close()
            return frame
        except Exception as error:
            LOGGER.warning("Failed to convert numpy array to Base64: %s", error)
