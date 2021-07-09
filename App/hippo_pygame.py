from message_handler import MessageHandler

import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP

class PyGameMessageHandler(MessageHandler):

    def handle_mouse_event(self, message:dict):
        '''
        Translates action to int and resets action buffer
        '''
        event_type = message['info']

        if hasattr(self.trial.agent, 'handle_events'):
            if event_type == 'point clicked':
                
                screen = pygame.display.get_surface()
                w, h = screen.get_size()

                coords = (
                    int(message['coordinates']['xRel'] * w),
                    int(message['coordinates']['yRel'] * h)
                )

                events = [
                    Event(MOUSEBUTTONDOWN, pos=coords, button=1),
                    Event(MOUSEBUTTONUP, pos=coords, button=1)
                ]
                
                self.trial.humanAction = self.trial.agent.handle_events(events)

            elif event_type == 'mouse motion':
                pass

        else:
            raise NotImplementedError('Agent has no member handle_event')

