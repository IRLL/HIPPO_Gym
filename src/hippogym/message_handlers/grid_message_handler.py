from typing import TYPE_CHECKING

from hippogym.message_handlers.message_handler import MessageHandler

if TYPE_CHECKING:
    from hippogym.ui_elements.grid import Tile
    from hippogym import HippoGym


class GridMessageHandler(MessageHandler):
    def __init__(self, hippo: "HippoGym") -> None:
        super().__init__(self.hippo.queues["grid_q"])
        self.grid = self.hippo.get_grid()
        self.hippo = hippo
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
