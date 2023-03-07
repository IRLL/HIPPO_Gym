from copy import copy
from enum import Enum
import logging

from hippogym import HippoGym, HumanAgent
from hippogym.ui_elements import InfoPanel, ControlPanel, standard_controls
from hippogym.trialsteps import GymStep

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class LunarLanderAction(Enum):
    NOOP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class HumanAction(Enum):
    NOOP = "noop"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"
    RESET = "reset"


VALUE_TO_ACTION = {
    HumanAction.NOOP: LunarLanderAction.NOOP.value,
    HumanAction.RIGHT: LunarLanderAction.RIGHT.value,
    HumanAction.DOWN: LunarLanderAction.DOWN.value,
    HumanAction.LEFT: LunarLanderAction.LEFT.value,
    HumanAction.RESET: -1,
}

KEY_TO_VALUE = {
    "ArrowRight": HumanAction.RIGHT,
    "ArrowDown": HumanAction.DOWN,
    "ArrowLeft": HumanAction.LEFT,
}


class HumanAgentToggling(HumanAgent):
    def __init__(self) -> None:
        self.default_action = VALUE_TO_ACTION[HumanAction.NOOP]
        self.last_action = self.default_action
        super().__init__(HumanAction, VALUE_TO_ACTION, KEY_TO_VALUE)

    def act(self, observation):
        if self.action is None:
            return self.last_action

        if self.action == self.last_action:
            self.action = self.default_action

        self.last_action = self.action
        action = self.action
        self.action = None
        return action

    def reset(self):
        self.last_action = self.default_action
        super().reset()


class LunarLanderV2Step(GymStep):
    def __init__(self, agent):
        self.info_panel = InfoPanel(
            text="Use keyboard to play the game",
            items=["s = down", "a = left", "d = right"],
        )
        self.control_panel = ControlPanel(buttons=standard_controls)
        self.score = 0
        super().__init__(
            "LunarLander-v2",
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


def build_experiment() -> HippoGym:
    agent = HumanAgentToggling()
    lunarstep = LunarLanderV2Step(agent)
    return HippoGym(lunarstep)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
