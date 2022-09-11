from multiprocessing import Queue


class Grid:
    def __init__(self, queue: Queue, rows: int = 10, columns: int = 10):
        self.queue = queue
        self.rows = rows
        self.columns = columns
        self.tiles = []
        self.selected_tiles = set()
        self.submitted = []

    def send(self):
        grid = {"rows": self.rows, "columns": self.columns, "tiles": self.tiles}
        self.queue.put_nowait({"grid": grid})

    def hide(self):
        self.queue.put_nowait({"grid": None})

    def update(self, **kwargs):
        self.rows = kwargs.get("rows", self.rows)
        self.columns = kwargs.get("columns", self.columns)
        tiles = kwargs.get("tiles", self.tiles)
        if not isinstance(tiles, list):
            raise TypeError("tiles must be a list")
        self.tiles = tiles
        self.send()

    def add_tile(self, row, col, **kwargs):
        tile = Tile(row, col, **kwargs)
        if tile in self.tiles:
            self.tiles.remove(tile)
        self.tiles.append(tile)
        self.send()

    def remove_tile(self, row, col):
        tile = Tile(row, col)
        if tile in self.tiles:
            self.tiles.remove(tile)
        self.send()

    def create_tile_type(self, **kwargs):
        return TileType(**kwargs)

    def select(self, tile):
        self.selected_tiles.add(tile)

    def unselect(self, tile):
        self.selected_tiles.discard(tile)

    def get_selected(self):
        return list(self.selected_tiles)

    def click(self, tile):
        if tile in self.selected_tiles:
            self.selected_tiles.remove(tile)
        else:
            self.selected_tiles.add(tile)


class Tile(dict):
    def __init__(self, row: int, col: int, tile_type=None, **kwargs):
        tile_type = tile_type if isinstance(tile_type, TileType) else TileType(**kwargs)
        dict.__init__(
            self,
            row=row,
            col=col,
            tile_type=tile_type,
        )

    def __eq__(self, other: "Tile"):
        if not isinstance(other, Tile):
            return False
        same_row = self["row"] == other["row"]
        same_col = self["col"] == other["col"]
        return same_row and same_col


class TileType(dict):
    def __init__(self, **kwargs):
        dict.__init__(
            self,
            text=kwargs.get("text", None),
            image=kwargs.get("image", None),
            icon=kwargs.get("icon", None),
            color=kwargs.get("color", None),
            bgcolor=kwargs.get("bgcolor", None),
            border=kwargs.get("border", None),
        )
