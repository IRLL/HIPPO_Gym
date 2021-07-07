class Grid():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.tiles = []
    
    def stringify(self):
        grid = {
            'rows': self.rows,
            'columns': self.cols,
            'tiles': self.tiles,
        }
        return grid
    
    def add_tile(self, row, col, type, value,):
        self.tiles.append({'type': type, 'value': value, 'row': row, 'col': col})
        return