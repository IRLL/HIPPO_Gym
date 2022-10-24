from abc import abstractmethod
from copy import copy
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional


from hippogym.message_handler import MessageHandler

if TYPE_CHECKING:
    from gym import Space

    from hippogym.trialsteps.gymstep import GymStep


class Agent(MessageHandler):
    def __init__(
        self,
        observation_space: Optional["Space"] = None,
        action_space: Optional["Space"] = None,
    ) -> None:
        self.observation_space = observation_space
        self.action_space = action_space
        self.trialstep: "GymStep" = None
        super().__init__()

    @abstractmethod
    def act(self, observation):
        """Policy of the agent.

        Return the agent action given its obsevation.
        """

    def build(self, trialstep: "GymStep") -> None:
        self.trialstep = trialstep
        MessageHandler.build(self, self.trialstep)

    def reset(self):
        """Reset the agent state"""

    def set_spaces(self, observation_space: "Space", action_space: "Space") -> None:
        self.observation_space = observation_space
        self.action_space = action_space


class HumanAgent(Agent):
    def __init__(
        self,
        values: Enum,
        value_to_action: Dict[str, Any],
        keyboard_to_value: Optional[Dict[str, str]] = None,
        observation_space: Optional["Space"] = None,
        action_space: Optional["Space"] = None,
    ) -> None:
        super().__init__(observation_space, action_space)
        self.action = None
        self.values = values
        self.value_to_action = value_to_action
        self.keyboard_to_value = (
            keyboard_to_value if keyboard_to_value is not None else {}
        )

    def on_button_event(self, event_type: "ButtonEvent", value: str):
        if event_type == "BUTTONPRESSED":
            human_input = value.lower()
            self.input_to_action(human_input)

    def on_keyboard_event(self, event_type: "KeyboardEvent", key: "KeyboardKey"):
        keyname = key[0]
        if event_type == "KEYDOWN":
            human_input = self.keyboard_to_value.get(keyname, None)
            self.input_to_action(human_input)

    def input_to_action(self, human_input: Optional[str]):
        try:
            human_input = self.values(human_input)
        except ValueError:
            return
        self.action = self.value_to_action.get(human_input, None)

    def act(self, observation):
        if self.action is not None:
            action = copy(self.action)
            self.action = None
            return action
        return self.action

    def reset(self):
        """Reset the agent state"""
        self.action = None
