from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hippogym.trialsteps.trialstep import TrialStep


class Agent(ABC):
    @abstractmethod
    def act(self, observation):
        """Policy of the agent.

        Return the agent action given its obsevation.
        """

    def set_step(self, trialstep: "TrialStep"):
        self.trialstep = trialstep
