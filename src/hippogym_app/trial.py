import json, shortuuid, time

import numpy as np

from multiprocessing.connection import Connection

from hippogym_app.agents.craftingAgent import CraftingAgent
from hippogym_app.message_handlers import LibraryHandler, PyGameMessageHandler
from hippogym.recorder.recorder import LegacyRecorder
from hippogym_app.utils import array_to_b64, load_config

from hippogym_app.message_handlers.library_handler import LibraryModes

# TODO: Refactor this for more general MessageHandlers composablity
class PyGameLibrairyHandler(LibraryHandler, PyGameMessageHandler):
    pass


class Trial:
    def __init__(self, pipe: Connection):
        self.config = load_config("hippogym_app/.trialConfig.yml")

        self.pipe = pipe
        self.frame_id = 0

        self.episode = 0
        self.done = False

        self.record = []

        self.human_action = self.config.get("defaultAction")
        self.play = self.config.get("defaultStart", False)
        self.framerate = self.config.get("startingFrameRate", 30)
        self.project_id = self.config.get("projectId")

        self.trial_id = shortuuid.uuid()
        self.user_id = None
        self.filename = None
        self.path = None
        self.outfile = None

        self._last_frame = None

        self.start()
        self.run()

    def start(self):
        """
        Call the function in the Agent/Environment combo required to start
        a trial. By default passes the environment name that will be passed
        to gym.make().
        By default this expects the openAI Gym Environment object to be
        returned.
        """
        self.config["library_mode"] = np.random.choice(list(LibraryModes))
        print("library_mode: ", self.config["library_mode"])

        games = ("minecrafting",)
        self.config["game"] = np.random.choice(games)

        items_names = ("diamond", "clock", "enchanting_table")
        self.config["task_item_name"] = np.random.choice(items_names)

        if self.config["library_mode"] == LibraryModes.OPTIONS_GRAPHS:
            self.config["filter_by_utility"] = np.random.choice((True, False))
            self.config["rank_by_complexity"] = np.random.choice((True, False))
            print("filter_by_utility: ", self.config["filter_by_utility"])
            print("rank_by_complexity: ", self.config["rank_by_complexity"])

        self.agent = CraftingAgent()
        self.message_handler = PyGameLibrairyHandler(self)
        self.recorder = LegacyRecorder(self)
        self.agent.start(self.config)

    def run(self):
        """
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        """
        while not self.done:
            message = self.check_message()
            if message:
                self.message_handler.handle_message(message)
                self.recorder.record_message(message)
            if self.play:
                render = self.get_render()
                self.send_render(render)
                self.recorder.record_render(render)
                if self.human_action is not None:
                    env_state = self.agent.step(self.human_action)
                    self.recorder.record_step(env_state)
                    self.human_action = self.config.get("defaultAction")
                    if env_state["done"]:
                        self.reset()
            else:
                # Makes sure to update frame when resuming
                self._last_frame = None

    def reset(self):
        """
        Resets the OpenAI gym environment to start a new episode.
        By default this function will create a new log file for every
        episode, if the intention is to log only full trials then
        comment the 3 lines below contianing self.outfile and
        self.create_file.
        """
        if self.check_trial_done():
            self.end()
        else:
            self.agent.reset()
            self.message_handler.reset()
            self.recorder.reset()
            self.episode += 1

    def check_trial_done(self):
        """
        Checks if the trial has been completed and can be quit. Add conditions
        as required.
        """
        return self.episode >= self.config.get("maxEpisodes", 20)

    def end(self):
        """
        Closes the environment through the agent, closes any remaining outfile
        and sends the 'done' message to the websocket pipe. If logging the
        whole trial memory in self.record, uncomment the call to self.save_record()
        to write the record to file before closing.
        """
        self.pipe.send("done")
        self.agent.close()
        self.recorder.close()
        self.play = self.config.get("defaultStart", False)
        self.done = True

    def check_message(self):
        """
        Checks pipe for messages from websocket, tries to parse message from
        json. Retruns message or error message if unable to parse json.
        Expects some poorly formatted or incomplete messages.
        """
        if self.pipe.poll():
            message = self.pipe.recv()
            try:
                message = json.loads(message)
            except (ValueError, TypeError):
                message = {"error": "unable to parse message", "frameId": self.frame_id}
            return message
        return None

    def get_render(self) -> dict:
        """
        Calls the Agent/Environment render function which must return a npArray.
        Translates the npArray into a jpeg image and then base64 encodes the
        image for transmission in json message.
        """
        render = self.agent.render()
        frame = array_to_b64(render)
        self.frame_id += 1
        return {"frame": frame, "frameId": self.frame_id}

    def send_render(self, render: dict = None):
        """
        Attempts to send render message to websocket
        """
        if render is None:
            render = self.get_render()

        if self._last_frame is not None and self._last_frame == render["frame"]:
            # Skip if frame is the same as last frame to save bandwidth
            return

        self._last_frame = render["frame"]
        try:
            self.pipe.send(json.dumps(render))
        except Exception as error:
            raise TypeError("Render Dictionary is not JSON serializable") from error

    def send_ui(self, ui=None):
        if ui is None:
            defaultUI = ["left", "right", "up", "down", "start", "pause"]
            ui = self.config.get("ui", defaultUI)
        try:
            self.pipe.send(json.dumps({"UI": ui}))
        except Exception as error:
            raise TypeError("Render Dictionary is not JSON serializable") from error

    def send_variables(self):
        try:
            self.pipe.send(json.dumps(self.config.get("variables")))
        except:
            return

    def pause(self):
        self.play = False

    def resume(self):
        self.play = True
