import numpy, json, shortuuid, time, base64, yaml, logging, os, xml.etree.ElementTree as ET, errno
from websocket import Websocket
import asyncio
import json
import os
import boto3
import random
from agent import Agent # this is the Agent/Environment compo provided by the researcher
from PIL import Image
from io import BytesIO

"""Press Start
Shows first demo.
Right arrow or right UI button, gives next demo. But have to press start to show it.
Right arrow or right UI button, gives previous demo. But have to press start to show it.
"""

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
        self.nextEntry = {}
        self.trialId = shortuuid.uuid()
        self.outfile = None
        self.userId = None
        self.projectId = self.config.get('projectId')
        self.show_demo = None
        self.total_reward = 0
        self.demo_idx = 1
        self.action = 'noop'
        self.modality = self.config.get('modality')
        self.framerate = self.config.get('startingFrameRate', 30)
        self.frameId = 0
        
    async def connect(self):
        await self.websocket.connectClient()
        if self.websocket.websocket is not None:
            print(f"{TAG} Connected to WebSocket address")
            await self.start()

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


        if self.modality == 'feedback':
            from tamerAgent import TamerAgent
            self.agent = TamerAgent()

        elif self.modality == 'pref':
            from agent import Agent
            self.agent = Agent()

        elif self.modality == 'demo':
            from agent import Agent
            self.agent = Agent()


        self.agent.start(self.config.get('game'))
        actionSpace = self.config.get('actionSpace')
        self.agent.reset()
        #self.start_trial()

    async def run(self):
        '''
        This is the main event controlling function for a Trial.
        It handles the render-step loop
        '''
        print(f'{TAG} Running trial...')
        while not self.done:
            message = await self.websocket.recieveData()
            await self.handle_message(message)
            print('waiting for messages')

            if self.play:
                #print('self.play', self.play)

                if self.modality == 'pref':
                    await self.render_policy()
                
                else:
                    render = await self.get_render()
                    await self.send_render(render)
                    self.take_step()
                    time.sleep(1/self.framerate)



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

# """trial.py:260: RuntimeWarning: coroutine 'Trial.end' was never awaited
# """

    async def handle_message(self, message:dict):
        '''
        Reads messages sent from websocket, handles commands as priority then 
        actions. Logs entire message in self.nextEntry
        '''
        print(f"{TAG} handle_message function has recieved: ", message)
        print('inside handle message', message)
        print('if KeyBoardEvent in message','KeyBoardEvent' in message )
        print(message.keys())
        print(list(message.keys()))
        # if 'action' in list(message.keys()):
        #     print(message['KeyboardEvent'])
        # if 'KeyBoardEvent' in list(message.keys()):
        #     print('message[KeyboardEvent]', message['KeyboardEvent'])

        if not self.userId and 'userId' in message:
            self.userId = message['userId']
            self.websocket.setID(self.userId)
            self.projectId = message['projectId']
            print(f"{TAG} self.userID is now = ", self.userId)
            print(f"{TAG} self.projectID is now = ", self.projectId)
            with open('./data/trialData.json') as json_file:
                self.trialData = json.load(json_file)
            await self.send_ui()

        if 'action' in message and message['action'] == 'command':
            print(f'{TAG} commmand in message recieved.')
            try:
            #if message['KeyboardEvent']:
                print('got key board input')
                await self.handle_key_board_events(message['KeyboardEvent'])
            except:
                print('got a different command')
                await self.handle_command(message)
        # if 'KeyBoardEvent' in message and message['KeyboardEvent']:
        #     print(f'{TAG} commmand in message recieved.')
        #     await self.handle_key_board_events(message)

        # if 'command' in message and message['command']:
        #     print(f'{TAG} commmand in message recieved.')
        #     await self.handle_command(message)
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

    async def handle_key_board_events(self, message):
        print('handle_key_board_event message', message)
        #command = message['KeyboardEvent'].strip().lower()
        print(f"{TAG} handle_key_board_event function: ", message)
        key = list(message.keys())[0]
        #print('key',key)
        value = message[key][0]
        self.handle_action(value)
        print('value', value)
    

    async def handle_command(self, message):
        '''
        Deals with allowable commands from user. To add other functionality
        add commands.
        '''
        print('message', message)
        command = message['command'].strip().lower()
        print(f"{TAG} handle_command function: ", command)
        print('Pass this?')
        if command == 'start':
                self.play = True
                if self.action == 'increase':
                    self.demo_idx+=1
                elif self.action == 'decrease':
                    self.demo_idx-=1

                print('using demo', self.demo_idx)
                    
                # if self.modality == 'pref':
                #     self.show_demo = True
                # #await self.render_all_frames()
                # #await self.render_policy()
        elif command == 'stop':
            self.end()
        elif command == 'reset':
            self.reset()
        elif command == 'pause':
            self.play = False
        elif command == 'requestUI':
            self.send_ui()
        elif command == 'good' or command == 'bad':
            self.handle_feedback(command)
            self.handle_pref(command)



    async def render_all_frames(self):
        while self.play:
            render = await self.get_render()
            await self.send_render(render)
            await asyncio.sleep(10)  # Sleep for 10 seconds
            # await asyncio.sleep(1 / self.framerate)  # Sleep to control framerate
            

            
    
    def handle_action(self, action:str):
        '''
        Translates action to int and resets action buffer if action !=0
        '''
        #action = action.strip().lower()
        print(action)
        if self.modality == 'pref':
            if action == 'ArrowRight':
                self.action = 'increase'
                #self.demo_idx+=1
                #self.play=True
            elif action == 'ArrowLeft':
                self.action = 'decrease'
                #self.demo_idx-=1
                #self.play=True

        elif self.modality == 'demo':
            self.action = 0
            if action == 'KEYDOWN':
                #print('USER: GOOD')
                self.action = '0'

            elif action == 'ArrowRight':
                #print('USER: GOOD')
                self.action = 2
            elif action == 'ArrowLeft':
                self.action = 1

        #add to array 
    def handle_feedback(self, feedback:str):
        '''
        Translates action to int and resets action buffer if action !=0
        '''
        feedback = feedback.strip().lower()
        self.humanfeedback = "None"
        if feedback == 'good':
            #print('USER: GOOD')
            self.humanfeedback = 'good'
        elif feedback == 'bad':
            self.humanfeedback = 'bad'
    def handle_feedback(self, feedback:str):
        '''
        Translates action to int and resets action buffer if action !=0
        '''
        feedback = feedback.strip().lower()
        self.humanfeedback = "None"
        if feedback == 'good':
            #print('USER: GOOD')
            self.humanfeedback = 'good'
        elif feedback == 'bad':
            self.humanfeedback = 'bad'
    def handle_pref(self, feedback:str):
        '''
        Translates action to int and resets action buffer if action !=0
        '''
        feedback = feedback.strip().lower()
        self.human_pref = "None"
        if feedback == 'good':
            #print('USER: GOOD')
            self.human_pref = 'good'
        elif feedback == 'bad':
            self.human_pref = 'bad'

        self.nextEntry = {'preference':[self.demo_idx, self.human_pref]}
        print(self.nextEntry)
        self.save_data()

    async def get_render(self):
        '''
        Calls the Agent/Environment render function which must return a npArray.
        Translates the npArray into a jpeg image and then base64 encodes the 
        image for transmission in json message.
        '''
        #print('inside get render')
       
        # self.agent.reset()
        render = self.agent.render()
        #print('render', render)
        try:
            
            img = Image.fromarray(render)
            fp = BytesIO()
            img.save(fp,'JPEG')
            frame = base64.b64encode(fp.getvalue()).decode('utf-8')
            fp.close()
        except: 
            raise TypeError("Render failed. Is env.render('rgb_array') being called\
                            With the correct arguement?")
        self.frameId += 1
        #print('got the render', frame, self.frameId)
        return {'frame': frame, 'frameId': self.frameId}
      
    async def send_ui(self):
        defaultUI = ['left','right','up','down','start','pause']
        try:
            print( self.config.get('ui', defaultUI))
            await self.websocket.sendData('UI', {'UI': self.config.get('ui', defaultUI)})
            render = await self.get_render()
            await self.send_render(render)
        except:
            raise TypeError("Render Dictionary is not JSON serializable")

    async def send_render(self, render:dict):
        await self.websocket.sendData('UI', {'env':render})

    async def take_step(self):
        '''
        Expects a dictionary return with all the values that should be recorded.
        Records return and saves all memory associated with this setp.
        Checks for DONE from Agent/Env
        '''
        if self.modality == 'feedback':
            print('self.humanfeedback', self.humanfeedback)
            done = self.agent.step(self.humanfeedback)

        elif self.modality == 'demo':
            print('self.humanAction', self.humanAction)
            done = self.agent.step(self.humanAction)

        

        if done:
            self.reset()
 

    async def render_policy(self):

        
        demo = self.agent.replay_buffer_of_demos[self.demo_idx]
        print(demo)
        print('len of demo', len(demo))
        #print(self.agent.short_replay_buffer_of_demos[1])
        #print('type of demo', type(demo))
        print('demo number', self.demo_idx)
        print('just reset the agent env')
        self.agent.reset()
        
        print('len of demo', len(demo))
        for idx, action in enumerate(demo):
            print(demo)
            print(f'idx {idx} out of {len(demo)}')
            print(action)
            done = self.agent.step(action)
            #print(envState, type(envState))
            # self.update_entry(envState)
            # self.save_entry()
            render = await self.get_render()
            await self.send_render(render)
            time.sleep(1/self.framerate)
            if done:
                break
            # if envState['done']:
            #     print('done')
            #     break
        self.play = False
        print('self.play is now False')
async def main():
    trial = Trial()
    await trial.connect()

if __name__ == '__main__':
    asyncio.run(main())