from typing import TYPE_CHECKING, Dict

from hippogym.event_handler import EventsQueues
from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:

    from multiprocessing import Queue

    from hippogym.ui_elements.grid import Grid, Tile


class GridMessageHandler(MessageHandler):
    def __init__(self, grid: "Grid", queues: Dict[EventsQueues, "Queue"]) -> None:
        super().__init__(queues, EventsQueues.GRID)
        self.grid = grid
        self.handlers = {
            "TILESELECTED": self.select,
            "TILEUNSELECTED": self.unselect,
            "TILECLICKED": self.click,
        }

    def select(self, tile_data: str) -> None:
        tile = Tile(*tuple(tile_data))
        self.grid.select(tile)

    def unselect(self, tile_data: str) -> None:
        tile = Tile(*tuple(tile_data))
        self.grid.unselect(tile)

    def click(self, tile_data: str) -> None:
        tile = Tile(*tuple(tile_data))
        self.grid.click(tile)
