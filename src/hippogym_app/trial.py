import base64
import errno
import json
import logging
import os

# for dummy score
import random
import time
import xml.etree.ElementTree as ET
from io import BytesIO
from xml.dom import minidom

import _pickle as cPickle
import numpy
import shortuuid
import yaml


from PIL import Image

# Get the score change from score_change
from hippogym_app.predict import get_score_change

# this is the Agent/Environment compo provided by the researcher
from hippogym_app.fingerprintAgent import FingerprintAgent


def load_config():
    logging.info("Loading Config in trial.py")
    with open(".trialConfig.yml", "r") as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info("Config loaded in trial.py")
    return config.get("trial")


class Trial:
    def __init__(self, pipe):
        self.config = load_config()
        self.pipe = pipe
        self.frameId = 0
        self.humanAction = 0
        self.episode = 0
        self.done = False
        self.play = False
        self.record = []
        self.nextEntry = {}
        self.trialId = shortuuid.uuid()
        self.outfile = None
        self.framerate = self.config.get("startingFrameRate", 30)
        self.userId = None
        self.projectId = self.config.get("projectId")
        self.filename = None
        self.path = None
        self.imagename = None  # Image name attribute for XML file output
        self.fingerprint = self.config.get("fingerprint", False)

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
        self.agent = FingerprintAgent()
        self.agent.start(self.config.get("game"))

    def run(self):
        """
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        """
        while not self.done:
            message = self.check_message()
            if message:
                self.handle_message(message)
            if self.play:
                self.take_step()
                render = self.get_render()
                self.send_render(render)
                self.play = False
            time.sleep(1 / self.framerate)

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
            if self.outfile:
                self.outfile.close()
                if self.config.get("s3upload"):
                    self.pipe.send(
                        {
                            "upload": {
                                "projectId": self.projectId,
                                "userId": self.userId,
                                "file": self.filename,
                                "path": self.path,
                                "bucket": self.config.get("bucket"),
                            }
                        }
                    )
            self.create_file()
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
        if self.config.get("dataFile") == "trial":
            self.save_record()
        if self.outfile:
            self.outfile.close()
            self.pipe.send(
                {
                    "upload": {
                        "projectId": self.projectId,
                        "userId": self.userId,
                        "file": self.filename,
                        "path": self.path,
                    }
                }
            )
        self.play = False
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
            except:
                message = {"error": "unable to parse message", "frameId": self.frameId}
            return message
        return None

    def handle_message(self, message: dict):
        """
        Reads messages sent from websocket, handles commands as priority then
        actions. Logs entire message in self.nextEntry
        """
        if not self.userId and "userId" in message:
            self.userId = message["userId"] or f"user_{shortuuid.uuid()}"
            self.send_ui()
            self.send_instructions(None)
            if self.fingerprint:
                self.send_fingerprint_config()
            self.reset()
            render = self.get_render()
            self.send_render(render)
            if self.fingerprint:
                self.send_expert()
        if "minutiaList" in message and message["minutiaList"] and message["command"]:
            self.handle_minutiae(message["command"], message["minutiaList"])
        elif "command" in message and message["command"]:
            self.handle_command(message["command"])
        elif "changeFrameRate" in message and message["changeFrameRate"]:
            self.handle_framerate_change(message["changeFrameRate"])
        elif "action" in message and message["action"]:
            self.handle_action(message["action"])
        self.update_entry(message)

    def handle_command(self, command: str):
        """
        Deals with allowable commands from user. To add other functionality
        add commands.
        """
        command = command.strip().lower()
        if command == "start":
            self.play = True
        elif command == "stop":
            self.end()
        elif command == "reset":
            self.reset()
        elif command == "pause":
            self.play = False
        elif command == "requestui":
            self.send_ui()
        elif command == "submitimage":
            self.play = True

    def handle_framerate_change(self, change: str):
        """
        Changes the framerate in either increments of step, or to a requested
        value within a minimum and maximum bound.
        """
        if not self.config.get("allowFrameRateChange"):
            return

        step = self.config.get("frameRateStepSize", 5)
        minFR = self.config.get("minFrameRate", 1)
        maxFR = self.config.get("maxFrameRate", 90)
        change = change.strip().lower()
        if change == "faster" and self.framerate + step < maxFR:
            self.framerate += step
        elif change == "slower" and self.framerate - step > minFR:
            self.framerate -= step
        else:
            try:
                requested = int(change)
                if requested > minFR and requested < maxFR:
                    self.framerate = requested
            except:
                pass

    def handle_action(self, action: str):
        """
        Translates action to int and resets action buffer if action !=0
        """
        action = action.strip().lower()
        actionSpace = self.config.get("actionSpace")
        if action in actionSpace:
            actionCode = actionSpace.index(action)
        else:
            actionCode = 0
        self.humanAction = actionCode

    def update_entry(self, update_dict: dict):
        """
        Adds a generic dictionary to the self.nextEntry dictionary.
        """
        self.nextEntry.update(update_dict)

    def get_render(self):
        """
        Calls the Agent/Environment render function which must return a npArray.
        Translates the npArray into a jpeg image and then base64 encodes the
        image for transmission in json message.
        """
        render = self.agent.render()

        # Get the image name from the rendered image path
        # from "Images/<filename>.bmp" get "<filename>"
        self.imagename = render[7:-4]

        try:
            img = Image.open(render)
            fp = BytesIO()
            img.save(fp, "BMP")  # Changes filetype to be BMP
            frame = base64.b64encode(fp.getvalue()).decode("utf-8")
            fp.close()
        except:
            raise TypeError(
                "Render failed. Is env.render('rgb_array') being called\
                            With the correct arguement?"
            )
        self.frameId += 1
        return {"frame": frame, "frameId": self.frameId}

    def send_render(self, render: dict):
        """
        Attempts to send render message to websocket
        """
        try:
            self.pipe.send(json.dumps(render))
        except:
            raise TypeError("Render Dictionary is not JSON serializable")

    def send_ui(self):
        defaultUI = ["left", "right", "up", "down", "start", "pause"]
        try:
            self.pipe.send(json.dumps({"UI": self.config.get("ui", defaultUI)}))
        except:
            raise TypeError("Render Dictionary is not JSON serializable")

    def send_instructions(self, instructions):
        if not instructions:
            instructions = self.config.get("instructions", None)
        if instructions:
            try:
                self.pipe.send(json.dumps({"Instructions": instructions}))
            except:
                return

    def send_fingerprint_config(self):
        max_score = self.config.get("maxScore")
        min_minutiae = self.config.get("minMinutiae")
        self.pipe.send(
            json.dumps(
                {
                    "Fingerprint": self.fingerprint,
                    "MaxScore": max_score,
                    "MinMinutiae": min_minutiae,
                }
            )
        )

    def get_score(self):
        # Get the score from the windows machine

        # For now, just sleep for 2 seconds and return a random score
        time.sleep(2)
        max_score = self.config.get("maxScore")
        return random.randint(0, max_score)

    def send_score(self, score):
        try:
            self.pipe.send(json.dumps({"Score": score}))
        except:
            return

    def send_expert(self):
        try:
            # Try to load in the first xml
            expert_1 = xmlToArray(f"Fingerprints/{self.imagename}.FingerNet.xml")
            # Try to load in the second xml
            expert_2 = xmlToArray(f"Fingerprints/{self.imagename}.MinutiaNet.xml")
            # Try to send it to front end
            self.pipe.send(
                json.dumps({"ExpertMarks1": expert_1, "ExpertMarks2": expert_2})
            )
        except:
            return

    def take_step(self):
        """
        Expects a dictionary return with all the values that should be recorded.
        Records return and saves all memory associated with this setp.
        Checks for DONE from Agent/Env
        """
        envState = self.agent.step(self.humanAction)
        self.update_entry(envState)
        self.save_entry()
        if envState["done"]:
            self.reset()
        else:
            # score = self.agent.get_score(self.xmlFilename)
            score = self.get_score()
            self.send_score(score)
        self.play = True

    def save_entry(self):
        """
        Either saves step memory to self.record list or pickles the memory and
        writes it to file, or both.
        Note that observation and render objects can get large, an episode can
        have several thousand steps, holding all the steps for an episode in
        memory can cause performance issues if the os needs to grow the heap.
        The program can also crash if the Server runs out of memory.
        It is recommended to write each step to file and not maintain it in
        memory if the full observation is being saved.
        comment/uncomment the below lines as desired.
        """
        if self.config.get("dataFile") == "trial":
            self.record.append(self.nextEntry)
        else:
            cPickle.dump(self.nextEntry, self.outfile)
            self.nextEntry = {}

    def save_record(self):
        """
        Saves the self.record object to file. Is only called if uncommented in
        self.end(). To record full trial records a line must also be uncommented
        in self.save_entry() and self.create_file()
        """
        cPickle.dump(self.record, self.outfile)
        self.record = []

    def create_file(self):
        """
        Creates a file to record records to. comment/uncomment as desired
        for episode or full-trial logging.
        """
        if self.config.get("dataFile") == "trial":
            filename = f"trial_{self.userId}"
        else:
            filename = f"episode_{self.episode}_user_{self.userId}"
        os.makedirs("Trials", exist_ok=True)
        path = os.path.join("Trials", filename)
        self.outfile = open(path, "ab")
        self.filename = filename
        self.path = path

    def handle_minutiae(self, command: str, minutiaList: list):
        """
        Creates a new XML file in the in the XML folder
        using the given minutia list
        """
        XMLstring = self.createXML(minutiaList)

        user = "Nadeen"
        filename = f"{self.imagename}"
        path = f"XML/{filename}.xml"
        self.xmlFilename = path

        try:
            XMLfile = open(path, "x")
            XMLfile.write(XMLstring)
            XMLfile.close()
        except OSError as e:
            # No such directory
            if e.errno == errno.ENOENT:
                os.makedirs("XML")  # create "XML" directory
            # File name already exists
            elif e.errno == errno.EEXIST:
                files = [file for file in os.listdir("XML") if filename in file]
                i = 1
                while filename + str(i) + ".xml" in files:
                    i += 1
                path = f"XML/{filename}{str(i)}.xml"

            XMLfile = open(path, "x")
            XMLfile.write(XMLstring)
            XMLfile.close()

        if command == "getFeedback":
            score_change = get_score_change(path)
            self.pipe.send(json.dumps({"ScoreChange": score_change}))

        self.play = True

    def createXML(self, minutiae: list):
        """
        Creates and returns an XML string with the following structure:
            <MinutiaeList>
                <Minutia X="313" Y="381" Angle="342.0" Type="End" />
                ...
            </MinutiaeList>
        """
        minutiaeList = ET.Element("MinutiaeList")

        for minutia in minutiae:
            ET.SubElement(
                minutiaeList,
                "Minutia",
                {
                    "X": str(minutia["x"]).split(".")[0],
                    "Y": str(minutia["y"]).split(".")[0],
                    "Angle": str(minutia["orientation"]),
                    "Type": str(minutia["type"]),
                },
            )

        tab_length = ""  # defining tab length to be 4 spaces
        rough_string = ET.tostring(minutiaeList)
        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent=tab_length)


def xmlToArray(path):
    tree = ET.parse(path)
    root = tree.getroot()
    score = root.attrib["Score"]
    minutiae = []
    for child in root:
        minutiae.append(
            {
                "x": int(child.attrib["X"]),
                "y": int(child.attrib["Y"]),
                "orientation": float(child.attrib["Angle"].replace(",", ".")),
            }
        )
    return {"score": int(score), "minutiae": minutiae}
