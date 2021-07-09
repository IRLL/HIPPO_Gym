from message_handler import MessageHandler

import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

def convert_relative_coordinates(x_rel, y_rel):
    screen = pygame.display.get_surface()
    w, h = screen.get_size()
    return (int(x_rel * w), int(y_rel * h))

class PyGameMessageHandler(MessageHandler):

    def handle_mouse_event(self, message:dict):
        '''
        Send pygames events to the trial agent.
        '''
        event_type = message['info']

        if hasattr(self.trial.agent, 'handle_events'):

            if event_type == 'point clicked':

                coords = message['coordinates']
                coords = convert_relative_coordinates(coords['xRel'], coords['yRel'])

                events = [
                    Event(MOUSEBUTTONDOWN, pos=coords, button=1),
                    Event(MOUSEBUTTONUP, pos=coords, button=1)
                ]

                self.trial.humanAction = self.trial.agent.handle_events(events)

            elif event_type == 'mouse motion':

                print(message)
                # raise NotImplementedError

                # pos = (
                #     int(message['coordinates']['xRel'] * w),
                #     int(message['coordinates']['yRel'] * h)
                # )

                # events = [
                #     Event(MOUSEMOTION, pos=pos, rel=rel)
                # ]
                

        else:
            raise NotImplementedError('Agent has no member handle_events')

