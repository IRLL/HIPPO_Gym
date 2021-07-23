import base64
import logging
from PIL import Image
from io import BytesIO


class GameWindow:

    def __init__(self, pipe, width=700, height=600, mode='responsive', image=None, text=None):
        self.width = width
        self.height = height
        self.mode = mode
        self.frame = image
        self.text = text
        self.frameId = 0
        self.pipe = pipe
        self.send_window_size()
        self.send_frame()

    def update(self, width=None, height=None, mode=None, image=None, text=None):
        if width:
            self.width = width
        if height:
            self.height = height
        if mode:
            self.mode = mode
        if width or height or mode:
            self.send_window_size()
        if text:
            self.text = text
            self.frame = None
        if image:
            if type(image) != str:
                self.frame = self.convert_numpy_array_to_base64(image)
            else:
                self.frame = image
            self.text = None
        if text or image:
            self.send_frame()

    def send_window_size(self):
        message = {"GameWindow": {"size": (self.width, self.height), "mode": self.mode}}
        self.send(message)

    def send_frame(self):
        message = None
        if self.frame:
            message = {"GameWindow": {"frame": self.frame, "frameId": self.frameId}}
        elif self.text:
            message = {"GameWindow": {"text": self.text, "frameId": self.frameId}}
        if message:
            self.send(message)
            self.frameId += 1

    def send(self, message):
        self.pipe.send(message)

    def set_size(self, size):
        self.width = size[0]
        self.height = size[1]

    # TODO: add functionality for RGBA array not just RGB
    def convert_numpy_array_to_base64(self, array):
        try:
            img = Image.fromarray(array)
            fp = BytesIO()
            img.save(fp, 'JPEG')
            frame = base64.b64encode(fp.getvalue()).decode('utf-8')
            fp.close()
            return frame
        except Exception as e:
            logging.info('Failed to convert numpy array to Base64')
            logging.info(f'Numpy Array conversion error: {e}')
