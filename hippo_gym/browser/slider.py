class Slider:
    def __init__(self, id, key, low, high, value):
        self.id = id
        self.key = key
        self.min = low
        self.max = high
        self.value = value

    def update(self, id=None, key=None, low=None, high=None, value=None):
        if id:
            self.id = id
        if key:
            self.key = key
        if low:
            self.low = low
        if high:
            self.high = high
        if value:
            self.value = value
