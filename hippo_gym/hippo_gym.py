
class HippoGym:

    def __int__(self):
        self.game_window = None
        self.info_panel = None
        self.control_panel = None
        self.grid = None

    def create_info_panel(self):
        self.info_panel = InfoPanel()
        return self.info_panel

    def create_control_panel(self):
        self.control_panel = ControlPanel()
        return self.control_panel

    def create_grid(self):
        self.grid = Grid()
        return self.grid