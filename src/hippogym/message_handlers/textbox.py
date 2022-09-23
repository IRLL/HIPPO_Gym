from typing import TYPE_CHECKING, Dict

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym.ui_elements.text_box import TextBox


class TextBoxMessageHandler(MessageHandler):
    def __init__(self, textbox: "TextBox"):
        super().__init__(EventsQueues.TEXTBOX)
        self.textbox = textbox
        self.handlers = {
            "TEXTBUTTON": self.button,
            "TEXTREQUEST": self.request,
        }

    def request(self, text: str) -> None:
        self.textbox.update(text=text, send=False)

    def button(self, message: Dict[int, str]) -> None:
        if message[0].lower() == "clear":
            self.textbox.clear(message[1])
        else:
            self.textbox.update(message[1])
