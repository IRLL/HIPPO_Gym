from typing import TYPE_CHECKING, Optional

from hippogym.message_handlers.message_handler import MessageHandler


if TYPE_CHECKING:
    from multiprocessing import Queue
    from hippogym import HippoGym
    from hippogym.ui_elements.control_panel import ControlPanel


class ControlMessageHandler(MessageHandler):
    def __init__(
        self, control_panel: "ControlPanel", queue: "Queue", hippo: "HippoGym"
    ):
        super().__init__(queue)
        self.hippo = hippo
        self.control_panel = control_panel

        self.handlers = {
            "userId": self.user,
            "projectId": self.project,
            "disconnect": self.disconnect,
            "SLIDERSET": self.slider,
            "start": self.resume,
            "pause": self.pause,
            "end": self.end,
        }

    def user(self, user_id: str):
        if not self.hippo.user_id:
            self.hippo.user_id = user_id
            self.hippo.send()
            return
        raise ValueError(
            "Two users conflicting: %s and %s", user_id, self.hippo.user_id
        )

    def project(self, project_id: str) -> None:
        self.hippo.project_id = project_id

    def disconnect(self, user_id: str) -> None:
        if self.hippo.user_id == user_id:
            self.hippo.user_id = None
            return
        raise ValueError(
            "Cannot disconnect unkown user: %s. Known users: %s",
            user_id,
            self.hippo.user_id,
        )

    def slider(self, setting: str) -> None:
        if self.control_panel is not None:
            self.control_panel.set_slider_value(*setting)

    def resume(self, _message: Optional[str] = None):
        self.hippo.start()

    def pause(self, _message: Optional[str] = None):
        self.hippo.pause()

    def end(self, _message: Optional[str] = None):
        self.hippo.end()
