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
    
    def add_tile(self, row, col, color, text = ""):
        self.tiles.append({'row': row, 'col': col, 'color': color, 'text': text})
        return