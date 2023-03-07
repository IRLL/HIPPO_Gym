from typing import TYPE_CHECKING, Any, Optional

from pymitter import EventEmitter

from hippogym.event_handler import EventHandler, EventTopic, UIEvent

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import TrialStep


class MessageHandler:
    """Base class for elements that reacts to incomming events."""

    def __init__(self) -> None:
        self.event_handler: Optional[EventHandler] = None
        self.emitter = EventEmitter()

    def build(self, trialstep: "TrialStep"):
        """Build the message handler on the current step.

        Args:
            trialstep (TrialStep): Current TrialStep.
        """
        self.event_handler = trialstep.event_handler
        self.event_handler.register(self)
        self.subscribe_to_events_topics()

    def subscribe_to_events_topics(self):
        """Subscribe all on_x_event methods to the EventEmitter."""
        for topic in EventTopic:
            method_name = f"on_{topic.name.lower()}_event"
            listner = getattr(self, method_name)

            # We ignore non-subclassed methods to reduce pass overhead
            if self.is_subclassed(method_name):
                self.emitter.on(topic.value, listner)

    def on_ui_event(self, event_type: UIEvent, *args, **kwargs):
        """How to react to any user interface event.

        Args:
            event_type (KeyboardEvent): Type of the event triggered.
        """

    def on_button_event(self, event_type: "ButtonEvent", value: str):
        """How to react to a button event.

        Args:
            event_type (KeyboardEvent): Type of the event triggered.
            value (KeyboardKey): Value give by the button.
        """

    def on_keyboard_event(self, event_type: "KeyboardEvent", key: "KeyboardKey"):
        """How to react to a keyboard event.

        Args:
            event_type (KeyboardEvent): Type of the event triggered.
            key (KeyboardKey): Key concerned by the event.
        """

    def on_mouse_event(self, event_type: "MouseEvent", event_data):
        """How to react to a mouse event.

        Args:
            event_type (MouseEvent): Type of the event triggered.
            event_data: Mouse event data.
        """

    def on_slider_event(self, event_type: "SliderEvent", content: Any):
        """How to react to a slider event.

        Args:
            event_type (TextEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    def on_text_event(self, event_type: "TextEvent", content: Any):
        """How to react to a text event.

        Args:
            event_type (TextEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    def on_grid_event(self, event_type: "GridEvent", tile_data: str):
        """How to react to a grid event.

        Args:
            event_type (GridEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    def on_window_event(self, event_type: "WindowEvent", content: Any):
        """How to react to a window event.

        Args:
            event_type (WindowEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    def on_user_event(self, event_type: "UserEvent", content: Any):
        """How to react to a user event.

        Args:
            event_type (WindowEvent): Type of the event triggered.
            content (Any): Content concerned by the event.
        """

    @classmethod
    def is_subclassed(cls, method_name: str):
        """Is the given method name subclassed in this subclass ?

        Args:
            method_name (str): Name of the method to check.

        Returns:
            bool: True if the method is subclassed and thus overriten.
        """
        method = getattr(cls, method_name)
        super_method = getattr(MessageHandler, method_name)
        return method is not super_method
