
class HippoGym:

    def __int__(self):
        self.game_window = None
        self.info_panel = None
        self.control_panel = None
        self.grid = None

    def create_game_window(self, width=None, height=None, image=None):
        self.game_window =  GameWindow(pipe, width, height, image)
        return self.game_window

    def create_info_panel(self):
        self.info_panel = InfoPanel()
        return self.info_panel

    def create_control_panel(self):
        self.control_panel = ControlPanel()
        return self.control_panel

    def create_grid(self):
        self.grid = Grid()
        return self.grid