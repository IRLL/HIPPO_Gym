import logging


class EventHandler:

    def __init__(self, queues):
        self.keyboard_q = queues.get('keyboard_q', None)
        self.button_q = queues.get('button_q', None)
        self.window_q = queues.get('window_q', None)
        self.standard_q = queues.get('standard_q', None)
        self.control_q = queues.get('control_q', None)
        self.textbox_q = queues.get('textbox_q', None)
        if not self.control_q:
            logging.debug("no control_q in EventHandler")
        if not self.keyboard_q:
            logging.debug("no keyboard_q in EventHandler")
        if not self.button_q:
            logging.debug("no button_q in EventHandler")
        if not self.window_q:
            logging.debug("no window_q in EventHandler")
        if not self.standard_q:
            logging.debug("no standard_q in EventHandler")
        if not self.textbox_q:
            logging.debug("no textbox_q in EventHandler")
        self.pressed_keys = set()
        self.key_map = {'w': 'up', 'a': 'left', 's': 'down', 'd': 'right', ' ': 'fire'}

        self.handlers = {
            'KeyboardEvent': self.handle_keyboard_event,
            'MouseEvent': self.handle_window_event,
            'ButtonEvent': self.handle_button_event,
            'WindowEvent': self.handle_window_event,
            'SliderEvent': self.handle_slider_event,
            'TextEvent': self.handle_text_event
        }

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
        for key in message.keys():
            if key in self.handlers:
                self.handlers[key](message[key])

    def handle_user_id(self, ids):
        message = {'userId': ids[0], 'projectId': ids[1]}
        print(ids[0], ids[1])
        put_in_queue(message, self.control_q)

    def handle_text_event(self, message):
        put_in_queue(message, self.textbox_q)

    def handle_keyboard_event(self, message):
        put_in_queue(message, self.keyboard_q)
        # check for common keys to add to standard_q events
        keydown = message.get('KEYDOWN', None)
        if keydown:
            key = keydown[0]
            if key in self.key_map.keys() and key not in self.pressed_keys:
                self.pressed_keys.add(key)
                self.check_standard_message(key)
        keyup = message.get('KEYUP', None)
        if keyup:
            key = keyup[0]
            if key in self.key_map.keys() and key in self.pressed_keys:
                self.pressed_keys.remove(key)
                print(self.pressed_keys)
                self.check_standard_message(key)

    def handle_button_event(self, message):
        put_in_queue(message, self.button_q)
        button = message.get('BUTTONPRESSED', None)
        if button:
            self.check_standard_message(button)
        if button == 'start':
            put_in_queue({'start': True}, self.control_q)
        if button == 'pause':
            put_in_queue({'pause': True}, self.control_q)
        if button == 'end':
            put_in_queue({'end': True}, self.control_q)

    def handle_window_event(self, message):
        put_in_queue(message, self.window_q)

    def check_standard_message(self, event):
        action = None
        if event in self.key_map.keys():
            if len(self.pressed_keys) == 0:
                action = 'noop'
            elif 'a' in self.pressed_keys and 'w' in self.pressed_keys:
                action = 'upleft'
            elif 'a' in self.pressed_keys and 's' in self.pressed_keys:
                action = 'downleft'
            elif 'd' in self.pressed_keys and 'w' in self.pressed_keys:
                action = 'upright'
            elif 'd' in self.pressed_keys and 's' in self.pressed_keys:
                action = 'downright'
            else:
                key = self.pressed_keys.pop()
                self.pressed_keys.add(key)
                action = self.key_map[key]

        elif event == 'w' or event == 'UpArrow' or event == 'up':
            action = 'up'
        elif event == 's' or event == 'DownArrow' or event == 'down':
            action = 'down'
        elif event == 'a' or event == 'LeftArrow' or event == 'left':
            action = 'left'
        elif event == 'd' or event == 'RightArrow' or event == 'right':
            action = 'right'
        elif event == ' ' or event == 'fire':
            action = 'fire'
        if action:
            put_in_queue({'ACTION': action}, self.standard_q)

    def handle_slider_event(self, message):
        put_in_queue(message, self.control_q)

    def connect(self, message):
        user_id = message.get('userId', None)
        project_id = message.get('projectId', None)
        return user_id, project_id

    def disconnect(self, user_id):
        put_in_queue({"disconnect": user_id}, self.control_q)


def put_in_queue(message, queue):
    try:
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(message)
    except Exception as e:
        logging.error(e)