import os
import json
import time
from enum import Enum
from typing import List

import numpy as np

from App.message_handlers import MessageHandler
from App.utils import load_to_b64


class LibraryCommands(Enum):
    OPEN_LIBRARY = "library"
    BACK_TO_GAME = "back to game"
    NEXT_ITEM = "next library item"
    PREVIOUS_ITEM = "previous library item"

    def toJson(self) -> str:
        return self.value


class LibraryModes(Enum):
    NONE = "None"
    OPTIONS_GRAPHS = "options_graphs"


class LibraryHandler(MessageHandler):
    def __init__(self, trial) -> None:
        super().__init__(trial)

        library_mode = self.trial.config.get("library_mode", LibraryModes.NONE)
        self.library_mode = LibraryModes(library_mode)

        if self.library_mode is None:
            self.handle_command = super().handle_command
            self.trial.send_ui([])
            return

        game = self.trial.config.get("game")

        if self.library_mode == LibraryModes.OPTIONS_GRAPHS:
            images_path = os.path.join("images", game)
            filter_by_utility = self.trial.config.get("filter_by_utility")
            task_item_name = self.trial.config.get("task_item_name")
            rank_by_complexity = self.trial.config.get("rank_by_complexity")
            library_images_path = os.path.join(images_path, self.library_mode.value)

            images_filenames = os.listdir(library_images_path)
            images_filenames = filter_and_order_images(
                images_filenames, filter_by_utility, rank_by_complexity, task_item_name
            )

            self.images = self._load_images(images_path, images_filenames)
            self.images_icons = self._load_icons(images_path, images_filenames)

        self.library_on = False
        self.cursor = 0
        self.reset()
        self.reset_ui()

    def reset(self):
        self.start_time = time.time()
        self.history = []

    def send_render(self):
        self.trial.frame_id += 1
        self.trial.send_render(
            {
                "frame": self.images[self.cursor],
                "frameId": self.trial.frame_id,
                "borderColor": "orange",
            }
        )

    def reset_ui(self):
        default_ui = self.trial.config.get("ui")
        if self.library_mode == LibraryModes.OPTIONS_GRAPHS:
            ui_navigation = {
                "previousBlock": None,
                "currentBlock": None,
                "nextBlock": None,
            }
            self.trial.pipe.send(json.dumps(ui_navigation))
            if LibraryCommands.OPEN_LIBRARY.value not in default_ui:
                default_ui += [LibraryCommands.OPEN_LIBRARY.value]
        self.trial.send_ui(default_ui)

    def send_ui(self):
        if len(self.images) > 1:
            self.trial.pipe.send(json.dumps(self._build_ui_navigation()))
        self.trial.send_ui([LibraryCommands.BACK_TO_GAME.value])

    def handle_command(self, command: str):
        command = super().handle_command(command)

        try:
            command = LibraryCommands(command)
        except ValueError:
            return command

        if command in (LibraryCommands.OPEN_LIBRARY, LibraryCommands.BACK_TO_GAME):
            if self.library_on:
                self.trial.play = True
                self.reset_ui()
            else:
                self.trial.play = False
                self.send_render()
                self.send_ui()
            self.library_on = not self.library_on

        if command in (LibraryCommands.NEXT_ITEM, LibraryCommands.PREVIOUS_ITEM):
            self._update_cursor(command)
            self.send_render()
            self.send_ui()

        command_time = time.time() - self.start_time
        self.history.append((command, command_time))

    @property
    def _prev_item(self):
        return (self.cursor - 1) % len(self.images)

    @property
    def _next_item(self):
        return (self.cursor + 1) % len(self.images)

    def _build_ui_navigation(self) -> dict:
        return {
            "previousBlock": {
                "image": self.images_icons[self._prev_item],
                "value": "previous library item",
                "name": f"{self._prev_item + 1}/{len(self.images)}",
                "borderColor": "orange",
            },
            "currentBlock": {
                "image": self.images_icons[self.cursor],
                "value": "current library item",
                "name": f"{self.cursor + 1}/{len(self.images)}",
                "borderColor": "orange",
            },
            "nextBlock": {
                "image": self.images_icons[self._next_item],
                "value": "next library item",
                "name": f"{self._next_item + 1}/{len(self.images)}",
                "borderColor": "orange",
            },
        }

    def _update_cursor(self, command: LibraryCommands):
        if command == LibraryCommands.NEXT_ITEM:
            self.cursor = self._next_item
        elif command == LibraryCommands.PREVIOUS_ITEM:
            self.cursor = self._prev_item
        else:
            raise ValueError(
                f"Command {command} is not valid to update the library cursor."
            )

    def _load_images(self, images_path: str, images_filenames: List[str]):
        images = []
        for graph_name in images_filenames:
            img_path = os.path.join(images_path, self.library_mode.value, graph_name)
            images.append(load_to_b64(img_path))
        return images

    def _load_icons(self, images_path: str, images_filenames: List[str]):
        options_names = [name.split("-")[3] for name in images_filenames]
        images_icons = []
        for options_name in options_names:
            img_path = os.path.join(images_path, "options_icons", options_name)
            images_icons.append(load_to_b64(img_path))
        return images_icons


def filter_and_order_images(
    images_filenames: List[str],
    filter_by_utility: bool,
    rank_by_complexity: bool,
    task_item_name: str,
):
    images_filenames = np.array(images_filenames)

    if filter_by_utility:
        pass
    # TODO Fix this
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

    return images_filenames
