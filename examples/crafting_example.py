""" This examples require to have install the crafting environment.

```bash
pip install git+https://github.com/IRLL/Crafting.git#egg=crafting
```

"""

import logging
from typing import Optional, Tuple

import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

from crafting import CraftingEnv, MineCraftingEnv
from crafting.task import TaskObtainItem
from crafting.render.render import get_human_action

from hippogym import HippoGym, Agent
from hippogym.trialsteps import GymStep
from hippogym.queue_handler import check_queue
from hippogym.event_handler import EventsQueues

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class HumanCraftingAgent(Agent):
    def __init__(self, observation_space=None, action_space=None) -> None:
        self.trialstep: Optional["GymStep"] = None
        super().__init__(observation_space, action_space)

    def message_to_event(self, message) -> Optional[Event]:
        window_size = self.trialstep.render_window.size
        if "MOUSEBUTTONUP" in message:
            event_type = MOUSEBUTTONUP
            pos, buttons, button = message["MOUSEBUTTONUP"]
            rel = None
        elif "MOUSEBUTTONDOWN" in message:
            event_type = MOUSEBUTTONDOWN
            pos, buttons, button = message["MOUSEBUTTONDOWN"]
            rel = None
        elif "MOUSEMOTION" in message:
            event_type = MOUSEMOTION
            pos, rel, buttons, button = message["MOUSEMOTION"]
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
            return Event(event_type, pos=pos_abs, rel=rel_abs, button=button)
        return Event(event_type, pos=pos_abs, button=1)

    def act(self, observation):
        for message in check_queue(self.trialstep.queues[EventsQueues.WINDOW]):

            # Create fake pygame mouse event
            fake_event = self.message_to_event(message)

            if fake_event is None:
                continue

            # Get action from crafting rendering
            env: CraftingEnv = self.trialstep.env
            action = get_human_action(
                env,
                additional_events=[fake_event],
                can_be_none=True,
                **env.render_variables,
            )
            if action:
                action = env.action(*action)
            return action


class MineCraftingStep(GymStep):
    def __init__(self, agent):
        self.score = 0
        env = MineCraftingEnv(verbose=1, max_step=50, render_mode="rgb_array")
        task = TaskObtainItem(env.world, env.world.item_from_name["enchanting_table"])
        env.add_task(task)
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


def build_experiment() -> HippoGym:
    agent = HumanCraftingAgent()
    lunarstep = MineCraftingStep(agent)
    return HippoGym(lunarstep)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
