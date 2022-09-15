from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from multiprocessing import Queue


class UIElement(ABC):
    """Base class for all UI elements that compose a TrialStep."""

    def __init__(self, messages_queue: "Queue") -> None:
        self.messages_queue = messages_queue

    @abstractmethod
    def dict(self) -> Dict[str, dict]:
        """Represent the UIElement as a serialized dictionary."""

    def send(self) -> None:
        """Send its serialized representation into the messages queue."""
        self.messages_queue.put_nowait(self.dict())

    def hide(self) -> None:
        """Send its serialized representation into the messages queue."""
        for name, _ in self.dict().items():
            self.messages_queue.put_nowait({name: None})

    def update(self, **kwargs) -> None:
        """Update the UIElement with new attr values."""
        for attr_name in dir(self):
            new_attr = kwargs.get(attr_name)
            if new_attr:
                setattr(self, attr_name, new_attr)
        self.send()
