import json
import logging

class Grid:
    def __init__(self, pipe, rows, columns):
        self.pipe = pipe
        self.rows = rows
        self.columns = columns

    def send_grid(self, grid):
        self.send({'grid': grid})


    def update_grid(self, update):
        self.send({'update': update})

    def send(self, message):
        self.pipe.send(json.dumps(message))