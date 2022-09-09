from __future__ import annotations
from enum import Enum

import shortuuid
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from App.trial import Trial


class MessageType(Enum):
    """Enumeration of message types that the MessageHandler can handle."""

    COMMAND = "command"
    FRAMERATE_CHANGE = "changeFrameRate"
    ACTION = "action"
    INFO = "info"
    USER_ID = "userId"


class Command(Enum):
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
            MessageType.USER_ID: self.handle_user_id_message,
            MessageType.COMMAND: self.handle_command_message,
            MessageType.FRAMERATE_CHANGE: self.handle_framerate_change_message,
            MessageType.ACTION: self.handle_action_message,
            MessageType.INFO: self.handle_info_message,
        }

        for message_type in MessageType:
            if message_type.value in message:
                msg_type = MessageType(message_type)
                handler = handlers[msg_type]
                handler(message)
                if message_type in (MessageType.COMMAND, MessageType.ACTION):
                    return  # TODO: Check why we shouln't perform multiple handler in those cases

    def handle_command_message(self, message: dict) -> Union[str, Command]:
        """Handle message containing commands from user."""
        command_msg = message[MessageType.COMMAND.value]
        command = str(command_msg).strip().lower()
        try:
            command = Command(command)
        except ValueError:
            pass
        self.handle_command(command)

    def handle_command(self, command: Union[str, Command]) -> Union[str, Command]:
        """Handle basic commands from user."""
        command_effects = {
            Command.START: self.trial.resume,
            Command.STOP: self.trial.end,
            Command.RESET: self.trial.reset,
            Command.PAUSE: self.trial.pause,
            Command.REQUEST_UI: self.trial.send_ui,
        }
        if command in command_effects:
            command_effects[command]()
        return command

    def handle_user_id_message(self, message: dict):
        """Handle message containing a userId."""
        user_id = message.get(MessageType.USER_ID.value)
        self.handle_framerate_change(user_id)

    def handle_user_id(self, user_id: Optional[int]):
        """Handle the setting of a user id."""
        if not self.trial.user_id:
            user_id = user_id or f"user_{shortuuid.uuid()}"
            self.trial.user_id = user_id
            self.trial.send_ui()
            self.trial.send_variables()
            self.trial.reset()
            self.trial.send_render()

    def handle_framerate_change_message(self, message: dict):
        """Handle message containing framerate change."""
        change = str(message[MessageType.FRAMERATE_CHANGE.value])
        self.handle_framerate_change(change)

    def handle_framerate_change(self, change: str):
        """
        Changes the framerate in either increments of step, or to a requested
        value within a minimum and maximum bound.
        """
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

    def handle_action_message(self, message: dict):
        """Handle message containing an action."""
        action: Union[str, int] = message[MessageType.ACTION.value]
        self.handle_action(action)

    def handle_action(self, action: Union[str, int]):
        """
        Translates action to int and resets action buffer
        """

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

    def handle_info_message(self, message: dict):
        """Handle message containing any custom info."""
        action: Union[str, int] = message[MessageType.INFO.value]
        self.handle_info(action)

    def handle_info(self, info: str):
        """
        Translates info into a custom behavior
        """
