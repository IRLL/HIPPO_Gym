from __future__ import annotations

import shortuuid
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from App.trial import Trial


class MessageHandler:
    def __init__(self, trial: Trial) -> None:
        self.trial = trial

    def reset(self) -> None:
        pass

    def handle_message(self, message: dict):
        """
        Reads messages sent from websocket, handles commands as priority then actions and infos.
        """
        if not self.trial.userId and "userId" in message:
            self.userId = message["userId"] or f"user_{shortuuid.uuid()}"
            self.trial.send_ui()
            self.trial.send_variables()
            self.trial.reset()
            self.trial.send_render()
        if "command" in message and message["command"]:
            self.handle_command(str(message["command"]))
        elif "changeFrameRate" in message and message["changeFrameRate"]:
            self.handle_framerate_change(message["changeFrameRate"])
        elif "action" in message and message["action"]:
            self.handle_action(message["action"])
        elif "info" in message:
            self.handle_mouse_event(message)

    def handle_command(self, command: str):
        """Deals with allowable commands from user."""
        command = command.strip().lower()
        if command == "start":
            self.trial.play = True
        elif command == "stop":
            self.trial.end()
        elif command == "reset":
            self.trial.reset()
        elif command == "pause":
            self.trial.play = False
        elif command == "requestUI":
            self.trial.send_ui()
        return command

    def handle_framerate_change(self, change: str):
        """
        Changes the framerate in either increments of step, or to a requested
        value within a minimum and maximum bound.
        """
        if not self.trial.config.get("allowFrameRateChange"):
            return

        step = self.trial.config.get("frameRateStepSize", 5)
        minFR = self.trial.config.get("minFrameRate", 1)
        maxFR = self.trial.config.get("maxFrameRate", 90)
        change = change.strip().lower()
        if change == "faster" and self.trial.framerate + step < maxFR:
            self.trial.framerate += step
        elif change == "slower" and self.trial.framerate - step > minFR:
            self.trial.framerate -= step
        else:
            try:
                requested = int(change)
                if requested > minFR and requested < maxFR:
                    self.trial.framerate = requested
            except:
                pass

    def handle_action(self, action: Union[str, int]):
        """
        Translates action to int and resets action buffer
        """
        if isinstance(action, int):
            self.trial.human_action = action
            return

        action = action.strip().lower()
        actionSpace = self.trial.config.get("actionSpace")
        if action in actionSpace:
            action = actionSpace.index(action)
        else:
            action = self.trial.config.get("defaultAction")
        self.trial.human_action = action

    def handle_mouse_event(self, message: dict):
        """
        Translates mouse events into a custom behavior
        """
        pass
