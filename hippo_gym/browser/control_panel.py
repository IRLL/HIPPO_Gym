class ControlPanel:
    def __init__(self, pipe, buttons=None, sliders=None, keys=False):
        self.buttons = buttons if type(buttons) == list else None
        self.sliders = sliders if type(sliders) == list else None
        self.keys = keys if type(keys) == bool else False
        self.pipe = pipe
        self.send_controls()

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
        self.send_controls()

    def add_button(self, text=None, icon=None, image=None, color=None, bgcolor=None, value=None):
        button = dict(text=text, icon=icon, image=image, color=color, bgcolor=bgcolor, value=value)
        self.buttons.append({"Button": button})
        return button

    def remove_button(self, index):
        if type(index) == int:
            button = self.buttons.pop(index)
            return button
        else:
            return {"Error": "Index not of type int"}

    def add_slider(self, title=None, id=None, min=1, max=100, value=50):
        slider = dict(title=title, id=id, min=min, max=max, value=value)
        self.sliders.append(slider)
        return slider

    def remove_slider(self, index):
        if type(index) == int:
            slider = self.sliders.pop(index)
            return slider
        else:
            return {"Error": "Index not of type int"}

    def set_keys(self, setting):
        if type(setting) == bool:
            self.keys = setting
        return self.keys
