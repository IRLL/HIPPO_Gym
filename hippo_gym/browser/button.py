
class Button:
    def __init__(self, face, color, value ):
        self.face = face
        self.color = color
        self.value = value

    def update(self, face=None, color=None, value=None):
        if face:
            self.face = face
        if color:
            self.color = color
        if value:
            self.value = value

    def get(self):
        return {'face': self.face, 'color': self.color, 'value': self.value}
