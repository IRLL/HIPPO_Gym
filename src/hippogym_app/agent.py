from PIL import Image


class Agent:
    """
    Use this class as a convenient place to store agent state.
    """

    def start(self, game: str):
        """
        Starts an OpenAI gym environment.
        Caller:
            - Trial.start()
        Inputs:
            -   game (Type: str corresponding to allowable gym environments)
        Returs:
            - env (Type: OpenAI gym Environment as returned by gym.make())
            Mandatory
        """
        f = open("images/imgnames.txt", "r")
        self.imgnames = f.read().split("\n")
        f.close()
        self.count = 0
        return

    def step(self, action: int):
        """
        Takes a game step.
        Caller:
            - Trial.take_step()
        Inputs:
            - env (Type: OpenAI gym Environment)
            - action (Type: int corresponding to action in env.action_space)
        Returns:
            - envState (Type: dict containing all information to be recorded for future use)
              change contents of dict as desired, but return must be type dict.
        """
        self.count += 1
        done = self.count > len(self.imgnames)
        envState = {"done": done}
        return envState

    def render(self):
        """
        Gets render from gym.
        Caller:
            - Trial.get_render()
        Inputs:
            - env (Type: OpenAI gym Environment)
        Returns:
            - return from env.render('rgb_array') (Type: npArray)
              must return the unchanged rgb_array
        """

        return f"images/{self.imgnames[self.count]}"

    def reset(self):
        """
        Resets the environment to start new episode.
        Caller:
            - Trial.reset()
        Inputs:
            - env (Type: OpenAI gym Environment)
        Returns:
            No Return
        """
        self.count = 0

    def close(self):
        """
        Closes the environment at the end of the trial.
        Caller:
            - Trial.close()
        Inputs:
            - env (Type: OpenAI gym Environment)
        Returns:
            No Return
        """
