from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from gym import Space

    from hippogym.trialsteps.trialstep import TrialStep


class Agent(ABC):
    def __init__(
        self,
        observation_space: Optional["Space"] = None,
        action_space: Optional["Space"] = None,
    ) -> None:
        self.observation_space = observation_space
        self.action_space = action_space

    @abstractmethod
    def act(self, observation):
        """Policy of the agent.

        Return the agent action given its obsevation.
        """

    def set_step(self, trialstep: "TrialStep"):
        self.trialstep = trialstep

    def set_spaces(self, observation_space: "Space", action_space: "Space") -> None:
        self.observation_space = observation_space
        self.action_space = action_space
