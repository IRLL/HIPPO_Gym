from typing import TYPE_CHECKING, Optional

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym import HippoGym
    from hippogym.ui_elements.control_panel import ControlPanel


class ControlMessageHandler(MessageHandler):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__(EventsQueues.CONTROL)
        self.control_panel = control_panel

        self.handlers = {
            "SLIDERSET": self.slider,
            "start": self.resume,
            "pause": self.pause,
            "end": self.end,
        }

    def slider(self, setting: str) -> None:
        if self.control_panel is not None:
            self.control_panel.set_slider_value(*setting)

    def resume(self, _message: Optional[str] = None):
        self.hippo.start()

    def pause(self, _message: Optional[str] = None):
        self.hippo.pause()

    def end(self, _message: Optional[str] = None):
        self.hippo.end()
