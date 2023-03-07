""" This examples require to have install the crafting environment.

```bash
pip install git+https://github.com/IRLL/Crafting.git#egg=crafting
```

"""

from copy import copy
import logging
from typing import Optional, Tuple

import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

import gym
from crafting import CraftingEnv
from crafting.render.human import get_human_action

from hippogym import HippoGym, Agent
from hippogym.trialsteps import GymStep

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class HumanCraftingAgent(Agent):
    def __init__(self, observation_space=None, action_space=None) -> None:
        self.trialstep: Optional["GymStep"] = None
        self.action = None
        super().__init__(observation_space, action_space)

    def message_to_event(self, event_type, event_data) -> Optional[Event]:
        window_size = self.trialstep.render_window.size
        if event_type == "MOUSEBUTTONUP":
            pygame_event_type = MOUSEBUTTONUP
            pos, buttons, button = event_data
            rel = None
        elif event_type == "MOUSEBUTTONDOWN":
            pygame_event_type = MOUSEBUTTONDOWN
            pos, buttons, button = event_data
            rel = None
        elif event_type == "MOUSEMOTION":
            pygame_event_type = MOUSEMOTION
            pos, rel, buttons, button = event_data
        else:
            return

        pos_relative = (pos["x"] / window_size[0], pos["y"] / window_size[1])
        pos_abs = rel_to_abs_coords(*pos_relative)

        if rel is not None:
            rel_relative = (
                rel["xMovement"] / window_size[0],
                rel["yMovement"] / window_size[1],
            )
            rel_abs = rel_to_abs_coords(*rel_relative)
            return Event(pygame_event_type, pos=pos_abs, rel=rel_abs, button=button)
        return Event(pygame_event_type, pos=pos_abs, button=1)

    def on_mouse_event(self, event_type: "MouseEvent", event_data):
        # Create fake pygame mouse event
        fake_event = self.message_to_event(event_type, event_data)

        if fake_event is None:
            return

        # Get action from crafting rendering
        env: CraftingEnv = self.trialstep.env
        action = get_human_action(
            env,
            additional_events=[fake_event],
            can_be_none=True,
        )
        if action:
            self.action = action

    def act(self, observation):
        if self.action is not None:
            action = copy(self.action)
            self.action = None
            return action
        return self.action


class MineCraftingStep(GymStep):
    def __init__(self, agent, render_mode: str = "rgb_array"):
        self.score = 0
        env = gym.make("MineCrafting-v1")
        super().__init__(env, agent)

    def run(self) -> None:
        self.env.reset()
        self.env.render()
        self.render_window.set_size(*pygame_screen_size())
        return super().run()


def pygame_screen_size() -> Tuple[int, int]:
    screen = pygame.display.get_surface()
    return screen.get_size()


def rel_to_abs_coords(x_rel: float, y_rel: float) -> Tuple[int, int]:
    """Convert relative to absolute coordinates on the pygame window.

    Args:
        x_rel (float): Relative horizontal coordinates.
        y_rel (float): Relative vertical coordinates.

    Returns:
        Tuple[int, int]: Absolute pixel coordinates on the pygame window.
    """
    width, height = pygame_screen_size()
    return int(x_rel * width), int(y_rel * height)


def build_experiment(render_mode: str = "rgb_array") -> HippoGym:
    agent = HumanCraftingAgent()
    lunarstep = MineCraftingStep(agent, render_mode=render_mode)
    return HippoGym(lunarstep)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
