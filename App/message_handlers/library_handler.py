import os
import json
import time
import numpy as np

from App.message_handlers import MessageHandler
from App.utils import load_to_b64


class LibraryHandler(MessageHandler):
    def __init__(self, trial) -> None:
        super().__init__(trial)

        library_mode = self.trial.config.get("library_mode")
        self.library_mode = library_mode

        if self.library_mode is None:
            self.handle_command = super().handle_command
            self.trial.send_ui([])
            return

        filter_by_utility = self.trial.config.get("filter_by_utility")
        rank_by_complexity = self.trial.config.get("rank_by_complexity")
        task_item_name = self.trial.config.get("task_item_name")
        game = self.trial.config.get("game")

        images_path = os.path.join("images", game)
        images_filenames = np.array(os.listdir(os.path.join(images_path, library_mode)))

        # TODO Fix this
        # if filter_by_utility:
        #     is_useful = np.array(
        #         [int(name.split("-")[2][task_number]) for name in images_filenames],
        #         dtype=bool,
        #     )
        #     images_filenames = images_filenames[is_useful]

        if rank_by_complexity:
            complexities = np.array(
                [name.split("-")[1] for name in images_filenames], dtype=np.float32
            )
            images_filenames = images_filenames[np.argsort(complexities)]
        else:
            permuted_indexes = np.random.permutation(np.arange(len(images_filenames)))
            images_filenames = images_filenames[permuted_indexes]

        self.images = []
        for graph_name in images_filenames:
            img_path = os.path.join(images_path, library_mode, graph_name)
            self.images.append(load_to_b64(img_path))

        if self.library_mode == "options_graphs":
            options_names = [name.split("-")[3] for name in images_filenames]
            self.images_icons = []
            for options_name in options_names:
                img_path = os.path.join(images_path, "options_icons", options_name)
                self.images_icons.append(load_to_b64(img_path))

        self.library_on = False
        self.cursor = 0
        self.reset()
        self.reset_ui()

    def reset(self):
        self.start_time = time.time()
        self.history = []

    def send_render(self):
        self.trial.frameId += 1
        self.trial.send_render(
            {
                "frame": self.images[self.cursor],
                "frameId": self.trial.frameId,
                "borderColor": "orange",
            }
        )

    def _prev_item(self):
        return (self.cursor - 1) % len(self.images)

    def _next_item(self):
        return (self.cursor + 1) % len(self.images)

    def reset_ui(self):
        if self.library_mode == "options_graphs":
            ui_navigation = {
                "previousBlock": None,
                "currentBlock": None,
                "nextBlock": None,
            }
            self.trial.pipe.send(json.dumps(ui_navigation))
        default_ui = self.trial.config.get("ui")
        if "library" not in default_ui:
            default_ui += ["library"]
        self.trial.send_ui(default_ui)

    def send_ui(self):
        if len(self.images) > 1:
            ui_navigation = {
                "previousBlock": {
                    "image": self.images_icons[self._prev_item()],
                    "value": "previous library item",
                    "name": f"{self._prev_item() + 1}/{len(self.images)}",
                    "borderColor": "orange",
                },
                "currentBlock": {
                    "image": self.images_icons[self.cursor],
                    "value": "current library item",
                    "name": f"{self.cursor + 1}/{len(self.images)}",
                    "borderColor": "orange",
                },
                "nextBlock": {
                    "image": self.images_icons[self._next_item()],
                    "value": "next library item",
                    "name": f"{self._next_item() + 1}/{len(self.images)}",
                    "borderColor": "orange",
                },
            }
            self.trial.pipe.send(json.dumps(ui_navigation))
        self.trial.send_ui(["back to game"])

    def handle_command(self, command: str):
        command = super().handle_command(command)

        if command in ("library", "back to game"):
            if self.library_on:
                self.trial.play = True
                self.reset_ui()
            else:
                self.trial.play = False
                self.send_render()
                self.send_ui()
            self.library_on = not self.library_on

        if command.startswith("next library item"):
            self.cursor = self._next_item()
            self.send_render()
            self.send_ui()
        elif command.startswith("previous library item"):
            self.cursor = self._prev_item()
            self.send_render()
            self.send_ui()

        if command in (
            "library",
            "back to game",
            "next library item",
            "previous library item",
        ):
            command_time = time.time() - self.start_time
            self.history.append((command, command_time))

        return command
