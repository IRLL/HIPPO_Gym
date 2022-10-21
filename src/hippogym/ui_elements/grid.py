from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from hippogym.ui_elements.ui_element import UIElement


class Grid(UIElement):
    def __init__(self, rows: int = 10, columns: int = 10) -> None:
        super().__init__("grid")
        self.rows = rows
        self.columns = columns
        self.tiles: List[List[Tile]] = [
            [Tile() for _ in range(rows)] for _ in range(columns)
        ]
        self.selected_tiles: Set[Tuple[int, int]] = set()

    def params_dict(self) -> dict:
        return {
            "rows": self.rows,
            "columns": self.columns,
            "tiles": [str(tile for tile in self.tiles)],
        }

    def select(self, row: int, column: int) -> None:
        tile = self.tiles[row][column]
        tile.bgcolor = "#f9cd09"
        self.selected_tiles.add((row, column))

    def unselect(self, row: int, column: int) -> None:
        tile = self.tiles[row][column]
        tile.bgcolor = None
        self.selected_tiles.discard((row, column))

    def click(self, row: int, column: int) -> None:
        if (row, column) in self.selected_tiles:
            self.unselect(row, column)
        else:
            self.select(row, column)

    @property
    def selected_tiles_list(self) -> List[Tuple[int, int]]:
        return list(self.selected_tiles)

    def on_grid_event(self, event_type: "GridEvent", tile_data: str) -> None:
        grid_event_handlers = {
            "TILESELECTED": self.select,
            "TILEUNSELECTED": self.unselect,
            "TILECLICKED": self.click,
        }
        tile_data = read_tile_data(tile_data)
        handler = grid_event_handlers[event_type]
        handler(*tile_data)


def read_tile_data(tile_data: str) -> Tuple[int, int]:
    row, column = tuple(tile_data)
    return int(row), int(column)


@dataclass
class Tile:
    text: Optional[str] = field(default=None)
    image: Optional[str] = field(default=None)
    icon: Optional[str] = field(default=None)
    color: Optional[str] = field(default=None)
    bgcolor: Optional[str] = field(default=None)
    border: Optional[str] = field(default=None)
