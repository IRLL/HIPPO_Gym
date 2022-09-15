from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Set


from hippogym.ui_elements.ui_element import UIElement


if TYPE_CHECKING:
    from multiprocessing import Queue


class Grid(UIElement):
    def __init__(self, queue: "Queue", rows: int = 10, columns: int = 10) -> None:
        super().__init__(queue)
        self.rows = rows
        self.columns = columns
        self.tiles: List[Tile] = []
        self.selected_tiles: Set[Tile] = set()

    def dict(self) -> dict:
        return {
            "grid": {
                "rows": self.rows,
                "columns": self.columns,
                "tiles": self.tiles,
            }
        }

    def select(self, tile: "Tile") -> None:
        self.selected_tiles.add(tile)

    def unselect(self, tile: "Tile") -> None:
        self.selected_tiles.discard(tile)

    def click(self, tile: "Tile") -> None:
        if tile in self.selected_tiles:
            self.selected_tiles.remove(tile)
        else:
            self.selected_tiles.add(tile)

    @property
    def selected_tiles_list(self) -> List["Tile"]:
        return list(self.selected_tiles)


@dataclass
class TileContent:
    text: Optional[str] = field(default=None)
    image: Optional[str] = field(default=None)
    icon: Optional[str] = field(default=None)
    color: Optional[str] = field(default=None)
    bgcolor: Optional[str] = field(default=None)
    border: Optional[str] = field(default=None)


@dataclass
class Tile(dict):
    row: int
    col: int
    content: Optional[TileContent] = field(default=None, compare=False)
