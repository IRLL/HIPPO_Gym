import json
import logging


class Fingerprint:
    def __int__(self, pipe):
        self.pipe = pipe

    def send_label(self, label):
        self.send({"label": label})

    def send_feedback(self, feedback):
        self.send({"feedback": feedback})

    def send(self, message: dict):
        self.pipe.send(json.dumps(message))
