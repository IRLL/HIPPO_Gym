from typing import TYPE_CHECKING, Dict

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from multiprocessing import Queue

    from hippogym import HippoGym


class UserMessageHandler(MessageHandler):
    def __init__(self, hippo: "HippoGym", queues: Dict[EventsQueues, "Queue"]):
        super().__init__(queues, EventsQueues.USER)
        self.hippo = hippo

        self.handlers = {
            "userId": self.user,
            "projectId": self.project,
            "disconnect": self.disconnect,
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
