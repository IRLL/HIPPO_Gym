import json
import time

from browser.control_panel import ControlPanel
from browser.game_window import GameWindow
from event.event_handler import EventHandler
from browser.grid import Grid
from browser.info_panel import InfoPanel


class HippoGym:

    def __init__(self, pipe):
        self.game_window = None
        self.info_panel = None
        self.control_panel = None
        self.grid = None
        self.pipe = pipe
        self.userId, self.projectId = get_ids(pipe)
        self.run = False
        self.event_handler = EventHandler(self.pipe, self)
        self.go()

    def go(self):
        buttons = [{"Button": {"text": "start"}}]
        self.control_panel = ControlPanel(self.pipe, buttons=buttons, keys=True)
        sliders = [{"Slider":{"title": "slide me"}}]
        self.control_panel.update(sliders=sliders)
        self.game_window = GameWindow(self.pipe, width=300)
        self.control_panel.update()
        for i in range(20):
            print(self.event_handler.get())
            time.sleep(2)

    def get_game_window(self):
        if not self.game_window:
            self.game_window = GameWindow(self.pipe)
        return self.game_window

    def get_info_panel(self):
        if not self.info_panel:
            self.info_panel = InfoPanel(self.pipe)
        return self.info_panel

    def get_control_panel(self):
        if not self.control_panel:
            self.control_panel = ControlPanel(self.pipe)
        return self.control_panel

    def get_grid(self):
        if not self.grid:
            self.grid = Grid()
        return self.grid

    def get_event_handler(self):
        return self.event_handler

    def set_game_window(self, new_game_window):
        if type(new_game_window) == GameWindow:
            self.game_window = new_game_window

    def set_info_panel(self, new_info_panel):
        if type(new_info_panel) == InfoPanel:
            self.info_panel = new_info_panel

    def set_control_panel(self, new_control_panel):
        if type(new_control_panel) == ControlPanel:
            self.control_panel = new_control_panel

    def set_grid(self, new_grid):
        if type(new_grid) == Grid:
            self.grid  = new_grid

    def start(self):
        self.run = True

    def pause(self):
        self.run = False

    def stop(self):
        self.run = False

    def set_window_size(self, new_size):
        if self.game_window:
            self.game_window.set_size(new_size)

def get_ids(pipe):
    message = pipe.recv()
    userId = message.get("userId", None)
    projectId = message.get("projectId", None)
    return userId, projectId

