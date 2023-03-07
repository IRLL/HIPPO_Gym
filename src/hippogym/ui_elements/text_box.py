import time

from hippogym.ui_elements.ui_element import UIElement


class TextBox(UIElement):
    def __init__(
        self,
        idx=0,
        width=700,
        height=600,
        mode="responsive",
        text=None,
        editable=True,
        bgcolor="white",
        color="black",
        font=None,
        syntax=None,
        buttons=None,
    ):
        super().__init__("TextBox")
        self.idx = idx
        self.width = width
        self.height = height
        self.mode = mode
        self.text = text
        self.text_buffer = []
        self.editable = editable
        self.bgcolor = bgcolor
        self.color = color
        self.font = font
        self.syntax = syntax
        self.buttons = buttons
        self.updated = True

    def params_dict(self) -> dict:
        return {
            "idx": self.idx,
            "size": (self.width, self.height),
            "width": self.width,
            "height": self.height,
            "mode": self.mode,
            "text": self.text,
            "editable": self.editable,
            "bgcolor": self.bgcolor,
            "color": self.color,
            "font": self.font,
            "syntax": self.syntax,
            "buttons": self.buttons,
        }

    def update(self, **kwargs):
        new_text = kwargs.pop("text", None)
        if new_text:
            self.update_buffer()
            self.text = new_text

        super().update(**kwargs)
        self.updated = True

    def clear(self, text=None):
        self.update(text=text)
        self.update_buffer()
        self.text = ""

    def update_buffer(self):
        self.text_buffer.append(self.text)
        if len(self.text_buffer) > 10:
            self.text_buffer.pop(0)

    def get_text(self):
        while not self.updated:
            time.sleep(0.1)
        return self.text
