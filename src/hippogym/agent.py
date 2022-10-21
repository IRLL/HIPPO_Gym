from abc import abstractmethod
from typing import TYPE_CHECKING, Optional


from hippogym.message_handler import MessageHandler

if TYPE_CHECKING:
    from gym import Space

    from hippogym.trialsteps.trialstep import TrialStep


class Agent(MessageHandler):
    def __init__(
        self,
        observation_space: Optional["Space"] = None,
        action_space: Optional["Space"] = None,
    ) -> None:
        self.observation_space = observation_space
        self.action_space = action_space
        self.trialstep: "TrialStep" = None

    @abstractmethod
    def act(self, observation):
        """Policy of the agent.

        Return the agent action given its obsevation.
        """

    def build(self, trialstep: "TrialStep") -> None:
        self.trialstep = trialstep
        MessageHandler.build(self, self.trialstep)

    def set_spaces(self, observation_space: "Space", action_space: "Space") -> None:
        self.observation_space = observation_space
        self.action_space = action_space
