import logging
from enum import Enum
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from multiprocessing import Queue

LOGGER = logging.getLogger(__name__)


class EventsQueues(Enum):
    """Events shared messages queues."""

    KEYBOARD = "keyboard_q"
    BUTTON = "button_q"
    WINDOW = "window_q"
    STANDARD = "standard_q"
    CONTROL = "control_q"
    TEXTBOX = "textbox_q"
    GRID = "grid_q"
    USER = "user_q"
    INFO_PANEL = "info_q"
    OUTPUT = "out_q"


class EventHandler:
    def __init__(self, queues: Dict[EventsQueues, "Queue"]):
        for queue_name in EventsQueues:
            if queue_name not in queues:
                LOGGER.debug("No %s in EventHandler", queue_name)

        self.queues = queues
        self.pressed_keys = set()
        self.key_map = {
            "w": "up",
            "a": "left",
            "s": "down",
            "d": "right",
            " ": "fire",
            "ArrowUp": "up",
            "ArrowDown": "down",
            "ArrowLeft": "left",
            "ArrowRight": "right",
        }

        self.handlers = {
            "KeyboardEvent": self.handle_keyboard_event,
            "MouseEvent": self.handle_window_event,
            "ButtonEvent": self.handle_button_event,
            "WindowEvent": self.handle_window_event,
            "SliderEvent": self.handle_slider_event,
            "TextEvent": self.handle_text_event,
            "GridEvent": self.handle_grid_event,
        }

    def parse(self, message):
        for key in message.keys():
            if key in self.handlers:
                self.handlers[key](message[key])

    def handle_text_event(self, message: dict):
        put_in_queue(message, self.queues[EventsQueues.TEXTBOX])

    def handle_keyboard_event(self, message: dict):
        put_in_queue(message, self.queues[EventsQueues.KEYBOARD])
        # check for common keys to add to standard_q events
        keydown = message.get("KEYDOWN", None)
        if keydown:
            key = keydown[0]
            if key in self.key_map.keys() and key not in self.pressed_keys:
                self.pressed_keys.add(key)
                self.check_standard_message(key)
        keyup = message.get("KEYUP", None)
        if keyup:
            key = keyup[0]
            if key in self.key_map.keys() and key in self.pressed_keys:
                self.pressed_keys.remove(key)
                self.check_standard_message(key)

    def handle_button_event(self, message: dict):
        put_in_queue(message, self.queues[EventsQueues.BUTTON])
        button = message.get("BUTTONPRESSED", None)
        if button:
            self.check_standard_message(button)
        if button in ("start", "pause", "end"):
            new_message = {button: True}
            put_in_queue(new_message, self.queues[EventsQueues.CONTROL])

    def handle_window_event(self, message: dict):
        put_in_queue(message, self.queues[EventsQueues.WINDOW])

    def handle_grid_event(self, message: dict):
        put_in_queue(message, self.queues[EventsQueues.GRID])

    def check_standard_message(self, event):
        action = None
        if event in self.key_map.keys():
            if len(self.pressed_keys) == 0:
                action = "noop"
            elif "a" in self.pressed_keys and "w" in self.pressed_keys:
                action = "upleft"
            elif "a" in self.pressed_keys and "s" in self.pressed_keys:
                action = "downleft"
            elif "d" in self.pressed_keys and "w" in self.pressed_keys:
                action = "upright"
            elif "d" in self.pressed_keys and "s" in self.pressed_keys:
                action = "downright"
            else:
                key = self.pressed_keys.pop()
                self.pressed_keys.add(key)
                action = self.key_map[key]

        elif event == "w" or event == "ArrowUp" or event == "up":
            action = "up"
        elif event == "s" or event == "ArrowDown" or event == "down":
            action = "down"
        elif event == "a" or event == "ArrowLeft" or event == "left":
            action = "left"
        elif event == "d" or event == "ArrowRight" or event == "right":
            action = "right"
        elif event == " " or event == "fire":
            action = "fire"
        if action:
            put_in_queue({"ACTION": action}, self.queues[EventsQueues.STANDARD])

    def handle_slider_event(self, message: dict):
        put_in_queue(message, self.queues[EventsQueues.CONTROL])

    def connect(self, user_id: str, project_id: str):
        message = {"userId": user_id, "projectId": project_id}
        put_in_queue(message, self.queues[EventsQueues.USER])

    def disconnect(self, user_id: str, project_id: str):
        put_in_queue(
            {"disconnect": user_id, "projectId": project_id},
            self.queues[EventsQueues.USER],
        )


def put_in_queue(message, queue):
    try:
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(message)
    except Exception as e:
        LOGGER.error(e)
