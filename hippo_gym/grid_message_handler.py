import time
from threading import Thread

from hippo_gym.queue_handler import check_queue

class GridMessageHandler(Thread):
    def __init__(self, hippo):
        Thread.__init__(self, daemon=True)
        self.hippo = hippo

        self.handlers = {
            'TILESELECTED': self.select,
            'TILEUNSELECTED': self.unselect,
            'TILECLICKED': self.click
            }

    def run(self):
        while True:
            messages = check_queue(self.hippo.queues['grid_q'])
            for message in messages:
                for key in message.keys():  
                    if key in self.handlers:
                        self.handlers[key](message[key])
            time.sleep(0.01)

    def select(self, tile):
        self.hippo.get_grid().select(tuple(tile))

    def unselect(self, tile):
        self.hippo.get_grid().unselect(tuple(tile))

    def click(self, tile):
        self.hipppo.get_grid().click(tuple(tile))
