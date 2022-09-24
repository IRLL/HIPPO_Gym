from typing import TYPE_CHECKING, Dict, List, Optional, TypeVar, Union

import time
import gym

from hippogym.trialsteps.trialstep import InteractiveStep
from hippogym.ui_elements import GameWindow
from hippogym.agent import Agent

if TYPE_CHECKING:
    from hippogym.ui_elements import UIElement
    from hippogym.event_handler import EventsQueues
    from multiprocessing import Queue

Observation = TypeVar("Observation")
Action = TypeVar("Action")


class GymStep(InteractiveStep):
    """A step where user interacts with a gym environment through hippogym."""

    def __init__(
        self,
        env: Union[str, gym.Env],
        agent: Agent,
        ui_elements: List["UIElement"],
        render_window: Optional[GameWindow] = None,
        **kwargs
    ):
        self.render_window = (
            render_window if render_window is not None else GameWindow()
        )
        if self.render_window not in ui_elements:
            ui_elements.append(self.render_window)
        super().__init__(ui_elements)
        if isinstance(env, str):
            env = gym.make(env, render_mode="rgb_array", **kwargs)
        self.env = env
        self.agent = agent

        self.stop = False
        self.running = False

    def build(self, queues: Optional[Dict["EventsQueues", "Queue"]] = None) -> None:
        """Initialize queues and message handler thread."""
        self.agent.set_step(self)
        super().build(queues)

    def step(
        self,
        observation: Observation,
        action: Action,
        new_observation: Observation,
        reward: float,
        done: bool,
        info: dict,
    ) -> None:
        """Custom step behavior

        Args:
            observation: Environment Observation before the action.
            action: Action performed by the agent.
            new_observation: New environment Observation after the action.
            reward (float): Reward given to the agent.
            done (bool): True if the environment episode is finished.
            info (dict): Additional informations given by the environment.
        """

    def run(self) -> None:
        self.stop = False
        self.running = False
        observation, info = self.env.reset()
        while not self.stop:
            self.send_render()
            while self.running:

                action = self.agent.act(observation)
                new_observation, reward, done, truncated, info = self.env.step(action)

                self.step(observation, action, new_observation, reward, done, info)

                if done or truncated:
                    self.stop = True
                    new_observation, info = self.env.reset()

                observation = new_observation
                self.send_render()
                time.sleep(0.03)
            time.sleep(1)
        self.env.close()

    def send_render(self):
        rgb_array = self.env.render()
        render = self.render_window.convert_numpy_array_to_base64(rgb_array)
        self.render_window.update(image=render)
