import logging


class EventHandler:

    def __init__(self, queues):
        self.keyboard_q = queues.get('keyboard_q', None)
        self.button_q = queues.get('button_q', None)
        self.window_q = queues.get('window_q', None)
        self.standard_q = queues.get('standard_q', None)
        self.control_q = queues.get('control_q', None)
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
        event = message.get('SliderEvent', None)
        if event:
            self.handle_slider_event(event)
            return new_user
        return new_user

    def handle_user_id(self, user_id, project_id):
        message = {'userId': user_id, 'projectId': project_id}
        put_in_queue(message, self.control_q)

    def handle_keyboard_event(self, message):
        put_in_queue(message, self.keyboard_q)
        # check for common keys to add to standard_q events
        keydown = message.get('KEYDOWN', None)
        if keydown:
            keydown = keydown[0]
            self.check_standard_message(keydown)

    def handle_button_event(self, message):
        put_in_queue(message, self.button_q)
        button = message.get('BUTTONPRESSED', None)
        if button:
            self.check_standard_message(button)
        if button == 'start':
            put_in_queue(message, self.control_q)
        if button == 'pause':
            put_in_queue(message, self.control_q)
        if button == 'stop':
            put_in_queue(message, self.control_q)

    def handle_window_event(self, message):
        put_in_queue(message, self.window_q)

    def check_standard_message(self, event):
        action = None
        if event == 'w' or event == 'UpArrow' or event == 'up':
            action = 'up'
        if event == 's' or event == 'DownArrow' or event == 'down':
            action = 'down'
        if event == 'a' or event == 'LeftArrow' or event == 'left':
            action = 'left'
        if event == 'd' or event == 'RightArrow' or event == 'right':
            action = 'right'
        if event == ' ' or event == 'fire':
            action = 'fire'
        if action:
            put_in_queue({'ACTION': action}, self.standard_q)

    def handle_slider_event(self, message):
        put_in_queue(message, self.control_q)

def put_in_queue(message, queue):
    try:
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(message)
    except Exception as e:
        logging.error(e)


