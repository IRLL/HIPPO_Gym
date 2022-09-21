from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict


if TYPE_CHECKING:
    from multiprocessing import Queue

    from hippogym import HippoGym
    from hippogym.event_handler import EventsQueues
    from hippogym.message_handlers.message_handler import MessageHandler

DO_NOT_UPDATE = "DO_NOT_UPDATE&@"


class UIElement(ABC):
    """Base class for all UI elements that compose a TrialStep."""

    def __init__(self, name: str, message_handler: "MessageHandler") -> None:
        self.name = name
        self.message_handler = message_handler

    @abstractmethod
    def params_dict(self) -> dict:
        """Represent the content of the UIElement as a serialized dictionary"""

    def asdict(self) -> Dict[str, dict]:
        """Represent the UIElement as a serialized dictionary."""
        return {self.name: self.params_dict()}

    def send(self) -> None:
        """Send its serialized representation into the messages queue."""
        attributes = self.params_dict()
        if any(attr is not None for attr in attributes.values()):
            self.message_handler.send(self.asdict())
        else:
            self.hide()

    def hide(self) -> None:
        """Hide the UI element."""
        self.message_handler.send({self.name: None})

    def update(self, **kwargs) -> None:
        """Update the UIElement with new attr values."""

        for attr_name in dir(self):
            new_attr = kwargs.get(attr_name, DO_NOT_UPDATE)
            if new_attr != DO_NOT_UPDATE:
                setattr(self, attr_name, new_attr)

        if kwargs.get("send", True):
            self.send()

    def set_queues(self, queues: Dict["EventsQueues", "Queue"]) -> None:
        self.message_handler.set_queues(queues)

    def set_hippo(self, hippo: "HippoGym") -> None:
        self.message_handler.set_hippo(hippo)
