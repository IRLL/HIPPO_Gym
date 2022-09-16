from typing import TYPE_CHECKING
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym.ui_elements.game_window import GameWindow
    from multiprocessing import Queue


class WindowMessageHandler(MessageHandler):
    def __init__(self, game_window: "GameWindow", queue: "Queue"):
        super().__init__(queue)
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
        event = "MOUSEBUTTONDOWN"
        self.game_window.add_event({event: event_action})

    def mouse_up(self, event_action):
        event = "MOUSEBUTTONUP"
        self.game_window.add_event({event: event_action})

    def mouse_move(self, event_action):
        event = "MOUSEMOTION"
        self.game_window.add_event({event: event_action})
