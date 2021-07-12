import os
import time
import numpy as np
from PIL import Image
import _pickle as cPickle

from message_handler import MessageHandler
from utils import array_to_b64, alpha_to_color

class LibraryHandler(MessageHandler):

    def __init__(self, trial, options:list=None) -> None:
        super().__init__(trial)
        self.library_on = False

        graphs_path = os.path.join('images', 'options_graphs')
        options_filenames = os.listdir(graphs_path)
        complexities = np.array([name.split('-')[1] for name in options_filenames], dtype=np.float32)
        ranks = np.argsort(complexities)
        options_filenames = np.array(options_filenames)[ranks]

        self.images = [
            array_to_b64(np.array(
                alpha_to_color(Image.open(os.path.join(graphs_path, graph_name))
            )))
            for graph_name in options_filenames
        ]
        self.cursor = 0
        self.reset()

    def reset(self):
        self.start_time = time.time()
        self.history = [('start', self.start_time)]

    def send_render(self):
        self.trial.frameId += 1
        self.trial.send_render({'frame': self.images[self.cursor], 'frameId': self.trial.frameId})

    def handle_command(self, command: str):
        command = super().handle_command(command)
        if command in ('librairy', 'back to game'):
            if self.library_on:
                self.trial.play = True
                self.trial.send_ui()
            else:
                self.trial.play = False
                self.send_render()
                ui = ['next librairy item', 'previous librairy item', 'back to game']
                self.trial.send_ui(ui)
            self.library_on = not self.library_on

        if command == 'next librairy item':
            self.cursor = (self.cursor + 1) % len(self.images)
            self.send_render()
        elif command == 'previous librairy item':
            self.cursor = (self.cursor - 1) % len(self.images)
            self.send_render()

        if command in ('librairy', 'back to game', 'next librairy item', 'previous librairy item'):
            command_time = time.time() - self.start_time
            self.history.append((command, command_time))

        return command
