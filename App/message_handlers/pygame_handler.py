import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

from App.message_handlers import MessageHandler


def convert_relative_coordinates(x_rel, y_rel):
    screen = pygame.display.get_surface()
    w, h = screen.get_size()
    return (int(x_rel * w), int(y_rel * h))


class PyGameMessageHandler(MessageHandler):
    def handle_info(self, event_type: dict):
        """
        Send pygames events to the trial agent.
        """

        if hasattr(self.trial.agent, "handle_events"):

            pos = message["pos"]
            pos = convert_relative_coordinates(pos["xRel"], pos["yRel"])

            if event_type == "mouse up":
                events = [Event(MOUSEBUTTONUP, pos=pos, button=1)]
            elif event_type == "mouse down":
                events = [Event(MOUSEBUTTONDOWN, pos=pos, button=1)]
            elif event_type == "mouse move":
                rel = message["rel"]
                rel = convert_relative_coordinates(
                    rel["xRelMovement"], rel["yRelMovement"]
                )
                events = [Event(MOUSEMOTION, pos=pos, rel=rel)]

            action = self.trial.agent.handle_events(events)
            if action is not None:
                self.handle_action(action)

        else:
            raise NotImplementedError(f"Agent cannot handle mouse_event: {message}")
