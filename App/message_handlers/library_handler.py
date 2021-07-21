import os
import time
import numpy as np
from PIL import Image

from App.message_handlers import MessageHandler
from App.utils import array_to_b64, alpha_to_color

class LibraryHandler(MessageHandler):

    def __init__(self, trial) -> None:
        super().__init__(trial)

        library_mode = self.trial.config.get('library_mode')

        if library_mode is None:
            self.handle_command = super().handle_command
            return

        filter_by_utility = self.trial.config.get('filter_by_utility')
        rank_by_complexity = self.trial.config.get('rank_by_complexity')
        task_number = self.trial.config.get('task_number')
        domain = self.trial.config.get('domain')

        images_path = os.path.join('images', domain, library_mode)
        images_filenames = np.array(os.listdir(images_path))

        if filter_by_utility:
            if task_number is None:
                raise ValueError("Argument 'task_number' should be specified when"
                                 " 'library_mode'='options_graphs' and 'filter_by_utility'=True.")
            is_useful = np.array(
                [int(name.split('-')[2][task_number]) for name in images_filenames], dtype=bool)
            images_filenames = images_filenames[is_useful]

        if rank_by_complexity:
            complexities = np.array(
                [name.split('-')[1] for name in images_filenames], dtype=np.float32)
            images_filenames = images_filenames[np.argsort(complexities)]
        else:
            images_filenames = np.random.permutation(images_filenames)

        self.images = [
            array_to_b64(np.array(
                alpha_to_color(Image.open(os.path.join(images_path, graph_name))
            )))
            for graph_name in images_filenames
        ]

        self.library_on = False
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
        ui = []
        if len(self.images) > 1:
            ui += [
                f'next library item ({self._next_item() + 1}/{len(self.images)})',
                f'previous library item ({self._prev_item() + 1}/{len(self.images)})',
            ]
        ui += ['back to game']
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
