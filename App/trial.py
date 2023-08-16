import numpy, json, shortuuid, time, base64, yaml, logging, os, xml.etree.ElementTree as ET, errno
from websocket import Websocket
import asyncio
import json
import os
import boto3
import random


TAG = "\033[1;35m[HIPPOGYM]\033[0m" 

def load_config():
    print(f'{TAG} Loading config from .trialConfig.yml...')
    with open('.trialConfig.yml', 'r') as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    print(f'{TAG} Config loaded')
    return config.get('trial')

class Trial():
    def __init__(self):
        print(f'{TAG} Initializing Trial...')
        self.config = load_config()
        self.trialData = None
        self.data = None
        self.count = 1
        self.websocket = Websocket() # If you wish to specify your own websocket server use it as param
        self.episode = 0
        self.done = False
        self.play = False
        self.record = []
        self.nextEntry = {}
        self.trialId = shortuuid.uuid()
        self.outfile = None
        self.userId = None
        self.projectId = self.config.get('projectId')
        self.filename = None
        self.selectedRanGraphs = []
        self.passedHeader = 0

    async def connect(self):
        await self.websocket.connectClient()
        if self.websocket.websocket is not None:
            print(f"{TAG} Connected to WebSocket address")
            await self.start()

    async def start(self):
        self.start_trial()
        await self.run()

    async def start(self):
        self.start_trial()
        await self.run()

    def start_trial(self):
        '''
        Call the function in the Agent/Environment combo required to start 
        a trial. By default passes the environment name that will be passed
        to gym.make(). 
        By default this expects the openAI Gym Environment object to be
        returned. 
        '''
        print(f'{TAG} Starting trial...')
        # populate random graph selection
        ranNum = random.randint(23, 42)
        self.selectedRanGraphs.append(ranNum)
        ranNum = random.randint(23, 42)
        while ranNum == self.selectedRanGraphs[0]:
            ranNum = random.randint(23, 42)
        self.selectedRanGraphs.append(ranNum)

    async def run(self):
        '''
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        '''
        print(f'{TAG} Running trial...')
        while not self.done:
            message = await self.websocket.recieveData()
            await self.handle_message(message)

    async def check_done(self):
        '''
        Check if self.done is set to True. If so, save the data and disconnect from the websocket.
        '''
        if self.done:
            await self.websocket.disconnectClient()

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
            await self.end()
        else:
            self.episode += 1
            print(f'{TAG} self.episode has been incremented...', self.episode)

    def check_trial_done(self):
        '''
        Checks if the trial has been completed and can be quit. Add conditions
        as required.
        '''
        return self.episode >= self.config.get('maxEpisodes', 20)

    async def end(self):
        '''
        Closes the environment through the agent, closes any remaining outfile
        and sends the 'done' message to the websocket pipe. If logging the 
        whole trial memory in self.record, uncomment the call to self.save_record()
        to write the record to file before closing.
        '''
        print(f"{TAG} Sending to websocket... :" , "DONE",{"done":"done"})
        await self.websocket.sendData("DONE",{"message":"done"})
        self.play = False



    async def handle_message(self, message:dict):
        '''
        Reads messages sent from websocket, handles commands as priority then 
        actions. Logs entire message in self.nextEntry
        '''
        print(f"{TAG} handle_message function has recieved: ", message)
        if not self.userId and 'userId' in message:
            self.userId = message['userId'] or f'user_{shortuuid.uuid()}'
            self.websocket.setID(self.userId)
            self.projectId = message['projectId']
            print(f"{TAG} self.userID is now = ", self.userId)
            print(f"{TAG} self.projectID is now = ", self.projectId)
            with open('./data/trialData.json') as json_file:
                self.trialData = json.load(json_file)
            await self.send_ui()
        if 'command' in message and message['command']:
            await self.handle_command(message)
        elif 'save' in message and message['save']:
            self.nextEntry = message['save']
            print(f"{TAG} saving data in self.nextEntry: ...",self.nextEntry)
            self.save_data()
            self.done = True # if we recieve the save message, then trial is done for now, change later to conditional
        await self.check_done()

    def save_data(self):
        s3upload = self.config.get('s3upload')
        fileName = f'{self.projectId}_{self.userId}.json'
        if s3upload:
            print(f"{TAG} S3 UPLOAD DETECTED... UPLOADING NOW....")
            s3 = boto3.client('s3')
            data_json = json.dumps(self.nextEntry)
            # Convert the JSON string to bytes
            data_bytes = data_json.encode('utf-8')
            bucket = self.config.get('bucket')
            # Upload the file to S3
            try:
                s3.put_object(Body=data_bytes, Bucket=bucket, Key=fileName)
            except:
                print(f"{TAG} S3 UPLOAD FAILED....")
                
        if not os.path.exists('Trials'):
             os.makedirs('Trials')
        
        file_path = os.path.join('Trials', fileName)
        with open(file_path, "w") as outfile:
            json.dump(self.nextEntry, outfile, indent = 2)


    async def handle_command(self, message):
        '''
        Deals with allowable commands from user. To add other functionality
        add commands.
        '''
        command = message['command'].strip().lower()
        print(f"{TAG} handle_command function: ", command)
        if command == 'get next':
            if self.count > 1:
                try:
                    await self.websocket.sendData('command',{'VALUES': self.data['qs'][message['info']]})
                except:
                    raise TypeError("Render Dictionary is not JSON serializable") # Change later
        elif command == 'new game' and self.count < 43:
            self.count+=1
            print(f"{TAG} self.count has been incremented... ", self.count)
            await self.send_ui()
            await self.reset()
        elif command == 'resume' and self.count < 43:
            await self.send_ui()
        elif self.count >= 43:
            print(f"{TAG} self.count is now greater then 43, ending...")
            await self.end()

    async def send_ui(self):
        if (self.count == 3 and self.passedHeader == 0) or (self.count == 23 and self.passedHeader == 1):
            print(f"{TAG} send_ui header sending....")
            if(self.count == 3):
                message = "This next section is the training section"
                print(f"{TAG} self.count == 3 so message: ", message)
            else:
                message = "This next section is the testing section"
                print(f"{TAG} self.count =! 3 so message: ", message)
            try:
                print(f"{TAG} Sending to websocket... :" , {'action': 'UI','HEADER': message})
                await self.websocket.sendData('UI',{'HEADER': message})
                self.passedHeader +=1
            except:
                raise TypeError("Render Dictionary is not JSON serializable")
        else:
            print(f"{TAG} sending ui with our count as ..." + str(self.count))
            feedback = "feedback"
            if self.count <= 2 or self.count >= 23:
                feedback = None

            ctest = None
            if self.count <=2:
                ctest = "CTEST"
            if self.count == self.selectedRanGraphs[0] or self.count == self.selectedRanGraphs[1]:
                ctest = "CTEST"

            if(self.count == 1 or self.count == 43):
                print(f'{TAG} self.count', self.count)
                self.data = self.trialData[str(self.count)]
                try:          
                    print(f"{TAG} Sending to websocket... :",{"action": 'UI', 'UI': self.data, "CTEST": "CTEST"} )
                    await self.websocket.sendData('UI', {'UI': self.data, "CTEST": "CTEST"})
                except:
                    raise TypeError("Render Dictionary is not JSON serializable")
            else:
                print(f'{TAG} self.count is now ....', self.count)
                self.data = self.trialData[str(self.count)]
                with open('data/increasing_prs.json') as json_file:
                    data = json.load(json_file)
                    for group in data:
                        if group['trial_id'] == self.data:
                            print(f'{TAG} USING TRIAL...', group['trial_id'])
                            self.data = group
                try:
                    print(f"{TAG} Sending to websocket... :" , {'action': 'UI','UI': self.data['stateRewards'], 'OPT_ACT': self.data['opt_act'], 'FEEDBACK': feedback, "CTEST": ctest})
                    await self.websocket.sendData('UI', {'UI': self.data['stateRewards'], 'OPT_ACT': self.data['opt_act'], 'FEEDBACK': feedback, "CTEST": ctest})
                except:
                    raise TypeError("Render Dictionary is not JSON serializable")

async def main():
    trial = Trial()
    await trial.connect()

if __name__ == '__main__':
    asyncio.run(main())