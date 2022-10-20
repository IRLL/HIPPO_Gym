from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from hippogym.event_handler import EventTopic

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import InteractiveStep


DO_NOT_UPDATE = "DO_NOT_UPDATE&@"


class UIElement(ABC):
    """Base class for all UI elements that compose a TrialStep."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.trialstep: Optional["InteractiveStep"] = None

    def build(self, trialstep: "InteractiveStep") -> None:
        """Build the UIElement for the given step."""
        self.trialstep = trialstep

    def start(self) -> None:
        """Start the UIElement on the given TrialStep."""
        self.subscribe_to_events_topics()

    def subscribe_to_events_topics(self):
        """Subscribe all on_x_event methods to the EventEmitter."""
        for topic in EventTopic:
            listner = getattr(self, f"on_{topic.name.lower()}_event", None)
            self.trialstep.event_handler.emitter.on(topic.value, listner)

    def on_button_event(self, event_type: "ButtonEvent", value: str):
        """How the UIElement reacts to a button event.

        Args:
            event_type (KeyboardEvent): Type of the event triggered.
            value (KeyboardKey): Value give by the button.
        """

    def on_keyboard_event(self, event_type: "KeyboardEvent", key: "KeyboardKey"):
        """How the UIElement reacts to a keyboard event.

        Args:
            event_type (KeyboardEvent): Type of the event triggered.
            key (KeyboardKey): Key concerned by the event.
        """

    def on_mouse_event(self, event_type: "MouseEvent", buttons: List["MouseButton"]):
        """How the UIElement reacts to a mouse event.

        Args:
            event_type (MouseEvent): Type of the event triggered.
            buttons (List["MouseButton"]): Mouse button concerned by the event.
        """

    def on_text_event(self, event_type: "TextEvent", content: Any):
        """How the UIElement reacts to a text event.

        Args:
            event_type (TextEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    def on_grid_event(self, event_type: "GridEvent", content: Any):
        """How the UIElement reacts to a grid event.

        Args:
            event_type (GridEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    def on_window_event(self, event_type: "WindowEvent", content: Any):
        """How the UIElement reacts to a window event.

        Args:
            event_type (WindowEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

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
