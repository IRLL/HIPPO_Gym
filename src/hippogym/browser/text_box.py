import time


class TextBox:

    def __init__(self, queue, idx=0, width=700, height=600, mode='responsive', text=None, editable=True,
                 bgcolor='white', color='black', font=None, syntax=None, buttons=None):
        self.queue = queue
        self.id = idx
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
        self.send()

    def send(self):
        text_box = {'TextBox': {
            'idx': self.id,
            'size': (self.width, self.height),
            'mode': self.mode,
            'text': self.text,
            'editable': self.editable,
            'bgcolor': self.bgcolor,
            'color': self.color,
            'font': self.font,
            'syntax': self.syntax,
            'buttons': self.buttons
        }}
        self.queue.put_nowait(text_box)

    def hide(self):
        self.queue.put_nowait({'TextBox': None})

    def request(self):
        request = {'Request': ['TEXTBOX', self.id]}
        self.queue.put_nowait(request)
        self.updated = False

    def update(self, **kwargs):
        if kwargs.get('idx', None):
            self.id = kwargs.get('idx')
        if kwargs.get('width', None):
            self.width = kwargs.get('width')
        if kwargs.get('height', None):
            self.height = kwargs.get('height')
        if kwargs.get('mode', None):
            self.mode = kwargs.get('mode')
        if kwargs.get('text', None):
            self.update_buffer()
            self.text = kwargs.get('text')
        if kwargs.get('editable', None):
            self.editable = kwargs.get('editable')
        if kwargs.get('bgcolor', None):
            self.bgcolor = kwargs.get('bgcolor')
        if kwargs.get('color', None):
            self.color = kwargs.get('color')
        if kwargs.get('font', None):
            self.font = kwargs.get('font')
        if kwargs.get('syntax', None):
            self.syntax = kwargs.get('syntax')
        if kwargs.get('buttons', None):
            self.buttons = kwargs.get('buttons')
        if kwargs.get('send', True):
            self.send()
        self.updated = True

    def clear(self, text=None):
        self.update(text=text)
        self.update_buffer()
        self.text = ''

    def update_buffer(self):
        self.text_buffer.append(self.text)
        if len(self.text_buffer) > 10:
            self.text_buffer.pop(0)

    def get_text(self):
        while not self.updated:
            time.sleep(0.1)
        return self.text
