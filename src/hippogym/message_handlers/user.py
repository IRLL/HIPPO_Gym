from typing import TYPE_CHECKING

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym import HippoGym


class UserMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(EventsQueues.USER)

        self.handlers = {
            "userId": self.start_trial,
            "disconnect": self.stop_trial,
            "projectId": self.project,
        }

    def project(self, project_id: str) -> None:
        self.hippo.project_id = project_id

    def start_trial(self, user_id: str) -> None:
        self.hippo.start_trial(user_id)

    def stop_trial(self, user_id: str) -> None:
        self.hippo.stop_trial(user_id)
