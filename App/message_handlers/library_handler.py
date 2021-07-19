import os
import time
import numpy as np
from PIL import Image
import _pickle as cPickle

from App.message_handlers import MessageHandler
from App.utils import array_to_b64, alpha_to_color

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

    def _prev_item(self):
        return (self.cursor - 1) % len(self.images)

    def _next_item(self):
        return (self.cursor + 1) % len(self.images)

    def send_ui(self):
        ui = [
            f'next library item ({self._next_item() + 1}/{len(self.images)})',
            f'previous library item ({self._prev_item() + 1}/{len(self.images)})',
            'back to game'
        ]
        self.trial.send_ui(ui)

    def handle_command(self, command: str):
        command = super().handle_command(command)
        
        if command in ('library', 'back to game'):
            if self.library_on:
                self.trial.play = True
                self.trial.send_ui()
            else:
                self.trial.play = False
                self.send_render()
                self.send_ui()
            self.library_on = not self.library_on

        if command.startswith('next library item'):
            self.cursor = self._next_item()
            self.send_render()
            self.send_ui()
        elif command.startswith('previous library item'):
            self.cursor = self._prev_item()
            self.send_render()
            self.send_ui()

        if command in ('library', 'back to game', 'next library item', 'previous library item'):
            command_time = time.time() - self.start_time
            self.history.append((command, command_time))

        return command
