import logging

class EventHandler:

    def __init__(self, **kwargs)
        self.keyboard_q = kwargs.get('keyboard_q', None)
        self.button_q = kwargs.get('button_q', None)
        self.game_window_queues = [kwargs.get('window_1_q', None), kwargs.get('window_2_q', None), kwargs.get('window_3_q', None)]
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
        event = message.get('KeyboardEvent', None)
        if event:
            self.handle_keyboard_event(event)
            return event
        event = message.get('MouseEvent', None)
        if event:
            self.handle_window_event(event)
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
        put_in_queue(message, self.keyboard_q)
        # check for common keys to add to standard_q events
        #keydown = message.get('KEYDOWN', None)
        #if keydown:



    def handle_button_event(self, message):
        put_in_queue(message, self.button_q)
        # check for flow control messages for the flow_q
        #button = message.get('BUTTONPRESSED', None)
        #if button == 'start':
            #self.hippo.start()
        #if button == 'pause':
            #self.hippo.pause()
        #if button == 'stop':
            #self.hippo.stop()

     def handle_window_event(self, message):
         index = message.get('windowId', 0)
         if len(self.game_window_queues) > index:
             put_in_queue(message, self.game_window_queues[index])

def put_in_queue(message, queue):
    try:
        if queue.full():
            queue.get_nowait()
        queue.put_nowait(message)
    except Exception as e:
        logging.error(e)
