import base64
import json
import logging
from PIL import Image
from io import BytesIO

class GameWindow:

    def __init__(self, pipe, width, height, image):
        self.width = width
        self.height = height
        self.frame = image
        self.frameId = 0
        self.pipe = pipe
        self.send_window_size()
        self.send_frame()

    def update(self, width=None, height=None, image=None):
        if width:
            self.width = width
        if height:
            self.height = height
        if width or height:
            self.send_window_size()
        if image:
            if type(image) != str:
                self.frame = self.convert_numpy_array_to_base64(image)
            else:
                self.frame = image
            self.send_frame()

    def send_window_size(self):
        self.pipe.send(json.dumps({'gameWindowSize': (self.width, self.height)}))

    def send_frame(self):
        self.pipe.send(json.dumps({'frame': self.frame, 'frameId': self.frameId}))
        self.frameId += 1

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