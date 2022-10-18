""" This examples require to have install the crafting environment.

```bash
pip install git+https://github.com/IRLL/Crafting.git#egg=crafting
```

"""

import logging
from typing import Tuple

import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

from crafting import CraftingEnv, MineCraftingEnv
from crafting.task import TaskObtainItem
from crafting.render.render import get_human_action

from hippogym import HippoGym, Agent
from hippogym.ui_elements import InfoPanel, ControlPanel, standard_controls
from hippogym.trialsteps import GymStep
from hippogym.queue_handler import check_queue
from hippogym.event_handler import EventsQueues

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class HumanCraftingAgent(Agent):
    def __init__(self, observation_space=None, action_space=None) -> None:
        self.trialstep: "GymStep" = None
        super().__init__(observation_space, action_space)

    def act(self, observation):
        for message in check_queue(self.trialstep.queues[EventsQueues.WINDOW]):

            # Get mouse event position
            event_type = message["info"]
            pos = message["pos"]
            pos = rel_to_abs_coords(pos["xRel"], pos["yRel"])

            # Create fake pygame mouse event
            if event_type == "mouse up":
                events = [Event(MOUSEBUTTONUP, pos=pos, button=1)]
            elif event_type == "mouse down":
                events = [Event(MOUSEBUTTONDOWN, pos=pos, button=1)]
            elif event_type == "mouse move":
                rel = message["rel"]
                rel = rel_to_abs_coords(rel["xRelMovement"], rel["yRelMovement"])
                events = [Event(MOUSEMOTION, pos=pos, rel=rel)]

            # Get action from crafting rendering
            env: CraftingEnv = self.trialstep.env
            action = get_human_action(
                env,
                additional_events=events,
                can_be_none=True,
                **env.render_variables,
            )
            if action:
                action = env.action(*action)
            return action


class MineCraftingStep(GymStep):
    def __init__(self, agent):
        self.info_panel = InfoPanel(text="Use your mouse to play the game")
        self.control_panel = ControlPanel(
            buttons=standard_controls,
            keys=True,
        )
        self.score = 0
        env = MineCraftingEnv(verbose=1, max_step=50, render_mode="rgb_array")
        env.add_task(
            TaskObtainItem(env.world, env.world.item_from_name["enchanting_table"])
        )
        super().__init__(
            env,
            agent,
            ui_elements=[self.info_panel, self.control_panel],
        )

    def step(
        self,
        observation,
        action,
        new_observation,
        reward: float,
        done: bool,
        info: dict,
    ) -> None:

        if done:
            self.info_panel.update(key_value={"Score": reward})
            self.score = 0
            return

        observation_msg = ", ".join([f"{x:.2f}" for x in new_observation])
        observation_msg = f"[{observation_msg}]"
        self.score += reward
        self.info_panel.update(
            key_value={
                "Score": self.score,
                "Reward": reward,
                "Observation": observation_msg,
            },
        )


def rel_to_abs_coords(x_rel: float, y_rel: float) -> Tuple[int, int]:
    """Convert relative to absolute coordinates on the pygame window.

    Args:
        x_rel (float): Relative horizontal coordinates.
        y_rel (float): Relative vertical coordinates.

    Returns:
        Tuple[int, int]: Absolute pixel coordinates on the pygame window.
    """
    screen = pygame.display.get_surface()
    width, height = screen.get_size()
    return (int(x_rel * width), int(y_rel * height))


def build_experiment() -> HippoGym:
    agent = HumanCraftingAgent()
    lunarstep = MineCraftingStep(agent)
    return HippoGym(lunarstep)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
