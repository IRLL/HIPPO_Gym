import time

from hippo_gym.browser.control_panel import ControlPanel
from hippo_gym.browser.game_window import GameWindow
from hippo_gym.browser.grid import Grid
from hippo_gym.browser.info_panel import InfoPanel
from multiprocessing import Process, Queue
from hippo_gym.communicator.communicator import Communicator
from hippo_gym.queue_handler import check_queue, check_all_queues


class HippoGym:

    def __init__(self):
        self.game_windows = []
        self.info_panel = None
        self.control_panel = None
        self.grid = None
        self.run = False
        self.user_id = None
        self.project_id = None
        self.user_connected = False
        self.queues = create_queues()
        self.out_q = Queue()
        self.communicator = Process(target=Communicator, args=(self.out_q, self.queues,))
        self.communicator.start()

    def add_game_window(self, game_window=None):
        if not type(game_window) == GameWindow:
            game_window = GameWindow(self.out_q, idx=len(self.game_windows))
        self.game_windows.append(game_window)
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

    def get_grid(self):
        if not self.grid:
            self.grid = Grid()
        return self.grid

    def get_event_handler(self):
        return self.event_handler

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
        self.run = True

    def pause(self):
        self.run = False

    def stop(self):
        self.run = False

    def set_window_size(self, new_size, index):
        if len(self.game_windows) > index:
            self.game_windows[index].set_size(new_size)

    def poll(self):
        messages = check_all_queues(self.queues)
        if messages:
            print(self.user_id, messages)
        return messages

    def standby(self):
        while not self.user_connected:
            time.sleep(0.01)
            self.user_id, self.project_id = get_ids(self.queues['flow_q'])
            if self.user_id:
                self.user_connected = True
        return self.user_id


def get_ids(flow_q):
    message = check_queue(flow_q)
    if message:
        user_id = message.get("userId", None)
        project_id = message.get("projectId", None)
        return user_id, project_id
    return None, None


def main():
    hg = HippoGym()
    while not hg.user_id:
        time.sleep(2)
        hg.user_id, hg.project_id = get_ids(hg.queues['flow_q'])
    print(f'starting with user: {hg.user_id}')
    buttons = [{"Button": {"text": "start"}}]
    hg.control_panel = ControlPanel(hg.out_q, buttons=buttons, keys=True)
    sliders = [{"Slider": {"title": "slide me"}}]
    hg.control_panel.update(sliders=sliders)
    hg.add_game_window()
    hg.control_panel.update()
    for i in range(2000):
        hg.poll()
        time.sleep(0.01)


def create_queues():
    keys = ['keyboard_q', 'window_q', 'button_q', 'standard_q', 'flow_q']
    queues = {}
    for key in keys:
        queues[key] = Queue()
    return queues


