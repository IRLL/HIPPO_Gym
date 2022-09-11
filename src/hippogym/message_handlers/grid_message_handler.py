import time
from threading import Thread
from typing import TYPE_CHECKING, Callable, Optional

from hippogym.queue_handler import check_queue

if TYPE_CHECKING:
    from hippogym import HippoGym


class GridMessageHandler(Thread):
    def __init__(self, hippo: "HippoGym") -> None:
        Thread.__init__(self, daemon=True)
        self.hippo = hippo

        self.handlers = {
            "TILESELECTED": self.select,
            "TILEUNSELECTED": self.unselect,
            "TILECLICKED": self.click,
        }

    def run(self) -> None:
        while True:
            messages = check_queue(self.hippo.queues["grid_q"])
            for message in messages:
                for key in message.keys():
                    if key in self.handlers:
                        handler: Callable[[Optional[str]], None] = self.handlers[key]
                        handler(message[key])
            time.sleep(0.01)

    def select(self, tile) -> None:
        self.hippo.get_grid().select(tuple(tile))

    def unselect(self, tile) -> None:
        self.hippo.get_grid().unselect(tuple(tile))

    def click(self, tile) -> None:
        self.hippo.get_grid().click(tuple(tile))
