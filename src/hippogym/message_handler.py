from typing import TYPE_CHECKING, Any, List, Optional
from hippogym.event_handler import EventHandler, EventTopic, UIEvent

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import TrialStep


class MessageHandler:
    def __init__(self) -> None:
        self.event_handler: Optional[EventHandler] = None

    def build(self, trialstep: "TrialStep"):
        self.event_handler = trialstep.event_handler
        self.subscribe_to_events_topics()

    def subscribe_to_events_topics(self):
        """Subscribe all on_x_event methods to the EventEmitter."""
        for topic in EventTopic:
            listner = getattr(self, f"on_{topic.name.lower()}_event")
            self.event_handler.emitter.on(topic.value, listner)

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

    def on_mouse_event(self, event_type: "MouseEvent", buttons: List["MouseButton"]):
        """How to react to a mouse event.

        Args:
            event_type (MouseEvent): Type of the event triggered.
            buttons (List["MouseButton"]): Mouse button concerned by the event.
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
