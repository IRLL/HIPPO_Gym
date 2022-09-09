import time
from threading import Thread

from hippogym.queue_handler import check_queue


class TextBoxMessageHandler(Thread):
    def __init__(self, hippo):
        Thread.__init__(self, daemon=True)
        self.hippo = hippo

        self.handlers = {
            'TEXTBUTTON': self.button,
            'TEXTREQUEST': self.request,
        }

    def run(self):
        while True:
            messages = check_queue(self.hippo.queues['textbox_q'])
            for message in messages:
                for key in message.keys():
                    if key in self.handlers:
                        self.handlers[key](message[key])
            time.sleep(0.01)

    def request(self, text, index=0):
        if len(self.hippo.text_boxes) > index:
            self.hippo.text_boxes[index].update(text=text, send=False)

    def button(self, message, index=0):
        if message[0].lower() == 'clear':
            self.hippo.text_boxes[index].clear(message[1])
        else:
            self.hippo.text_boxes[index].update(message[1])
