""" To try this example you must install the minigrid environment

```bash
pip install git+https://github.com/MathisFederico/gym-minigrid.git
```

"""

from enum import Enum
import logging

import gym

from hippogym import HippoGym, Agent
from hippogym.ui_elements import InfoPanel, ControlPanel
from hippogym.ui_elements.building_blocks.button import *
from hippogym.trialsteps import GymStep

from gym_minigrid.minigrid import MiniGridEnv

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
    def __init__(
        self,
    ) -> None:
        self.trialstep: "GymStep" = None
        super().__init__()  # ?

    def act(self, observation):

        button_value_to_action = {
            HumanValue.LEFT: MiniGridEnv.Actions.left.value,
            HumanValue.RIGHT: MiniGridEnv.Actions.right.value,
            HumanValue.UP: MiniGridEnv.Actions.forward.value,
            HumanValue.TOGGLE: MiniGridEnv.Actions.toggle.value,
            HumanValue.PICKUP: MiniGridEnv.Actions.pickup.value,
            HumanValue.DROP: MiniGridEnv.Actions.drop.value,
            HumanValue.END: MiniGridEnv.Actions.done.value,
        }

        for message in self.trialstep.poll():
            button: str = message.get("BUTTONPRESSED", "")

            try:
                human_input = HumanValue(button.lower())
            except ValueError:
                continue

            return button_value_to_action[human_input]


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
 
        self.control_panel = ControlPanel(
            buttons=controls,
            keys=True,
        )

        self.score = 0
        self.env: MiniGridEnv = gym.make("MiniGrid-MultiRoom-N6-v0")
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
        image = self.env.gen_obs()["image"]
        rgb_array = self.env.get_obs_render(image, tile_size=64)
        render = self.render_window.convert_numpy_array_to_base64(rgb_array)
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
