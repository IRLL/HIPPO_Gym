from typing import TYPE_CHECKING, Tuple

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
        self.grid.select(*read_tile_data(tile_data))

    def unselect(self, tile_data: str) -> None:
        self.grid.unselect(*read_tile_data(tile_data))

    def click(self, tile_data: str) -> None:
        self.grid.click(*read_tile_data(tile_data))


def read_tile_data(tile_data: str) -> Tuple[int, int]:
    row, column = tuple(tile_data)
    return int(row), int(column)
