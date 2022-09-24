import logging
import time
import gym
import numpy as np

from hippogym.agent import Agent
from hippogym.hippogym import HippoGym
from hippogym.ui_elements import InfoPanel, GameWindow, ControlPanel, standard_controls
from hippogym.trialsteps import GymStep

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def send_render(env: gym.Env, window: GameWindow):
    render = window.convert_numpy_array_to_base64(env.render("rgb_array"))
    window.update(image=render)


class RandomAgent(Agent):
    def act(self, observation):
        actions = ["noop", "right", "down", "left"]
        action = np.random.choice(actions)
        if action in actions:
            return actions.index(action)
        return None


class HumanAgent(Agent):
    def __init__(self) -> None:
        self.last_action = "noop"
        self.trialstep: "GymStep" = None

    def act(self, observation):
        actions = ["noop", "right", "down", "left"]
        action = self.last_action
        for message in self.trialstep.poll():
            action = message.get("ACTION")
            button: str = message.get("BUTTONPRESSED", "")
            if button.lower() == "reset":
                return -1

        if action not in actions:
            action = self.last_action
        else:
            self.last_action = action
        return actions.index(action)


class LunarLanderV2Step(GymStep):
    def __init__(self, agent):
        self.info_panel = InfoPanel(
            text="Use keyboard to play the game",
            items=["s = down", "a = left", "d = right"],
        )
        self.control_panel = ControlPanel(
            buttons=standard_controls,
            keys=True,
        )
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
        else:
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
    agent = HumanAgent()
    lunarstep = LunarLanderV2Step(agent)
    return HippoGym(lunarstep)


def main():
    hippo = build_experiment()
    hippo.start()


if __name__ == "__main__":
    main()
