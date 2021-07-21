class Slider:
    def __init__(self, title, key, low, high, value):
        self.title = title
        self.key = key
        self.low = low
        self.high = high
        self.value = value

    def update(self, title=None, key=None, low=None, high=None, value=None):
        if title:
            self.title = title
        if key:
            self.key = key
        if low:
            self.low = low
        if high:
            self.high = high
        if value:
            self.value = value
