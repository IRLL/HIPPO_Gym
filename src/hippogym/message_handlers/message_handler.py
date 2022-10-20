import time
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import TrialStep
    from hippogym.event_handler import EventHandler


class MessageHandler:
    """Handle messages between a UIElement and the client."""

    def __init__(self) -> None:
        """Handle messages between a UIElement and the client."""
        self.trialstep: "TrialStep" = None
        self.event_handler: Optional["EventHandler"] = None
        self.handlers: Dict[str, Callable] = {}

    def set_step(self, trialstep: "TrialStep") -> None:
        """Associate the MessageHandler to a Trial instance."""
        self.trialstep = trialstep
        self.event_handler = self.trialstep.event_handler

    def send(self, message: Any) -> None:
        """Send a message to the UI."""
        self.event_handler.send(message)

    def run(self) -> None:
        """Run the message handler on a new Thread."""
        # Subscribe to relevant topics with relevant functions and run forever.
        raise NotImplementedError
