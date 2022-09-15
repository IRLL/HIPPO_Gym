import time
from typing import TYPE_CHECKING, Callable, Optional

from threading import Thread

from hippogym.queue_handler import check_queue

if TYPE_CHECKING:
    from multiprocessing import Queue


class MessageHandler(Thread):
    def __init__(self, queue: "Queue") -> None:
        Thread.__init__(self, daemon=True)
        self.queue = queue
        self.handlers = {}

    def run(self) -> None:
        while True:
            messages = check_queue(self.queue)
            for message in messages:
                for key in message.keys():
                    if key in self.handlers:
                        handler: Callable[[Optional[str]], None] = self.handlers[key]
                        handler(message[key])
            time.sleep(0.01)
