import logging


class EventHandler:

    def __init__(self, **kwargs):
        self.keyboard_q = kwargs.get('keyboard_q', None)
        self.button_q = kwargs.get('button_q', None)
        self.window_q = kwargs.get('window_q', None)
        self.standard_q = kwargs.get('standard_q', None)
        self.flow_q = kwargs.get('flow_q', None)

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

    def parse(self, message):
        new_user = False
        user_id = message.get('userId', None)
        if user_id:
            project_id = message.get('projectId', None)
            self.handle_user_id(user_id, project_id)
            return new_user
        event = message.get('KeyboardEvent', None)
        if event:
            self.handle_keyboard_event(event)
            return new_user
        event = message.get('MouseEvent', None)
        if event:
            self.handle_window_event(event)
            return new_user
        event = message.get('ButtonEvent', None)
        if event:
            self.handle_button_event(event)
            return new_user
        event = message.get('WindowEvent', None)
        if event:
            self.handle_window_event(event)
            return new_user
        return new_user

    def handle_user_id(self, user_id, project_id):
        message = {'userId': user_id, 'projectId': project_id}
        put_in_queue(message, self.flow_q)

    def handle_keyboard_event(self, message):
        put_in_queue(message, self.keyboard_q)
        # check for common keys to add to standard_q events
        keydown = message.get('KEYDOWN', None)
        if keydown:
            key = keydown.get('KEWDOWN', None)
            if key:
                key = key[0]
                standard_message = get_standard_message(key)
                if standard_message:
                    put_in_queue(standard_message, self.standard_q)

    def handle_button_event(self, message):
        put_in_queue(message, self.button_q)
        button = message.get('BUTTONPRESSED', None)
        if button == 'start':
            put_in_queue(message, self.flow_q)
        if button == 'pause':
            put_in_queue(message, self.flow_q)
        if button == 'stop':
            put_in_queue(message, self.flow_q)

    def handle_window_event(self, message):
        put_in_queue(message, self.widow_q)


def put_in_queue(message, queue):
    try:
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(message)
    except Exception as e:
        logging.error(e)


def get_standard_message(event):
    action = None
    if event == 'w' or event == 'UpArrow' or event == 'up':
        action = 'up'
    if event == 's' or event == 'DownArrow' or event == 'down':
        action = 'down'
    if event == 'a' or event == 'LeftArrow' or event == 'left':
        action = 'left'
    if event == 'd' or event == 'RightArrow' or event == 'right':
        action = 'right'
    if event == 'Space' or event == 'fire':
        action = 'fire'
    if action:
        return {'ACTION': action}
    return None
