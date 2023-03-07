import logging
import time

from hippogym import HippoGym
from hippogym.ui_elements import ControlPanel, InfoPanel, Grid, standard_controls
from hippogym.trialsteps import InteractiveStep

logging.basicConfig(level=10)


class GridStep(InteractiveStep):
    def __init__(self) -> None:
        self.grid = Grid(rows=41, columns=42)
        self.grid.tiles[20][21].text = "Hello"
        self.control_panel = ControlPanel(standard_controls)
        self.info = InfoPanel()
        super().__init__([self.grid, self.control_panel, self.info])

    def run(self) -> None:
        done = False
        while not done:
            for item in self.poll():
                button = item.get("BUTTONPRESSED", "")
                if button.lower() in ("next", "end"):
                    done = True
            self.info.update(
                text=f"Selected Tiles: {str(self.grid.selected_tiles_list)}"
            )
            time.sleep(1)


def build_experiment():
    return HippoGym(GridStep())


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
