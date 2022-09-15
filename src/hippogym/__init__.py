""" HippoGym: A framework for human-in-the-loop experiments. """

import time
from logging import getLogger
from multiprocessing import Process, Queue
from typing import Callable, Dict, List, Optional, Tuple

from hippogym.ui_elements.control_panel import ControlPanel
from hippogym.ui_elements.game_window import GameWindow
from hippogym.ui_elements.grid import Grid
from hippogym.ui_elements.info_panel import InfoPanel
from hippogym.ui_elements.text_box import TextBox

from hippogym.bucketer import bucketer
from hippogym.communicator.communicator import Communicator

from hippogym.queue_handler import check_queues
from hippogym.recorder.recorder import Recorder

from hippogym.message_handlers import (
    ControlMessageHandler,
    GridMessageHandler,
    TextBoxMessageHandler,
    WindowMessageHandler,
)

LOGGER = getLogger(__name__)


class HippoGym:
    def __init__(self) -> None:
        self.game_windows: List[GameWindow] = []
        self.info_panel: InfoPanel = None
        self.control_panel: Optional[ControlPanel] = None
        self.text_boxes: List[TextBox] = []
        self.grid: Optional[Grid] = None
        self.run = False
        self.stop = False
        self.user_id: Optional[str] = None
        self.project_id = None
        self.recorders: List[Recorder] = []
        self.queues = create_queues()
        self.out_q = Queue()
        self.communicator = Process(
            target=Communicator,
            args=(
                self.out_q,
                self.queues,
            ),
            kwargs={
                "address": "localhost",
                "port": 5000,
                "use_ssl": True,
                "force_ssl": False,
                "fullchain_path": "fullchain.pem",
                "privkey_path": "privkey.pem",
            },
            daemon=True,
        )
        self.communicator.start()

        self.control_message_handler = ControlMessageHandler(self)
        self.control_message_handler.start()

        self.window_message_handler = None
        self.textbox_message_handler = None
        self.grid_message_handler: Optional[GridMessageHandler] = None

    def add_recorder(self, **kwargs):
        recorder = Recorder(self, **kwargs)
        self.recorders.append(Recorder)
        return recorder

    def get_recorder(self, index=0):
        if len(self.recorders) > index:
            return self.recorders[index]
        else:
            return self.add_recorder()

    def add_text_box(self, text_box=None, **kwargs) -> TextBox:
        if not isinstance(text_box, TextBox):
            text_box = TextBox(self.out_q, idx=len(self.text_boxes), **kwargs)
        self.text_boxes.append(text_box)
        if not self.textbox_message_handler:
            self.textbox_message_handler = TextBoxMessageHandler(self)
            self.textbox_message_handler.start()
        return text_box

    def add_game_window(self, game_window=None, **kwargs) -> GameWindow:
        if not isinstance(game_window, GameWindow):
            game_window = GameWindow(self.out_q, idx=len(self.game_windows), **kwargs)
        self.game_windows.append(game_window)
        if not self.window_message_handler:
            self.window_message_handler = WindowMessageHandler(self)
            self.window_message_handler.start()
        return game_window

    def get_game_window(self, index=0) -> GameWindow:
        if len(self.game_windows) < index:
            game_window = None
        elif len(self.game_windows) == index:
            game_window = self.add_game_window()
        else:
            game_window = self.game_windows[index]
        return game_window

    def get_info_panel(self) -> InfoPanel:
        if not self.info_panel:
            self.info_panel = InfoPanel(self.out_q)
        return self.info_panel

    def get_control_panel(self) -> ControlPanel:
        if not self.control_panel:
            self.control_panel = ControlPanel(self.out_q)
        return self.control_panel

    def add_grid(self, rows: int = 10, columns: int = 10) -> Grid:
        if self.grid is None:
            self.grid = Grid(self.out_q, rows=rows, columns=columns)
            self.grid_message_handler = GridMessageHandler(self)
            self.grid_message_handler.start()
        return self.grid

    def get_grid(self, **kwargs) -> Grid:
        if not self.grid:
            self.grid = self.add_grid(**kwargs)
        return self.grid

    def set_game_window(self, game_window: GameWindow, index: int) -> None:
        if not isinstance(game_window, GameWindow):
            raise TypeError("Given game_window must subclass GameWindow")
        if len(self.game_windows) <= index + 1:
            game_window.update(idx=index)
            self.game_windows[index] = game_window

    def set_info_panel(self, info_panel: InfoPanel) -> None:
        if not isinstance(info_panel, InfoPanel):
            raise TypeError("Given info_panel must subclass InfoPanel")
        self.info_panel = info_panel

    def set_control_panel(self, control_panel: ControlPanel) -> None:
        if not isinstance(control_panel, ControlPanel):
            raise TypeError("Given control_panel must subclass ControlPanel")
        self.control_panel = control_panel

    def set_grid(self, grid: Grid) -> None:
        if isinstance(grid, Grid):
            self.grid = grid

    def start(self) -> None:
        self.stop = False
        self.run = True

    def pause(self) -> None:
        self.run = False

    def end(self) -> None:
        self.run = False
        self.stop = True

    def disconnect(self) -> None:
        self.out_q.put_nowait("done")
        # self.__init__(False)  # Need an alternative to this

    def set_window_size(self, new_size: Tuple[int, int], index: int) -> None:
        if len(self.game_windows) > index:
            self.game_windows[index].set_size(new_size)

    def group(self, num_groups: int) -> int:
        if self.user_id is None:
            raise TypeError("User must not be None in order to get user group.")
        return bucketer(self.user_id, num_groups)

    def poll(self) -> List[str]:
        return check_queues(
            [
                self.queues["keyboard_q"],
                self.queues["button_q"],
                self.queues["standard_q"],
            ]
        )

    def send(self) -> None:
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

    def standby(self, function: Optional[Callable] = None) -> None:
        time_printer = TimeActor(lambda: LOGGER.debug("HippoGym in standby"), 2)
        while self.user_id is None:
            time.sleep(0.01)
            time_printer.tick()

        if function:
            function(self)


class TimeActor:
    def __init__(self, func: Callable[[None], None], interval: float) -> None:
        self.start_time = time.time()
        self.last_tick = self.start_time
        self.interval = interval
        self.func = func

    def tick(self):
        now = time.time()
        delta = now - self.last_tick
        if delta >= self.interval:
            self.last_tick = time.time()
            self.func()


def create_queues() -> Dict[str, Queue]:
    keys = [
        "keyboard_q",
        "window_q",
        "button_q",
        "standard_q",
        "control_q",
        "textbox_q",
        "grid_q",
    ]
    queues: Dict[str, Queue] = {}
    for key in keys:
        queues[key] = Queue()
    return queues
