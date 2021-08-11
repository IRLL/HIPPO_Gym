import time
from threading import Thread

from hippo_gym.queue_handler import check_queue


class WindowMessageHandler(Thread):
    def __init__(self, hippo):
        Thread.__init__(self)
        self.hippo = hippo

        self.handlers = {
            'WINDOWRESIZED': self.window_resize,
            'MOUSEBUTTONDOWN': self.mouse,
            'MOUSEBUTTONUP': self.mouse,
            'MOUSEMOTION': self.mouse
        }

    def run(self):
        while True:
            messages = check_queue(self.hippo.queues['window_q'])
            for message in messages:
                for key in message.keys():
                    if key in self.handlers:
                        self.handlers[key](key, message[key])
            time.sleep(0.01)

    def window_resize(self, event, size, index=0):
        if len(self.hippo.game_windows) > index:
            self.hippo.game_windows[index].set_size(size)

    def mouse(self, event, action, index=0):
        if len(self.hippo.game_windows) > index:
            self.hippo.game_windows[index].add_event({event: action})
