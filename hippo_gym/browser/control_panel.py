class ControlPanel:
    def __init__(self, pipe, buttons=None, sliders=None, keys=False):
        self.buttons = buttons if type(buttons) == list else None
        self.sliders = sliders if type(sliders) == list else None
        self.keys = keys if type(keys) == bool else False
        self.pipe = pipe

    def send(self):
        control_panel = {'ControlPanel': {
            'Buttons': self.buttons,
            'Sliders': self.sliders,
            'Keys': self.keys
        }}
        self.pipe.put_nowait(control_panel)

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
        self.send()

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

    def reset_buttons(self):
        self.buttons = None

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

    def reset_sliders(self):
        self.sliders = None

    def set_slider_value(self, slider_id, value):
        print(slider_id, value)
        for slider in self.sliders:
            if slider_id == slider.get('Slider', {}).get('id', None):
                slider['Slider']['value'] = value

    def set_keys(self, setting):
        if type(setting) == bool:
            self.keys = setting
        return self.keys

    def use_standard_buttons(self):
        self.buttons = standard_controls

    def use_image_sliders(self):
        self.sliders = image_sliders


start_button = {'Button': {
    'image': None,
    'icon': 'FaPlayCircle',
    'text': 'start',
    'color': 'white',
    'bgcolor': 'green',
    'value': 'start'
}}

reset_button = {'Button': {
    'image': None,
    'icon': 'FaRedo',
    'text': 'reset',
    'color': 'white',
    'bgcolor': 'red',
    'value': 'reset'
}}

submit_button = {'Button': {
    'image': None,
    'icon': 'FaCheckCircle',
    'text': 'submit',
    'color': 'white',
    'bgcolor': 'green',
    'value': 'submit'
}}

end_button = {'Button': {
    'image': None,
    'icon': 'FaStopCircle',
    'text': 'end',
    'color': 'white',
    'bgcolor': 'blue',
    'value': 'end'
}}

up_button = {'Button': {
    'image': None,
    'icon': 'FaArrowUp',
    'text': None,
    'color': 'black',
    'bgcolor': 'white',
    'value': 'up'
}}

down_button = {'Button': {
    'image': None,
    'icon': 'FaArrowDown',
    'text': None,
    'color': 'black',
    'bgcolor': 'white',
    'value': 'down'
}}

left_button = {'Button': {
    'image': None,
    'icon': 'FaArrowLeft',
    'text': None,
    'color': 'black',
    'bgcolor': 'white',
    'value': 'left'
}}

right_button = {'Button': {
    'image': None,
    'icon': 'FaArrowRight',
    'text': None,
    'color': 'black',
    'bgcolor': 'white',
    'value': 'right'
}}

standard_controls = [
    start_button,
    reset_button,
    end_button,
    left_button,
    right_button,
    up_button,
    down_button
]

brightness_slider = {'Slider': {
    'title': 'Brightness',
    'icon': 'BsFillBrightnessHighFill',
    'id': 'brightness',
    'min': 0,
    'max': 1000,
    'value': 100
}}

contrast_slider = {'Slider': {
    'title': 'Contrast',
    'icon': 'IoContrast',
    'id': 'contrast',
    'min': 0,
    'max': 500,
    'value': 100
}}

saturation_slider = {'Slider': {
    'title': 'Saturation',
    'icon': 'BsDropletHalf',
    'id': 'saturation',
    'min': 0,
    'max': 100,
    'value': 100
}}

hue_slider = {'Slider': {
    'title': 'Hue',
    'icon': 'IoColorPaletteOutline',
    'id': 'hue',
    'min': 0,
    'max': 360,
    'value': 0
}}

image_sliders = [brightness_slider, contrast_slider, saturation_slider, hue_slider]
