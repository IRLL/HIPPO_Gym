from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from hippogym.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import InteractiveStep


DO_NOT_UPDATE = "DO_NOT_UPDATE&@"


class UIElement(MessageHandler):
    """Base class for all UI elements that compose a TrialStep."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.trialstep: Optional["InteractiveStep"] = None
        MessageHandler.__init__(self)

    def build(self, trialstep: "InteractiveStep") -> None:
        """Build the UIElement for the given step."""
        self.trialstep = trialstep
        MessageHandler.build(self, self.trialstep)

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
            self.trialstep.event_handler.send(self.asdict())
        else:
            self.hide()

    def hide(self) -> None:
        """Hide the UI element."""
        self.trialstep.event_handler.send({self.name: None})

    def update(self, **kwargs: Any) -> None:
        """Update the UIElement with new attr values."""

        for attr_name in dir(self):
            new_attr = kwargs.get(attr_name, DO_NOT_UPDATE)
            if new_attr != DO_NOT_UPDATE:
                setattr(self, attr_name, new_attr)

        if kwargs.get("send", True):
            self.send()
