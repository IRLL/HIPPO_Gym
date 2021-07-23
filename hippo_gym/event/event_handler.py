class EventHandler:

    def __init__(self, pipe, hippo):
        self.pipe = pipe
        self.pressed_keys = set()
        self.hippo = hippo

    def get(self):
        # return all events from queue
        events = []
        while self.pipe.poll():
            event = self.parse_event(self.pipe.recv())
            if event:
                events.append(event)
        if len(events) == 0:
            events = None
        return events

    def poll(self):
        # return single event from queue
        if self.pipe.poll():
            event = self.parse_event(self.pipe.recv())
            return event
        else:
            return None

    def wait(self):
        # wait for single event
        return self.parse_event(self.pipe.recv())

    def peek(self):
        # test if event type is waiting in queue
        return self.pipe.peek()

    def clear(self):
        # clear all events from queue
        while self.pipe.poll():
            self.pipe.recv()

    def parse_event(self, message):
        event = message.get('KeyboardEvent', None)
        if event:
            self.handle_keyboard_event(event)
            return event
        event = message.get('MouseEvent', None)
        if event:
            self.handle_mouse_event(event)
            return event
        event = message.get('ButtonEvent', None)
        if event:
            self.handle_button_event(event)
            return event
        event = message.get('WindowEvent', None)
        if event:
            self.handle_window_event(event)
            return event
        return None

    def handle_keyboard_event(self, message):
        keydown = message.get('KEYDOWN', None)
        if keydown:
            self.pressed_keys.add(tuple(keydown[0]))
        keyup = message.get('KEYUP', None)
        if keyup:
            self.pressed_keys.discard(keyup[0])

    def handle_mouse_event(self, message):
        pass

    def handle_button_event(self, message):
        button = message.get('BUTTONPRESSED', None)
        if button == 'start':
            self.hippo.start()
        if button == 'pause':
            self.hippo.pause()
        if button == 'stop':
            self.hippo.stop()

    def handle_window_event(self, message):
        size = message.get('WINDOWRESIZED', None)
        if size:
            self.hippo.set_window_size(size)
