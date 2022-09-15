from typing import TYPE_CHECKING
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym import HippoGym


class WindowMessageHandler(MessageHandler):
    def __init__(self, hippo: "HippoGym"):
        super().__init__(self.hippo.queues["window_q"])
        self.hippo = hippo
        self.handlers = {
            "WINDOWRESIZED": self.window_resize,
            "MOUSEBUTTONDOWN": self.mouse,
            "MOUSEBUTTONUP": self.mouse,
            "MOUSEMOTION": self.mouse,
        }

    def window_resize(self, event, size, index=0):
        if len(self.hippo.game_windows) > index:
            self.hippo.game_windows[index].set_size(size)

    def mouse(self, event, action, index=0):
        if len(self.hippo.game_windows) > index:
            self.hippo.game_windows[index].add_event({event: action})
