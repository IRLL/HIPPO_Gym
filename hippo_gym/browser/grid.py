
class Grid:
    def __init__(self, queue, rows=10, columns=10):
        self.queue = queue
        self.rows = rows
        self.columns = columns
        self.tiles = []
        self.selected_tiles = set()
        self.submitted = []

    def send(self):
        grid = {
            'rows': self.rows, 
            'columns': self.columns, 
            'tiles': self.tiles
        }
        self.queue.put_nowait({'grid': grid})

    def hide(self):
        self.queue.put_nowait({'grid': None})

    def update(self, **kwargs):
        self.rows = kwargs.get('rows', self.rows)
        self.columns = kwargs.get('columns', self.columns)
        tiles = kwargs.get('tiles', self.tiles)
        if not type(tiles) == list:
            raise TypeError('tiles must be a list')
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


class Tile(dict):
    def __init__(self, row, col, tile_type=None, **kwargs):
        dict.__init__(
            self,
            row=row,
            col=col,
            tile_type=tile_type if type(tile_type) == TileType else TileType(**kwargs)
        )

    def __eq__(self, other):
        if self['row'] == other['row'] and self['col'] == other['col']:
            return True
        else:
            return False

class TileType(dict):
    def __init__(self, **kwargs):
        dict.__init__(
            self,
            text = kwargs.get('text', None),
            image = kwargs.get('image', None),
            icon = kwargs.get('icon', None),
            color = kwargs.get('color', None),
            bgcolor = kwargs.get('bgcolor', None),
            border = kwargs.get('border', None)
        )

