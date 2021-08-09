from crafting import MineCraftingEnv
from crafting.render.render import get_human_action
from crafting.examples.minecraft.tasks import TASKS

from App.agents import Agent

class CraftingAgent(Agent):
    '''
    Use this class as a convenient place to store agent state.
    '''

    def start(self, config:dict) -> None:
        ''' Starts the Agent's environment.
        Args:
            config: trial config.
        '''
        game = config.get('game')
        if game == 'minecrafting':
            task_name = list(TASKS.keys())[config.get('task_number')]
            self.env = MineCraftingEnv(tasks=[task_name], tasks_can_end=[True], max_step=100)

    def handle_events(self, events):
        action = get_human_action(self.env, additional_events=events,
            can_be_none=True, **self.env.render_variables)
        if action:
            action = self.env.action(*action)
        return action

    def step(self, action:int):
        '''
        Takes a game step.
        Caller: 
            - Trial.take_step()
        Inputs:
            - env (Type: OpenAI gym Environment)
            - action (Type: int corresponding to action in env.action_space)
        Returns:
            - envState (Type: dict containing all information to be recorded for future use)
              change contents of dict as desired, but return must be type dict.
        '''
        observation, reward, done, info = self.env.step(action)
        envState = {'observation': observation, 'reward': reward, 'done': done, 'info': info}
        return envState

    def render(self):
        '''
        Gets render from gym.
        Caller:
            - Trial.get_render()
        Inputs:
            - env (Type: OpenAI gym Environment)
        Returns:
            - return from env.render('rgb_array') (Type: npArray)
              must return the unchanged rgb_array
        '''
        return self.env.render('rgb_array')
    
    def reset(self):
        '''
        Resets the environment to start new episode.
        Caller: 
            - Trial.reset()
        Inputs:
            - env (Type: OpenAI gym Environment)
        Returns: 
            No Return
        '''
        self.env.reset()
    
    def close(self):
        '''
        Closes the environment at the end of the trial.
        Caller:
            - Trial.close()
        Inputs:
            - env (Type: OpenAI gym Environment)
        Returns:
            No Return
        '''
        self.env.close()
