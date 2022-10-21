""" To try this example you must install the minigrid environment

```bash
pip install git+https://github.com/Farama-Foundation/Minigrid.git
```

"""

from copy import copy
from enum import Enum
import logging
from typing import Optional

import gymnasium as gym
from minigrid.minigrid_env import MiniGridEnv

from hippogym import HippoGym, Agent
from hippogym.ui_elements import InfoPanel, ControlPanel
from hippogym.ui_elements.building_blocks import Button
from hippogym.trialsteps import GymStep


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class HumanValue(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    TOGGLE = "toggle"
    PICKUP = "pickup"
    DROP = "drop"
    END = "end"


class HumanAgent(Agent):
    def __init__(self) -> None:
        self.trialstep: "GymStep" = None
        self.action = None
        super().__init__()

        self.keyboard_to_value = {
            "ArrowRight": HumanValue.RIGHT,
            "ArrowLeft": HumanValue.LEFT,
            "ArrowUp": HumanValue.UP,
            " ": HumanValue.TOGGLE,
            "c": HumanValue.PICKUP,
            "v": HumanValue.DROP,
            "Enter": HumanValue.END,
        }

        self.value_to_action = {
            HumanValue.LEFT: MiniGridEnv.Actions.left.value,
            HumanValue.RIGHT: MiniGridEnv.Actions.right.value,
            HumanValue.UP: MiniGridEnv.Actions.forward.value,
            HumanValue.TOGGLE: MiniGridEnv.Actions.toggle.value,
            HumanValue.PICKUP: MiniGridEnv.Actions.pickup.value,
            HumanValue.DROP: MiniGridEnv.Actions.drop.value,
            HumanValue.END: MiniGridEnv.Actions.done.value,
        }

    def on_button_event(self, event_type: "ButtonEvent", value: str):
        if event_type == "BUTTONPRESSED":
            human_input = value.lower()
            self.input_to_action(human_input)

    def on_keyboard_event(self, event_type: "KeyboardEvent", key: "KeyboardKey"):
        keyname = key[0]
        if event_type == "KEYDOWN":
            human_input = self.keyboard_to_value.get(keyname, None)
            self.input_to_action(human_input)

    def input_to_action(self, human_input: Optional[str]):
        try:
            human_input = HumanValue(human_input)
        except ValueError:
            return
        self.action = self.value_to_action.get(human_input, None)

    def act(self, observation):
        if self.action is not None:
            action = copy(self.action)
            self.action = None
            return action
        return self.action


class MiniGridStep(GymStep):
    def __init__(self, agent):
        self.info_panel = InfoPanel()

        buttons_params = {
            HumanValue.LEFT: {"icon": "FaArrowLeft"},
            HumanValue.RIGHT: {"icon": "FaArrowRight"},
            HumanValue.UP: {"icon": "FaArrowUp"},
            HumanValue.TOGGLE: {"icon": "IoToggle"},
            HumanValue.PICKUP: {"icon": "GiCardPickup"},
            HumanValue.DROP: {"icon": "GiDropWeapon"},
            HumanValue.END: {},
        }

        controls = [
            Button(text=val.name.capitalize(), value=val.value, **buttons_params[val])
            for val in HumanValue
        ]

        self.control_panel = ControlPanel(buttons=controls)

        self.score = 0
        self.env: MiniGridEnv = gym.make("MiniGrid-KeyCorridorS5R3-v0")
        super().__init__(
            self.env,
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

        observation_msg = f"Step={self.env.step_count}, Reward={reward}"
        observation_msg = f"[{observation_msg}]"
        self.score += reward
        self.info_panel.update(
            key_value={
                "Score": self.score,
                "Reward": reward,
                "Observation": observation_msg,
            },
        )

    def send_render(self):
        rgb_frame = self.env.get_frame(tile_size=64, agent_pov=True)
        render = self.render_window.convert_numpy_array_to_base64(rgb_frame)
        self.render_window.update(image=render)


def build_experiment() -> HippoGym:
    agent = HumanAgent()
    minigrid = MiniGridStep(agent)
    return HippoGym(minigrid)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
