from abc import ABC, abstractmethod

from multiprocessing import Queue


class UIElement(ABC):
    """Base class for all UI elements that compose a TrialStep."""

    def __init__(self, messages_queue: Queue) -> None:
        self.messages_queue = messages_queue

    @abstractmethod
    def dict(self) -> dict:
        """Represent the UIElement as a serialized dictionary."""

    def send(self) -> None:
        """Send its serialized representation into the messages queue."""
        self.messages_queue.put_nowait(self.dict())
