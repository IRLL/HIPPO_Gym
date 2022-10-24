import time
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, TypeVar

import gym
import numpy as np

from hippogym.agent import Agent

from hippogym.trialsteps.trialstep import InteractiveStep
from hippogym.ui_elements import GameWindow
from hippogym.log import get_logger


if TYPE_CHECKING:
    from hippogym.event_handler import EventHandler
    from hippogym.ui_elements import UIElement

LOGGER = get_logger(__name__)

Observation = TypeVar("Observation")
Action = TypeVar("Action")


class GymStep(InteractiveStep):
    """A step where user interacts with a gym environment through hippogym."""

    def __init__(
        self,
        env: gym.Env,
        agent: Agent,
        ui_elements: Optional[List["UIElement"]] = None,
        render_window: Optional[GameWindow] = None,
        run_from_start: bool = True,
        **kwargs: dict,
    ) -> None:
        self.render_window = (
            render_window if render_window is not None else GameWindow()
        )
        if ui_elements is None:
            ui_elements = []
        if self.render_window not in ui_elements:
            ui_elements.append(self.render_window)
        super().__init__(ui_elements)
        if isinstance(env, str):
            env = gym.make(env, render_mode="rgb_array", **kwargs)
        self.env = env
        self.agent = agent
        self.agent.set_spaces(self.env.observation_space, self.env.action_space)

        self.stop = False
        self.run_from_start = run_from_start
        self.running = self.run_from_start

    def build(self, event_handler: "EventHandler") -> None:
        """Initialize queues and message handler thread."""
        super().build(event_handler)
        self.agent.build(self)

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
        self.running = self.run_from_start

        observation, info = self.gym_reset()

        while not self.stop:
            self.send_render()
            while self.running:

                action = None
                while action is None:
                    self.event_handler.trigger_events()
                    action = self.agent.act(observation)

                new_observation, reward, terminated, truncated, info = self.gym_step(
                    action
                )
                done = terminated or truncated
                LOGGER.debug("GymStep action was taken: %s. Reward: %f", action, reward)

                self.step(
                    observation, action, new_observation, reward, terminated, info
                )

                if done:
                    self.stop = True
                    observation, info = self.gym_reset()

                observation = new_observation
                self.send_render()
                time.sleep(0.01)
            time.sleep(1)
        self.env.close()

    def gym_step(self, action: Any) -> Tuple[Any, float, bool, bool, dict]:
        step_data = self.env.step(action)
        if len(step_data) == 5:
            return step_data
        if len(step_data) == 4:
            new_observation, reward, terminated, info = step_data
            truncated = False
            return new_observation, reward, terminated, truncated, info
        raise ValueError(
            f"Unexpected step data size : {len(step_data)}. Step data: {step_data}"
        )

    def gym_reset(self) -> Tuple[Any, dict]:
        reset_data = self.env.reset()
        if len(reset_data) == 2 and isinstance(reset_data[1], dict):
            return reset_data
        observation = reset_data
        info = {}
        return observation, info

    def send_render(self):
        rgb_array = self.env.render()
        if not isinstance(rgb_array, np.ndarray):
            raise TypeError("Env render should output a numpy array.")
        render = self.render_window.convert_numpy_array_to_base64(rgb_array)
        self.render_window.update(image=render)
