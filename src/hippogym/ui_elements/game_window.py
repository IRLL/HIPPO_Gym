import base64
import logging
from io import BytesIO
from multiprocessing import Queue
from typing import TYPE_CHECKING, Optional

from PIL import Image

from hippogym.message_handlers.window import WindowMessageHandler
from hippogym.ui_elements.ui_element import UIElement
from hippogym.log import get_logger

LOGGER = get_logger(__name__)

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import InteractiveStep


class GameWindow(UIElement):
    def __init__(
        self,
        width: int = 700,
        height: int = 600,
        mode="responsive",
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
        self.events: Optional[Queue] = None

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

    def update(self, **kwargs):
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

    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height

    def add_event(self, event):
        if self.events.full():
            self.get_event()
        self.events.put(event)

    def get_event(self) -> Optional[str]:
        event = None
        if not self.events.empty():
            event = self.events.get()
        return event

    def clear_events(self) -> None:
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
