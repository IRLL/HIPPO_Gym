import os
import time
import numpy as np
from PIL import Image
import _pickle as cPickle

from message_handler import MessageHandler
from utils import array_to_b64, alpha_to_color

class LibraryHandler(MessageHandler):

    def __init__(self, trial, filter_by_utility:bool=True, rank_by_complexity:bool=True,
            task_number:int=None) -> None:
        super().__init__(trial)
        self.library_on = False

        graphs_path = os.path.join('images', 'options_graphs')
        options_filenames = np.array(os.listdir(graphs_path))

        if filter_by_utility:
            if task_number is None:
                raise ValueError("Argument 'task_number' should be specified "
                                 "when 'filter_by_utility'=True.")
            is_useful = np.array(
                [int(name.split('-')[2][task_number]) for name in options_filenames], dtype=bool)
            options_filenames = options_filenames[is_useful]

        if rank_by_complexity:
            complexities = np.array(
                [name.split('-')[1] for name in options_filenames], dtype=np.float32)
            options_filenames = options_filenames[np.argsort(complexities)]
        else:
            options_filenames = np.random.permutation(options_filenames)

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
        self.history = []

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
