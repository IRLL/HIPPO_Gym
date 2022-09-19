from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from multiprocessing import Queue

    from hippogym.message_handlers.message_handler import MessageHandler

DO_NOT_UPDATE = "DO_NOT_UPDATE&@"


class UIElement(ABC):
    """Base class for all UI elements that compose a TrialStep."""

    def __init__(self, name: str, message_handler: "MessageHandler") -> None:
        self.name = name
        self.message_handler = message_handler
        self.message_handler.start()

    @abstractmethod
    def params_dict(self) -> dict:
        """Represent the content of the UIElement as a serialized dictionary"""

    def dict(self) -> Dict[str, dict]:
        """Represent the UIElement as a serialized dictionary."""
        return {self.name: self.params_dict()}

    def send(self) -> None:
        """Send its serialized representation into the messages queue."""
        self.message_handler.send(self.dict())

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
