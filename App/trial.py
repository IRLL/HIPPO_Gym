import os, numpy, json, shortuuid, time, base64, yaml, logging
import _pickle as cPickle
from PIL import Image
from io import BytesIO
from optionAgent import CraftingAgent # this is the Agent/Environment compo provided by the researcher
from hippo_pygame import PyGameMessageHandler

def load_config():
    logging.info('Loading Config in trial.py')
    try:
        with open('.trialConfig.yml', 'r') as infile:
            config = yaml.load(infile, Loader=yaml.FullLoader)
    except FileNotFoundError:
        with open(os.path.join('App', '.trialConfig.yml'), 'r') as infile:
            config = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info('Config loaded in trial.py')
    return config.get('trial')


class Trial():

    def __init__(self, pipe):
        self.config = load_config()
        self.pipe = pipe
        self.frameId = 0
        self.humanAction = None
        self.episode = 0
        self.done = False
        self.play = False
        self.record = []
        self.nextEntry = {}
        self.trialId = shortuuid.uuid()
        self.outfile = None
        self.framerate = self.config.get('startingFrameRate', 30)
        self.userId = None
        self.projectId = self.config.get('projectId')
        self.filename = None
        self.path = None

        self.start()
        self.run()

    def start(self):
        '''
        Call the function in the Agent/Environment combo required to start 
        a trial. By default passes the environment name that will be passed
        to gym.make(). 
        By default this expects the openAI Gym Environment object to be
        returned. 
        '''
        self.agent = CraftingAgent()
        self.message_handler = PyGameMessageHandler(self)
        self.agent.start(self.config.get('game'))

    def run(self):
        '''
        This is the main event controlling function for a Trial. 
        It handles the render-step loop
        '''
        while not self.done:
            message = self.check_message()
            if message:
                self.message_handler.handle_message(message)
                self.update_entry(message)
            if self.play:
                render = self.get_render()
                self.send_render(render)
                if self.humanAction is not None:
                    self.take_step()
                    self.humanAction = self.config.get('defaultAction')
            time.sleep(1/self.framerate)

    def reset(self):
        '''
        Resets the OpenAI gym environment to start a new episode.
        By default this function will create a new log file for every
        episode, if the intention is to log only full trials then
        comment the 3 lines below contianing self.outfile and 
        self.create_file.
        '''
        if self.check_trial_done():
            self.end()
        else:
            self.agent.reset()
            if self.outfile:
                self.outfile.close()
                if self.config.get('s3upload'):
                    self.pipe.send({
                        'upload': {'projectId':self.projectId, 'userId':self.userId,
                            'file':self.filename, 'path':self.path,
                            'bucket': self.config.get('bucket')}
                    })
            self.create_file()
            self.episode += 1

    def check_trial_done(self):
        '''
        Checks if the trial has been completed and can be quit. Add conditions
        as required.
        '''
        return self.episode >= self.config.get('maxEpisodes', 20)

    def end(self):
        '''
        Closes the environment through the agent, closes any remaining outfile
        and sends the 'done' message to the websocket pipe. If logging the 
        whole trial memory in self.record, uncomment the call to self.save_record()
        to write the record to file before closing.
        '''
        self.pipe.send('done')
        self.agent.close()
        if self.config.get('dataFile') == 'trial':
            self.save_record()
        if self.outfile:
            self.outfile.close()
            self.pipe.send({'upload':{
                'projectId':self.projectId,'userId':self.userId,
                'file':self.filename,'path':self.path}})
        self.play = False
        self.done = True

    def check_message(self):
        '''
        Checks pipe for messages from websocket, tries to parse message from
        json. Retruns message or error message if unable to parse json.
        Expects some poorly formatted or incomplete messages.
        '''
        if self.pipe.poll():
            message = self.pipe.recv()
            try:
                message = json.loads(message)
            except:
                message = {'error': 'unable to parse message', 'frameId': self.frameId}
            return message
        return None

    def update_entry(self, update_dict:dict):
        '''
        Adds a generic dictionary to the self.nextEntry dictionary.
        '''
        self.nextEntry.update(update_dict)

    def get_render(self):
        '''
        Calls the Agent/Environment render function which must return a npArray.
        Translates the npArray into a jpeg image and then base64 encodes the 
        image for transmission in json message.
        '''
        render = self.agent.render()
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
        return {'frame': frame, 'frameId': self.frameId}

    def send_render(self, render:dict=None):
        '''
        Attempts to send render message to websocket
        '''
        if render is None:
            render = self.get_render()
        try: 
            self.pipe.send(json.dumps(render))
        except:
            raise TypeError("Render Dictionary is not JSON serializable")

    def send_ui(self):
        defaultUI = ['left','right','up','down','start','pause']
        try:
            self.pipe.send(json.dumps({'UI': self.config.get('ui', defaultUI)}))
        except:
            raise TypeError("Render Dictionary is not JSON serializable")

    def send_variables(self):
        try:
            self.pipe.send(json.dumps(self.config.get('variables')))
        except:
            return

    def take_step(self):
        '''
        Expects a dictionary return with all the values that should be recorded.
        Records return and saves all memory associated with this setp.
        Checks for DONE from Agent/Env
        '''
        envState = self.agent.step(self.humanAction)
        self.update_entry(envState)
        self.save_entry()
        if envState['done']:
            self.reset()

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
        path = 'Trials/' + filename
        if not os.path.exists('Trials'):
            os.makedirs('Trials')
        self.outfile = open(path, 'ab')
        self.filename = filename
        self.path = path
