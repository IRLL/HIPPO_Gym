import time
from threading import Thread
from typing import TYPE_CHECKING, Callable, Dict, Optional

from hippogym.queue_handler import check_queue

if TYPE_CHECKING:
    from hippogym import HippoGym


class TextBoxMessageHandler(Thread):
    def __init__(self, hippo: "HippoGym"):
        Thread.__init__(self, daemon=True)
        self.hippo = hippo

        self.handlers = {
            "TEXTBUTTON": self.button,
            "TEXTREQUEST": self.request,
        }

    def run(self) -> None:
        while True:
            messages = check_queue(self.hippo.queues["textbox_q"])
            for message in messages:
                for key in message.keys():
                    if key in self.handlers:
                        handler: Callable[[Optional[str]], None] = self.handlers[key]
                        handler(message[key])
            time.sleep(0.01)

    def request(self, text:str, index=0) -> None:
        if len(self.hippo.text_boxes) > index:
            self.hippo.text_boxes[index].update(text=text, send=False)

    def button(self, message:Dict[int, str], index=0) -> None:
        if message[0].lower() == "clear":
            self.hippo.text_boxes[index].clear(message[1])
        else:
            self.hippo.text_boxes[index].update(message[1])
