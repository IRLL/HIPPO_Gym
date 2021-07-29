import time
import asyncio

from browser.control_panel import ControlPanel
from browser.game_window import GameWindow
from event.event_handler import EventHandler
from browser.grid import Grid
from browser.info_panel import InfoPanel
from multiprocessing import Process, Queue
from communicator.communicator import Communicator


class HippoGym:

    def __init__(self):
        self.game_windows = []
        self.info_panel = None
        self.control_panel = None
        self.grid = None
        self.run = False
        self.userId = None
        self.projectId = None
        self.queues = create_queues()
        self.communicator = Process(target=Communicator, args=(self.queues,))
        self.communicator.start()
        self.event_handler = EventHandler(self.pipe, self)

    async def go(self):
        print("starting")
        #while not self.userId:
            #print('waiting')
            #time.sleep(2)
        buttons = [{"Button": {"text": "start"}}]
        self.control_panel = ControlPanel(self.pipe, buttons=buttons, keys=True)
        sliders = [{"Slider": {"title": "slide me"}}]
        self.control_panel.update(sliders=sliders)
        self.add_game_window()
        self.control_panel.update()
        for i in range(20):
            # print(self.event_handler.get())
            time.sleep(2)

    def add_game_window(self, game_window=None):
        if not type(game_window) == GameWindow:
            game_window = GameWindow(self.pipe, idx=len(self.game_windows))
        self.game_windows.append(game_window)

    def get_game_window(self, index):
        if len(self.game_windows) < index:
            game_window = None
        else:
            game_window = self.game_windows[index]
        return game_window

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


async def get_ids(pipe):
    print("getting ids")
    message = pipe.get()
    print(message)
    print('fidget')
    userId = message.get("userId", None)
    projectId = message.get("projectId", None)
    return userId, projectId

async def doit(hg):
    print("doit")
    print(hg.userId)
    hg.userId, hg.projectId = await get_ids(hg.idQ)
    print(hg.userId)

def main():
    hg = HippoGym()
    time.sleep(10)
    asyncio.get_event_loop().run_until_complete(doit(hg))
    asyncio.get_event_loop().run_forever()
    asyncio.get_event_loop().run_until_complete(hg.go())
    asyncio.get_event_loop().run_forever()

def create_queues():
    keys = ['up_q', 'keyboard_q', 'window_1_q', 'window_2_q', 'window_3_q', 'button_q', 'standard_q', 'flow_q']
    queues = {}
    for key in keys:
        queues[key] = Queue()
    return queues
main()
