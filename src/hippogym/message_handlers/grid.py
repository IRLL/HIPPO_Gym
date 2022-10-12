from typing import TYPE_CHECKING

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym.ui_elements.grid import Grid


class GridMessageHandler(MessageHandler):
    def __init__(self, grid: "Grid") -> None:
        super().__init__(EventsQueues.GRID)
        self.grid = grid
        self.handlers = {
            "TILESELECTED": self.select,
            "TILEUNSELECTED": self.unselect,
            "TILECLICKED": self.click,
        }

    def select(self, tile_data: str) -> None:
        self.grid.select(*tuple(tile_data))

    def unselect(self, tile_data: str) -> None:
        self.grid.unselect(*tuple(tile_data))

    def click(self, tile_data: str) -> None:
        self.grid.click(*tuple(tile_data))
