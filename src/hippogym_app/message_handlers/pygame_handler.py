from typing import Tuple
import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

from hippogym_app.message_handlers import MessageHandler


def rel_to_abs_coords(x_rel: float, y_rel: float) -> Tuple[int, int]:
    """Convert relative to absolute coordinates on the pygame window.

    Args:
        x_rel (float): Relative horizontal coordinates.
        y_rel (float): Relative vertical coordinates.

    Returns:
        Tuple[int, int]: Absolute pixel coordinates on the pygame window.
    """
    screen = pygame.display.get_surface()
    w, h = screen.get_size()
    return (int(x_rel * w), int(y_rel * h))


class PyGameMessageHandler(MessageHandler):
    """
    A MessageHandler design to send incomming messages as pygame events.
    """

    def handle_info_message(self, message: dict):
        """
        Send pygames events to the trial agent.
        """
        if not hasattr(self.trial.agent, "handle_events"):
            raise NotImplementedError(f"Agent cannot handle mouse_event: {message}")

        event_type = message["info"]
        pos = message["pos"]
        pos = rel_to_abs_coords(pos["xRel"], pos["yRel"])

        if event_type == "mouse up":
            events = [Event(MOUSEBUTTONUP, pos=pos, button=1)]
        elif event_type == "mouse down":
            events = [Event(MOUSEBUTTONDOWN, pos=pos, button=1)]
        elif event_type == "mouse move":
            rel = message["rel"]
            rel = rel_to_abs_coords(rel["xRelMovement"], rel["yRelMovement"])
            events = [Event(MOUSEMOTION, pos=pos, rel=rel)]

        action = self.trial.agent.handle_events(events)
        if action is not None:
            self.handle_action(action)
