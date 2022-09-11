""" HippoGym: A framework for human-in-the-loop experiments. """

import time
from logging import getLogger
from multiprocessing import Process, Queue

from hippogym.browser.control_panel import ControlPanel
from hippogym.browser.game_window import GameWindow
from hippogym.browser.grid import Grid
from hippogym.browser.info_panel import InfoPanel
from hippogym.browser.text_box import TextBox

from hippogym.bucketer import bucketer
from hippogym.communicator.communicator import Communicator

from hippogym.queue_handler import check_queue, check_queues
from hippogym.recorder.recorder import Recorder

from hippogym.message_handlers import (
    ControlMessageHandler,
    GridMessageHandler,
    TextBoxMessageHandler,
    WindowMessageHandler,
)

LOGGER = getLogger(__name__)


class HippoGym:
    def __init__(self):
        self.game_windows = []
        self.info_panel = None
        self.control_panel = None
        self.text_boxes = []
        self.grid = None
        self.run = False
        self.stop = False
        self.user_id = None
        self.project_id = None
        self.recorders = []
        self.queues = create_queues()
        self.out_q = Queue()
        self.communicator = Communicator(
            self.out_q,
            self.queues,
            address=None,
            port=5000,
            use_ssl=True,
            force_ssl=False,
            fullchain_path="fullchain.pem",
            privkey_path="privkey.pem",
        )
        self.communicator.start()
        self.control_message_handler = ControlMessageHandler(self)
        self.control_message_handler.start()
        self.window_message_handler = None
        self.textbox_message_handler = None
        self.grid_message_handler = None

    def add_recorder(self, **kwargs):
        recorder = Recorder(self, **kwargs)
        self.recorders.append(Recorder)
        return recorder

    def get_recorder(self, index=0):
        if len(self.recorders) > index:
            return self.recorders[index]
        else:
            return self.add_recorder()

    def add_text_box(self, text_box=None, **kwargs):
        if not isinstance(text_box, TextBox):
            text_box = TextBox(self.out_q, idx=len(self.text_boxes), **kwargs)
        self.text_boxes.append(text_box)
        if not self.textbox_message_handler:
            self.textbox_message_handler = TextBoxMessageHandler(self)
            self.textbox_message_handler.start()
        return text_box

    def add_game_window(self, game_window=None, **kwargs):
        if not isinstance(game_window, GameWindow):
            game_window = GameWindow(self.out_q, idx=len(self.game_windows), **kwargs)
        self.game_windows.append(game_window)
        if not self.window_message_handler:
            self.window_message_handler = WindowMessageHandler(self)
            self.window_message_handler.start()
        return game_window

    def get_game_window(self, index=0):
        if len(self.game_windows) < index:
            game_window = None
        elif len(self.game_windows) == index:
            game_window = self.add_game_window()
        else:
            game_window = self.game_windows[index]
        return game_window

    def get_info_panel(self):
        if not self.info_panel:
            self.info_panel = InfoPanel(self.out_q)
        return self.info_panel

    def get_control_panel(self):
        if not self.control_panel:
            self.control_panel = ControlPanel(self.out_q)
        return self.control_panel

    def add_grid(self, grid=None, **kwargs):
        if not isinstance(grid, Grid):
            self.grid = Grid(self.out_q, **kwargs)
        self.grid_message_handler = GridMessageHandler(self)
        self.grid_message_handler.start()

    def get_grid(self, **kwargs):
        if not self.grid:
            self.add_grid(**kwargs)
        return self.grid

    def set_game_window(self, new_game_window, index):
        if type(new_game_window) == GameWindow and len(self.game_windows) <= index + 1:
            new_game_window.update(id=index)
            self.game_windows[index] = new_game_window

    def set_info_panel(self, new_info_panel):
        if type(new_info_panel) == InfoPanel:
            self.info_panel = new_info_panel

    def set_control_panel(self, new_control_panel):
        if type(new_control_panel) == ControlPanel:
            self.control_panel = new_control_panel

    def set_grid(self, new_grid):
        if type(new_grid) == Grid:
            self.grid = new_grid

    def start(self):
        self.stop = False
        self.run = True

    def pause(self):
        self.run = False

    def end(self):
        self.run = False
        self.stop = True

    def disconnect(self):
        self.out_q.put_nowait("done")
        self.__init__(False)

    def set_window_size(self, new_size, index):
        if len(self.game_windows) > index:
            self.game_windows[index].set_size(new_size)

    def group(self, num_groups):
        return bucketer(self.user_id, num_groups)

    def poll(self):
        control = []  # self.handle_control_messages()
        window = []  # self.handle_window_messages()
        messages = check_queues(
            [
                self.queues["keyboard_q"],
                self.queues["button_q"],
                self.queues["standard_q"],
            ]
        )
        for message in window:
            messages.append(message)
        for message in control:
            messages.append(message)
        return messages

    def send(self):
        for window in self.game_windows:
            window.send()
        for text_box in self.text_boxes:
            text_box.send()
        if self.control_panel:
            self.control_panel.send()
        if self.grid:
            self.grid.send()
        if self.info_panel:
            self.info_panel.send()

    def standby(self, function=None):
        while len(self.communicator.users) == 0:
            time.sleep(0.01)
        if function:
            function(self)


def create_queues():
    keys = [
        "keyboard_q",
        "window_q",
        "button_q",
        "standard_q",
        "control_q",
        "textbox_q",
        "grid_q",
    ]
    queues = {}
    for key in keys:
        queues[key] = Queue()
    return queues
