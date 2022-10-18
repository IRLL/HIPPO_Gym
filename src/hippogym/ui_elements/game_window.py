import base64
import logging
from io import BytesIO
from multiprocessing import Queue
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from PIL import Image

from hippogym.log import get_logger
from hippogym.message_handlers.window import WindowMessageHandler
from hippogym.ui_elements.ui_element import UIElement

LOGGER = get_logger(__name__)

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import InteractiveStep


class GameWindow(UIElement):
    def __init__(
        self,
        width: int = 700,
        height: int = 600,
        mode: str = "responsive",
        image: Optional[str] = None,
        text: Optional[str] = None,
    ) -> None:
        super().__init__("GameWindow", WindowMessageHandler(self))
        self.width = width
        self.height = height
        self.mode = mode
        self.frame = image
        self.text = text
        self.frame_id: int = 0

    def build(self, trialstep: "InteractiveStep") -> None:
        self.events: Queue = Queue(maxsize=10)
        super().build(trialstep)

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

    def add_event(self, event: Dict[str, Any]) -> None:
        if self.events is None:
            raise RuntimeError("Trying to add an event before the GameWindow is built.")
        if self.events.full():
            self.get_event()
        self.events.put(event)

    def get_event(self) -> Optional[str]:
        if self.events is None:
            raise RuntimeError("Trying to get an event before the GameWindow is built.")
        event = None
        if not self.events.empty():
            event = self.events.get()
        return event

    def clear_events(self) -> None:
        if self.events is None:
            raise RuntimeError("Trying to clear events before the GameWindow is built.")
        while not self.events.empty():
            self.events.get()

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
