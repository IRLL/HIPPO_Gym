import time
from threading import Thread
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from hippogym.event_handler import EventsQueues
from hippogym.queue_handler import check_queue, create_or_get_queue

if TYPE_CHECKING:
    from multiprocessing import Queue


class MessageHandler(Thread):
    def __init__(
        self,
        queues: Dict[EventsQueues, "Queue"],
        in_queue_type: EventsQueues,
        out_queue_type: EventsQueues = EventsQueues.OUTPUT,
    ) -> None:
        Thread.__init__(self, daemon=True)
        self.in_queue = create_or_get_queue(queues, in_queue_type)
        self.out_queue = create_or_get_queue(queues, out_queue_type)
        self.handlers = {}

    def send(self, message: Any):
        self.out_queue.put_nowait(message)

    def recv_all(self) -> list:
        return check_queue(self.in_queue)

    def run(self) -> None:
        while True:
            for message in self.recv_all():
                self.call_handlers(message)
            time.sleep(0.01)

    def call_handlers(self, message: Any):
        if not isinstance(message, dict):
            raise NotImplementedError("Non-dict messages are not supported.")
        for key in message.keys():
            if key in self.handlers:
                handler: Callable[[Optional[str]], None] = self.handlers[key]
                handler(message[key])
