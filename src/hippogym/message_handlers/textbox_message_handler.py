from typing import TYPE_CHECKING, Dict

from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym import HippoGym


class TextBoxMessageHandler(MessageHandler):
    def __init__(self, hippo: "HippoGym"):
        super().__init__(hippo.queues["textbox_q"])
        self.hippo = hippo
        self.handlers = {
            "TEXTBUTTON": self.button,
            "TEXTREQUEST": self.request,
        }

    def request(self, text: str, index=0) -> None:
        if len(self.hippo.text_boxes) > index:
            self.hippo.text_boxes[index].update(text=text, send=False)

    def button(self, message: Dict[int, str], index=0) -> None:
        if message[0].lower() == "clear":
            self.hippo.text_boxes[index].clear(message[1])
        else:
            self.hippo.text_boxes[index].update(message[1])
