import json


class ControlPanel:
    def __int__(self, pipe, buttons=None, sliders=None, keys=False):
        self.buttons = buttons if type(buttons) == list else None
        self.sliders = sliders if type(sliders) == list else None
        self.keys = keys if type(keys) == bool else False
        self.pipe = pipe

    def send_controls(self):
        control_panel = {'ControlPanel': {
            'Buttons': self.buttons,
            'Sliders': self.sliders,
            'Keys': self.keys
        }}
        self.pipe.send(control_panel)

    def get_buttons(self):
        return self.buttons

    def get_sliders(self):
        return self.sliders

    def get_keys(self):
        return self.keys

    def update(self, buttons=None, sliders=None, keys=None):
        if buttons and type(buttons) == list:
            self.buttons = buttons
        if sliders and type(sliders) == list:
            self.sliders = sliders
        if keys and type(keys) == bool:
            self.keys = keys
