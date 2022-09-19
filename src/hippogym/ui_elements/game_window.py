import base64
import logging
from io import BytesIO
from multiprocessing import Queue
from typing import TYPE_CHECKING, Dict, Optional

from PIL import Image

from hippogym.message_handlers.window import WindowMessageHandler
from hippogym.ui_elements.ui_element import UIElement

if TYPE_CHECKING:
    from hippogym.event_handler import EventsQueues


class GameWindow(UIElement):
    def __init__(
        self,
        queues: Dict["EventsQueues", Queue],
        width=700,
        height=600,
        mode="responsive",
        image=None,
        text=None,
    ) -> None:
        super().__init__("GameWindow", WindowMessageHandler(self, queues))
        self.width = width
        self.height = height
        self.mode = mode
        self.frame = image
        self.text = text
        self.frame_id = 0
        self.events: Queue = Queue(maxsize=10)

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
        except Exception as e:
            logging.info("Failed to convert numpy array to Base64")
            logging.info(f"Numpy Array conversion error: {e}")
