import time
from threading import Thread
from typing import TYPE_CHECKING, Callable, Optional

from hippogym.queue_handler import check_queue

if TYPE_CHECKING:
    from hippogym import HippoGym


class ControlMessageHandler(Thread):
    def __init__(self, hippo: "HippoGym"):
        Thread.__init__(self, daemon=True)
        self.hippo = hippo

        self.handlers = {
            "userId": self.user,
            "projectId": self.project,
            "disconnect": self.disconnect,
            "SLIDERSET": self.slider,
            "start": self.start,
            "pause": self.pause,
            "end": self.end,
        }

    def run(self) -> None:
        while True:
            messages = check_queue(self.hippo.queues["control_q"])
            for message in messages:
                for key in message.keys():
                    if key in self.handlers:
                        handler: Callable[[Optional[str]], None] = self.handlers[key]
                        handler(message[key])
            time.sleep(0.01)

    def user(self, user_id):
        if not self.hippo.user_connected:
            self.hippo.user_id = user_id
            self.hippo.user_connected = True
            self.hippo.send()

    def project(self, project_id: str) -> None:
        self.hippo.project_id = project_id

    def disconnect(self) -> None:
        self.hippo.user_id = None

    def slider(self, setting) -> None:
        if self.hippo.control_panel:
            self.hippo.control_panel.set_slider_value(*setting)

    def start(self, _message:Optional[str]=None):
        self.hippo.start()

    def pause(self, _message:Optional[str]=None):
        self.hippo.pause()
    
    def end(self, _message:Optional[str]=None):
        self.hippo.end()
