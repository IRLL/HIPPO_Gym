import time
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, TypeVar

import gym
import numpy as np

from hippogym.agent import Agent
from hippogym.log import get_logger
from hippogym.trialsteps.trialstep import InteractiveStep
from hippogym.ui_elements import GameWindow

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
            if "LunarLander" in str(self):
                env = gym.make(env, render_mode="rgb_array", **kwargs)
            else:
                env = gym.make(env, **kwargs)
        self.env = env
        self.agent = agent
        self.agent.set_spaces(self.env.observation_space, self.env.action_space)
        self.RESET_ACTION = -1
        self.START_ACTION = -2
        self.waiting_for_start = False
        self.reset_pressed = False
        self.stop = False
        self.reseet_triggered = False
        self.run_from_start = run_from_start
        self.running = self.run_from_start

    def build(self, user_id: str, event_handler: "EventHandler") -> None:
        """Initialize queues and message handler thread."""
        super().build(user_id, event_handler)
        self.agent.build(self)

    def step(
        self,
        episode: int,
        step: int,
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
      self.reset_triggered = False
      self.reset_pressed = True
      observation, info = self.gym_reset()
      step = 0
      episode = 0

      while not self.stop:
          self.send_render()
          while self.running:
              action = None
              while action is None:
                  self.event_handler.trigger_events()
                  action = self.agent.act(observation)
                  if action == self.RESET_ACTION:
                      self.reset_triggered = True
                      observation, info = self.gym_reset()
                      self.agent.reset()
                      self.running = False
                      self.reset_pressed = True
                      step = 0
                      episode = 0
                      continue
                  elif action == self.START_ACTION:
                      self.running = True
                      self.reset_pressed = False
                      action = None
                      continue
                  step += 1
              if action not in [self.RESET_ACTION, self.START_ACTION]:
                  new_observation, reward, terminated, truncated, info = self.gym_step(
                      action
                  )
                  done = terminated or truncated
                  LOGGER.debug("GymStep action was taken: %s. Reward: %f", action, reward)

                  self.step(
                      episode,
                      step,
                      observation,
                      action,
                      new_observation,
                      reward,
                      terminated,
                      info,
                  )
  
                  if done:
                      observation, info = self.gym_reset()
                      self.agent.reset()
                      step = 0
                      episode += 1
  
                  observation = new_observation
              self.send_render()
              time.sleep(0.03)
          if self.reset_pressed:
              while action != self.START_ACTION or not self.agent.start_triggered:
                  self.event_handler.trigger_events()
                  action = self.agent.act(observation)
              self.running = True
              self.reset_pressed = False
              action = None
              self.agent.start_triggered = False
          else:
              action = None
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
        if "LunarLander" in str(self):
            rgb_array = self.env.render()
        else:
            rgb_array = self.env.render(mode="rgb_array")
        try:
            rgb_array = np.array(rgb_array)
        except:
            raise TypeError("Env render should output a numpy array.")
        render = self.render_window.convert_numpy_array_to_base64(rgb_array)
        self.render_window.update(image=render)
