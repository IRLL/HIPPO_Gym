""" To try this example you must install the minigrid environment

```bash
pip install git+https://github.com/Farama-Foundation/Minigrid.git
```

"""

from enum import Enum
import logging

import gymnasium as gym
from minigrid.minigrid_env import MiniGridEnv

from hippogym import HippoGym, HumanAgent
from hippogym.ui_elements import InfoPanel, ControlPanel
from hippogym.ui_elements.building_blocks import Button
from hippogym.trialsteps import GymStep


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class HumanValue(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    TOGGLE = "toggle"
    PICKUP = "pickup"
    DROP = "drop"
    END = "end"


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

    keyboard_to_value = {
        "ArrowRight": HumanValue.RIGHT,
        "ArrowLeft": HumanValue.LEFT,
        "ArrowUp": HumanValue.UP,
        " ": HumanValue.TOGGLE,
        "c": HumanValue.PICKUP,
        "v": HumanValue.DROP,
        "Enter": HumanValue.END,
    }

    value_to_action = {
        HumanValue.LEFT: MiniGridEnv.Actions.left.value,
        HumanValue.RIGHT: MiniGridEnv.Actions.right.value,
        HumanValue.UP: MiniGridEnv.Actions.forward.value,
        HumanValue.TOGGLE: MiniGridEnv.Actions.toggle.value,
        HumanValue.PICKUP: MiniGridEnv.Actions.pickup.value,
        HumanValue.DROP: MiniGridEnv.Actions.drop.value,
        HumanValue.END: MiniGridEnv.Actions.done.value,
    }

    agent = HumanAgent(HumanValue, value_to_action, keyboard_to_value)
    minigrid = MiniGridStep(agent)
    return HippoGym(minigrid)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
