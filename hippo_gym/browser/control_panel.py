import json


class ControlPanel:
    def __int__(self, buttons, sliders, keys):
        self.buttons
        self.sliders
        self.keys

    def send_controls(self):
        control_panel = {'ControlPanel': {
            'Buttons': self.buttons,
            'Sliders': self.sliders,
            'Keys': self.keys
        }}
        self.pipe.send(json.dumps(control_panel))
