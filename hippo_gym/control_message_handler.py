import time
from threading import Thread

from hippo_gym.queue_handler import check_queue


class ControlMessageHandler(Thread):
    def __init__(self, hippo):
        Thread.__init__(self, daemon=True)
        self.hippo = hippo
        print("CONTROL ME")

        self.handlers = {
            'userId': self.user,
            'projectId': self.project,
            'disconnect': self.disconnect,
            'SLIDERSET': self.slider,
            'start': self.hippo.start,
            'pause': self.hippo.pause,
            'end': self.hippo.end
        }

    def run(self):
        while True:
            messages = check_queue(self.hippo.queues['control_q'])
            for message in messages:
                print(message)
                for key in message.keys():
                    if key in self.handlers:
                        self.handlers[key](message[key])
            time.sleep(0.01)

    def user(self, user_id):
        if not self.hippo.user_connected:
            self.hippo.user_id = user_id
            self.hippo.user_connected = True
            self.hippo.send()

    def project(self, project_id):
        self.hippo.project_id = project_id

    def disconnect(self, user_id):
        self.hippo.user_connected = False
        self.hippo.user_id = None

    def slider(self, setting):
        if self.hippo.control_panel:
            self.hippo.control_panel.set_slider_value(*setting)
