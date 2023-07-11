import string
import numpy, json, shortuuid, time, base64, yaml, logging, os, xml.etree.ElementTree as ET, errno
import _pickle as cPickle
from xml.dom import minidom

from io import BytesIO
#from agent import Agent # this is the Agent/Environment compo provided by the researcher

# Get the score change from score_change
from predict import get_score_change
import asyncio
import websockets
import json


# for dummy score
import random

def load_config():
    logging.info('Loading Config in trial.py')
    with open('.trialConfig.yml', 'r') as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info('Config loaded in trial.py')
    return config.get('trial')

class Trial():

    def __init__(self, connection_url):
        self.config = load_config()
        self.trialData = None
        self.data = None
        self.count = 1
        self.connection_url = connection_url
        self.websocket = None
        # self.humanAction = 0
        self.episode = 0
        self.done = False
        self.play = False
        self.record = []
        self.nextEntry = {}
        self.trialId = shortuuid.uuid()
        self.outfile = None
        # self.framerate = self.config.get('startingFrameRate', 30)
        self.userId = None
        self.projectId = self.config.get('projectId')
        self.filename = None

        self.selectedRanGraphs = []
        self.passedHeader = 0

        self.start()
        self.run()

    async def connect(self):
        retries = 0
        while retries < 5:
            try:
                async with websockets.connect(self.connection_url) as ws:
                    self.websocket = ws
                    print("Connected to WebSocket address")
                    await self.run()

            except Exception as e:
                print(f"Failed to connect: {e}")
                retries += 1
                await asyncio.sleep(1)  # wait a bit before retrying






    def start(self):
        '''
        Call the function in the Agent/Environment combo required to start 
        a trial. By default passes the environment name that will be passed
        to gym.make(). 
        By default this expects the openAI Gym Environment object to be
        returned. 
        '''
        # populate random graph selection
        ranNum = random.randint(23, 42)
        self.selectedRanGraphs.append(ranNum)
        ranNum = random.randint(23, 42)
        while ranNum == self.selectedRanGraphs[0]:
            ranNum = random.randint(23, 42)
        self.selectedRanGraphs.append(ranNum)

        #self.agent = Agent()
        #self.agent.start(self.config.get('game'))

    async def run(self):
        '''
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        '''
        self.create_file()
        while not self.done:
            message = await self.check_message()
            if message:
                await self.handle_message(message)


    async def reset(self):
        '''
        Resets the OpenAI gym environment to start a new episode.
        By default this function will create a new log file for every
        episode, if the intention is to log only full trials then
        comment the 3 lines below contianing self.outfile and 
        self.create_file.
        '''
        if self.check_trial_done():
            print("check_trial_done successful")
            self.end()
        else:
            #self.agent.reset()
            if self.outfile:
                print("self.outfile successful")
                self.outfile.close()
                # if self.config.get('s3upload'):
                #     self.pipe.send({'upload':{'projectId':self.projectId ,'userId':self.userId,'file':self.filename,'path':self.path, 'bucket': self.config.get('bucket')}})
            self.create_file()
            self.episode += 1
            print('self.episode', self.episode)

    def check_trial_done(self):
        '''
        Checks if the trial has been completed and can be quit. Add conditions
        as required.
        '''
        print('maxEpisodes', self.config.get('maxEpisodes', 20))
        return self.episode >= self.config.get('maxEpisodes', 20)

    async def end(self):
        '''
        Closes the environment through the agent, closes any remaining outfile
        and sends the 'done' message to the websocket pipe. If logging the 
        whole trial memory in self.record, uncomment the call to self.save_record()
        to write the record to file before closing.
        '''
        
        await self.websocket.send(json.dumps('done'))
        #self.agent.close()
        if self.config.get('dataFile') == 'trial':
            self.save_record()
        if self.outfile:
            self.outfile.close()
            await self.websocket.send({'upload':{'projectId':self.projectId,'userId':self.userId,'file':self.filename,'path':self.path}})
        self.play = False
        self.done = True

    async def check_message(self):
        '''
        Checks pipe for messages from websocket, tries to parse message from
        json. Returns message or error message if unable to parse json.
        Expects some poorly formatted or incomplete messages.
        '''
        if self.websocket:
            message = await self.websocket.recv()
            try:
                message = json.loads(message)
                print("check_message function recieved: ", message)
            except:
                message = {'error': 'unable to parse message', 'frameId': self.frameId}
            return message
        return None


    async def handle_message(self, message:dict):
        '''
        Reads messages sent from websocket, handles commands as priority then 
        actions. Logs entire message in self.nextEntry
        '''
        print("handle_message function: ", message)
        if not self.userId and 'userId' in message:
            self.userId = message['userId'] or f'user_{shortuuid.uuid()}'
            print("self.userID is now = ", self.userId)
            with open('./data/trialData.json') as json_file:
                self.trialData = json.load(json_file)
            await self.send_ui()
        if 'command' in message and message['command']:
            await self.handle_command(message)
        elif 'save' in message and message['save']:
            self.nextEntry = message['save']
            print("self.nextEntry: ",self.nextEntry)
            self.save_entry()


    async def handle_command(self, message):
        '''
        Deals with allowable commands from user. To add other functionality
        add commands.
        '''
        command = message['command'].strip().lower()
        print("handle_command function: ", command)
        if command == 'get next':
            if self.count > 1:
                try:
                    print("sending.. :" , {'action': 'command','VALUES': self.data['qs'][message['info']]})
                    await self.websocket.send(json.dumps({'action': 'command','VALUES': self.data['qs'][message['info']]}))
                except:
                    raise TypeError("Render Dictionary is not JSON serializable")
        elif command == 'new game' and self.count < 43:
            self.count+=1
            print("self.count has been incremented: ", self.count)
            await self.send_ui()
            await self.reset()
            #if (self.count != 3 and self.passedHeader != 0) or (self.count != 23 and self.passedHeader!=1):
            # print('self.passedHeader', self.passedHeader)
            # print('self.count', self.count)
            # print('self.passedHeader != 0', self.passedHeader != 0)
            # print('self.count != 3', self.count != 3)
            # print('self.count != 23 ', self.count != 23 )
            # print('self.passedHeader!=1', self.passedHeader!=1)
            #if (self.count != 3 and self.passedHeader != 0) or (self.count != 23 and self.passedHeader!=1):
                #print("resetting env....")
            
        elif command == 'resume' and self.count < 43:
            await self.send_ui()
        elif self.count >= 43:
            print("IN HEREEEEE")
            self.end()

    async def send_ui(self):
        if (self.count == 3 and self.passedHeader == 0) or (self.count == 23 and self.passedHeader == 1):
            print("header sending..")
            if(self.count == 3):
                message = "This next section is the training section"
                print("message: ", message)
            else:
                message = "This next section is the testing section"
                print("message: ", message)
            try:
                print("sending.. :" , {'action': 'UI','HEADER': message})
                await self.websocket.send(json.dumps({'action': 'UI','HEADER': message}))
                self.passedHeader +=1
            except:
                raise TypeError("Render Dictionary is not JSON serializable")
        else:
            print("sending ui.." + str(self.count))
            feedback = "feedback"
            if self.count <= 2 or self.count >= 23:
                feedback = None

            ctest = None
            if self.count <=2:
                ctest = "CTEST"
            if self.count == self.selectedRanGraphs[0] or self.count == self.selectedRanGraphs[1]:
                ctest = "CTEST"

            if(self.count == 1 or self.count == 43):
                print("self.count is 1 or 43")
                print('self.count', self.count)
                self.data = self.trialData[str(self.count)]
                print('self.data', self.data)
                try:          
                    print("sending... ",{"action": 'UI', 'UI': self.data, "CTEST": "CTEST"} )
                    await self.websocket.send(json.dumps({"action": 'UI', 'UI': self.data, "CTEST": "CTEST"}))
                except:
                    raise TypeError("Render Dictionary is not JSON serializable")
            else:
                print('self.count', self.count)
                self.data = self.trialData[str(self.count)]
                #print('self.data', self.data)
                with open('data/increasing_prs.json') as json_file:
                    data = json.load(json_file)
                    
                    for group in data:
                        print('group', group['trial_id'])
                        if group['trial_id'] == self.data:
                            print('USING TRIAL', group['trial_id'])
                            self.data = group
                try:
                    print("sending.. :" , {'action': 'UI','UI': self.data['stateRewards'], 'OPT_ACT': self.data['opt_act'], 'FEEDBACK': feedback, "CTEST": ctest})
                    await self.websocket.send(json.dumps({'action': 'UI','UI': self.data['stateRewards'], 'OPT_ACT': self.data['opt_act'], 'FEEDBACK': feedback, "CTEST": ctest}))
                except:
                    raise TypeError("Render Dictionary is not JSON serializable")


    def save_entry(self):
        '''
        Either saves step memory to self.record list or pickles the memory and
        writes it to file, or both.
        Note that observation and render objects can get large, an episode can
        have several thousand steps, holding all the steps for an episode in 
        memory can cause performance issues if the os needs to grow the heap.
        The program can also crash if the Server runs out of memory. 
        It is recommended to write each step to file and not maintain it in
        memory if the full observation is being saved.
        comment/uncomment the below lines as desired.
        '''
        if self.config.get('dataFile') == 'trial':
            self.record.append(self.nextEntry)
        else:
            cPickle.dump(self.nextEntry, self.outfile)
            self.nextEntry = {}

    def save_record(self):
        '''
        Saves the self.record object to file. Is only called if uncommented in
        self.end(). To record full trial records a line must also be uncommented
        in self.save_entry() and self.create_file()
        '''
        cPickle.dump(self.record, self.outfile)
        self.record = []

    def create_file(self):
        '''
        Creates a file to record records to. comment/uncomment as desired 
        for episode or full-trial logging.
        '''
        
        if self.config.get('dataFile') == 'trial':
            filename = f'trial_{self.userId}'
        else:
            filename = f'episode_{self.episode}_user_{self.userId}'

        path = 'Trials/'+filename
        try:
            
            self.outfile = open(path, 'ab')
        except:
            os.makedirs('Trials')
            self.outfile = open(path, 'ab')
            print('saved')
        self.filename = filename
        self.path = path
        print(f"created a file at: {filename}")

async def main():
    trial = Trial('wss://x4v1m0bphh.execute-api.ca-central-1.amazonaws.com/production?connection_type=backend')
    await trial.connect()
    await trial.run()

asyncio.run(main())