""" This examples require to have install the hcraft dependency.

```bash
pip install hcraft[gui]
```

"""

from copy import copy
import logging
from typing import Optional, Tuple

from enum import Enum
from hippogym.ui_elements import InfoPanel, ControlPanel, Button
from hippogym.recorder import JsonRecorder

import pygame
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

from hcraft import HcraftEnv
from hcraft.render.human import get_human_action

from hippogym import HippoGym, Agent
from hippogym.trialsteps import GymStep

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class HumanValue(Enum):
    END = "end"

class HumanHCraftAgent(Agent):
    def __init__(self, observation_space=None, action_space=None) -> None:
        self.trialstep: Optional["GymStep"] = None
        self.action = None
        self.done = False
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

    def on_mouse_event(self, event_type, event_data):
        # Create fake pygame mouse event
        fake_event = self.message_to_event(event_type, event_data)

        if fake_event is None:
            return

        # Get action from crafting rendering
        env: HcraftEnv = self.trialstep.env
        action = get_human_action(
            env,
            additional_events=[fake_event],
            can_be_none=True,
        )
        if action:
            self.action = action
        if event_type == "MOUSEBUTTONUP" or event_type == "MOUSEBUTTONDOWN":
            pos, buttons, button = event_data
        elif event_type == "MOUSEMOTION":
            pos, rel, buttons, button = event_data

        if button == HumanValue.END.value:
            # Record data and reset score
            self.trialstep.recorder.record(
                data = {
                    "episode": self.trialstep.env.current_episode,
                    "steps": self.trialstep.env.step_count,
                    "reward": self.trialstep.score,
                },
                user_id=self.trialstep.user_id,
            )
            self.trialstep.score = 0

    def act(self, observation):
        if self.action is not None:
            action = copy(self.action)
            self.action = None
            return action
        return self.action


class HCraftStep(GymStep):
    def __init__(self, env, agent):
        self.info_panel = InfoPanel(text="Press the end button to end the game")
        self.recorder = JsonRecorder(
                    records_path="records", experiment_name="hcraft_human"
                )
        buttons_params = {
            HumanValue.END: {},
        }

        controls = [
            Button(text=val.name.capitalize(), value=val.value, **buttons_params[val])
            for val in HumanValue
        ]

        self.control_panel = ControlPanel(buttons=controls)

        self.score = 0
        super().__init__(
            env,
            agent,
            ui_elements=[self.info_panel, self.control_panel],
        )
    def on_button_event(self, event_type, event_data):
        button_value = event_data.get("value")

        if button_value == HumanValue.END.value:
            # Record data and reset score
            self.recorder.record(
                data = {
                    "episode": self.env.current_episode,
                    "steps": self.env.step_count,
                    "reward": self.score,
                },
                user_id=self.user_id,
            )
            self.score = 0
    def step(
        self,
        episode: int,
        step: int,
        observation,
        action,
        new_observation,
        reward: float,
        done: bool,
        info: dict,
    ) -> None:
        self.score += reward
        self.info_panel.update(
            key_value={
                "Score": self.score,
                "Reward": reward,
            },
        )

        if done or self.agent.done:
            self.recorder.record(
                data={
                    "episode": episode,
                    "steps": self.env.step_count,
                    "reward": reward,
                },
                user_id=self.user_id,
            )
            self.score = 0
            self.agent.done = False  # Reset agent's done flag
            
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
    agent = HumanHCraftAgent()
    lunarstep = HCraftStep("MineHcraft-v1", agent)
    return HippoGym(lunarstep)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()