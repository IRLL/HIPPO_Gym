from typing import TYPE_CHECKING

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym.ui_elements.game_window import GameWindow


class WindowMessageHandler(MessageHandler):
    def __init__(self, game_window: "GameWindow"):
        super().__init__(EventsQueues.WINDOW)
        self.game_window = game_window
        self.handlers = {
            "WINDOWRESIZED": self.resize,
            "MOUSEBUTTONDOWN": self.mouse_down,
            "MOUSEBUTTONUP": self.mouse_up,
            "MOUSEMOTION": self.mouse_move,
        }

    def resize(self, size):
        width, height = size
        self.game_window.set_size(width, height)

    def mouse_down(self, event_action):
        self.game_window.add_event({"MOUSEBUTTONDOWN": event_action})

    def mouse_up(self, event_action):
        self.game_window.add_event({"MOUSEBUTTONUP": event_action})

    def mouse_move(self, event_action):
        self.game_window.add_event({"MOUSEMOTION": event_action})
