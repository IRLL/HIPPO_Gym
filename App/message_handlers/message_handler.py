from __future__ import annotations
from enum import Enum

import shortuuid
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from App.trial import Trial


class MessageType(Enum):
    """Enumeration of message types that the MessageHandler can handle."""

    COMMAND = "command"
    FRAMERATE_CHANGE = "changeFrameRate"
    ACTION = "action"
    INFO = "info"
    USER_ID = "userId"


class Commands(Enum):
    """Enumeration of commands that the MessageHandler can handle."""

    START = "start"
    STOP = "stop"
    RESET = "reset"
    PAUSE = "pause"
    REQUEST_UI = "requestui"


class MessageHandler:
    def __init__(self, trial: Trial) -> None:
        self.trial = trial

    def reset(self) -> None:
        pass

    def handle_message(self, message: dict):
        """
        Reads messages sent from websocket, handles commands as priority then actions and infos.
        """
        handlers = {
            MessageType.USER_ID: self.handle_user_id,
            MessageType.COMMAND: self.handle_command,
            MessageType.FRAMERATE_CHANGE: self.handle_framerate_change,
            MessageType.ACTION: self.handle_action,
            MessageType.INFO: self.handle_user_id,
        }
        for message_type in MessageType:
            if message_type.value in message:
                msg_type = MessageType(msg_type)
                handler = handlers[msg_type]
                handler(message)
                return  # TODO: Check why we shouln't perform multiple handler

    def handle_command(self, message: dict) -> str:
        """Deals with allowable commands from user."""
        command_msg = message[MessageType.COMMAND]
        command = str(command_msg).strip().lower()
        command = Commands(command)
        command_effects = {
            Commands.START: self.trial.resume,
            Commands.STOP: self.trial.end,
            Commands.RESET: self.trial.reset,
            Commands.PAUSE: self.trial.pause,
            Commands.REQUEST_UI: self.trial.send_ui,
        }
        try:
            command_effects[command]()
            return command.value
        except KeyError:
            return command_msg

    def handle_user_id(self, message: dict):
        """Handle the setting of a user_id."""
        user_id = message[MessageType.USER_ID]
        if not self.trial.user_id:
            user_id = user_id or f"user_{shortuuid.uuid()}"
            self.trial.send_ui()
            self.trial.send_variables()
            self.trial.reset()
            self.trial.send_render()

    def handle_framerate_change(self, message: dict):
        """
        Changes the framerate in either increments of step, or to a requested
        value within a minimum and maximum bound.
        """
        change = str(message[MessageType.FRAMERATE_CHANGE])
        if not self.trial.config.get("allowFrameRateChange"):
            return

        step = self.trial.config.get("frameRateStepSize", 5)
        min_fps = self.trial.config.get("minFrameRate", 1)
        max_fps = self.trial.config.get("maxFrameRate", 90)
        change = change.strip().lower()
        if change == "faster" and self.trial.framerate + step < max_fps:
            self.trial.framerate += step
        elif change == "slower" and self.trial.framerate - step > min_fps:
            self.trial.framerate -= step
        else:
            requested = int(change)
            if min_fps < requested < max_fps:
                self.trial.framerate = requested

    def handle_action(self, message: dict):
        """
        Translates action to int and resets action buffer
        """
        action: Union[str, int] = message[MessageType.ACTION]

        # Directly given action index
        if isinstance(action, int):
            self.trial.human_action = action
            return

        # Action as str to interpret
        action = action.strip().lower()
        action_space = self.trial.config.get("actionSpace")
        if action in action_space:
            action = action_space.index(action)
        else:
            action = self.trial.config.get("defaultAction")
        self.trial.human_action = action

    def handle_info(self, message: dict):
        """
        Translates info into a custom behavior
        """
