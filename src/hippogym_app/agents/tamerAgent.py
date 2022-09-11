"""
This demo of a TAMER algorithm implmented with HIPPO Gym has been adapted
from code provided by Calarina Muslimani of the Intelligent Robot Learning Laboratory
To use this code with the default setup simply rename this file to agent.py
"""

import itertools
import time

import gym
import numpy as np

# This is the code for tile coding features
basehash = hash


class IHT:
    "Structure to handle collisions"

    def __init__(self, sizeval):
        self.size = sizeval
        self.overfullCount = 0
        self.dictionary = {}

    def __str__(self):
        "Prepares a string for printing whenever this object is printed"
        return (
            "Collision table:"
            + " size:"
            + str(self.size)
            + " overfullCount:"
            + str(self.overfullCount)
            + " dictionary:"
            + str(len(self.dictionary))
            + " items"
        )

    def count(self):
        return len(self.dictionary)

    def fullp(self):
        return len(self.dictionary) >= self.size

    def getindex(self, obj, readonly=False):
        d = self.dictionary
        if obj in d:
            return d[obj]
        elif readonly:
            return None
        size = self.size
        count = self.count()
        if count >= size:
            if self.overfullCount == 0:
                print("IHT full, starting to allow collisions")
            self.overfullCount += 1
            return basehash(obj) % self.size
        else:
            d[obj] = count
            return count


def hashcoords(coordinates, m, readonly=False):
    if type(m) == IHT:
        return m.getindex(tuple(coordinates), readonly)
    if type(m) == int:
        return basehash(tuple(coordinates)) % m
    if m == None:
        return coordinates


from itertools import zip_longest
from math import floor, log


def tiles(ihtORsize, numtilings, floats, ints=[], readonly=False):
    """returns num-tilings tile indices corresponding to the floats and ints"""
    qfloats = [floor(f * numtilings) for f in floats]
    Tiles = []
    for tiling in range(numtilings):
        tilingX2 = tiling * 2
        coords = [tiling]
        b = tiling
        for q in qfloats:
            coords.append((q + b) // numtilings)
            b += tilingX2
        coords.extend(ints)
        Tiles.append(hashcoords(coords, ihtORsize, readonly))
    return Tiles


def tileswrap(ihtORsize, numtilings, floats, wrapwidths, ints=[], readonly=False):
    """returns num-tilings tile indices corresponding to the floats and ints, wrapping some floats"""
    qfloats = [floor(f * numtilings) for f in floats]
    Tiles = []
    for tiling in range(numtilings):
        tilingX2 = tiling * 2
        coords = [tiling]
        b = tiling
        for q, width in zip_longest(qfloats, wrapwidths):
            c = (q + b % numtilings) // numtilings
            coords.append(c % width if width else c)
            b += tilingX2
        coords.extend(ints)
        Tiles.append(hashcoords(coords, ihtORsize, readonly))
    return Tiles


class MountainCarTileCoder:
    def __init__(self, iht_size=4096, num_tilings=8, num_tiles=8):
        """
        Initializes the MountainCar Tile Coder

        iht_size -- int, the size of the index hash table, typically a power of 2
        num_tilings -- int, the number of tilings
        num_tiles -- int, the number of tiles. Here both the width and height of the
        tile coder are the same
        """
        self.iht = IHT(iht_size)
        self.num_tilings = num_tilings
        self.num_tiles = num_tiles

    def get_tiles(self, position, velocity):
        """
        Takes in a position and velocity from the mountaincar environment
        and returns a numpy array of active tiles.

        returns:
        tiles - np.array, active tiles
        """
        # Use the ranges above and self.num_tiles to scale position and velocity to the range [0, 1]
        # then multiply that range with self.num_tiles so it scales from [0, num_tiles]
        minP = -1.2
        maxP = 0.5
        minV = -0.07
        maxV = 0.07
        scaleP = maxP - minP
        scaleV = maxV - minV

        position_scaled = ((position - minP) / (scaleP)) * self.num_tiles

        velocity_scaled = ((velocity - minV) / (scaleV)) * self.num_tiles

        # get the tiles using tc.tiles, with self.iht, self.num_tilings and [scaled position, scaled velocity]
        # nothing to implment here
        mytiles = tiles(self.iht, self.num_tilings, [position_scaled, velocity_scaled])

        return np.array(mytiles)


# this is the tamer agent class


class TamerAgent:
    """
    Initialization of Tamer Agent. All values are set to None so they can
    be initialized in the agent_init method.
    """

    def __init__(self):

        self.last_action = None
        self.previous_tiles = None
        self.first_state = None
        self.current_action = None
        self.current_tiles = None

        self.num_tilings = 8
        self.num_tiles = 8
        self.iht_size = 4096
        self.epsilon = 0.01
        self.x = 0.08
        self.alpha = self.x / self.num_tilings  # this is step size
        self.num_actions = 3
        self.actions = list(range(self.num_actions))
        self.time_step = 0
        self.experiences = list()
        self.max_n_experiences = 1000
        self.window_size = 1

        # We initialize self.w to three times the iht_size. Recall this is because
        # we need to have one set of weights for each action.
        self.w = np.ones((self.num_actions, self.iht_size))

        # We initialize self.mctc to the mountaincar verions of the
        # tile coder that we created

        self.mctc = MountainCarTileCoder(
            iht_size=self.iht_size,
            num_tilings=self.num_tilings,
            num_tiles=self.num_tiles,
        )

    def argmax(self, q_values):
        """argmax with random tie-breaking
        Args:
        q_values (Numpy array): the array of action values
        Returns:
        action (int): an action with the highest value
        """
        top = float("-inf")
        ties = []

        for i in range(len(q_values)):
            if q_values[i] > top:
                top = q_values[i]
                ties = []

            if q_values[i] == top:
                ties.append(i)

        return np.random.choice(ties)

    def select_greedy_action(self, tiles):
        """
        Selects an action using greedy
        Args:
        tiles - np.array, an array of active tiles
        Returns:
        (chosen_action, action_value) - (int, float), tuple of the chosen action
        and it's value
        """
        action_values = []
        chosen_action = None

        for a in range(self.num_actions):
            action_values.append(np.sum(self.w[a][tiles]))
        # First loop through the weights of each action and populate action_values
        # with the action value for each action and tiles instance

        if np.random.random() < self.epsilon:
            chosen_action = np.random.choice(self.actions)
        else:
            chosen_action = self.argmax(action_values)

        return chosen_action

    def action_selection(self, state):
        position, velocity = state
        active_tiles = self.mctc.get_tiles(position, velocity)
        current_action = self.select_greedy_action(active_tiles)
        self.current_action = current_action
        self.current_tiles = np.copy(active_tiles)

    def agent_start(self, state):
        """The first method called when the experiment starts, called after
        the environment starts.
        Args:
        state (Numpy array): the state observation from the
        environment's evn_start function.
        Returns:
        The first action the agent takes.
        """
        position, velocity = state

        active_tiles = self.mctc.get_tiles(position, velocity)

        self.current_action = np.random.choice(self.actions)
        self.current_tiles = np.copy(active_tiles)

        self.experiences.append((self.current_action, self.current_tiles, time.time()))
        return self.current_action

    def update_reward_function(self, reward):

        if reward == "good":
            r = 1
        elif reward == "reallygood":
            r = 4
        elif reward == "bad":
            r = -1

        elif reward == "None":
            return

        current_time = time.time()
        while len(self.experiences) > 0:
            experience = self.experiences[0]

            # diff= current_time-experience[2]

            # if (diff < .2 or diff > 2):

            if experience[2] < current_time - self.window_size:  #
                self.experiences.pop(0)

            else:
                break

        # update weights using Algorithm 1 in paper
        n_experiences = len(self.experiences)

        if n_experiences == 0:
            return
        weight_per_experience = 1.0 / n_experiences
        cred_features = np.zeros((self.num_actions, self.iht_size))

        for experience in self.experiences:
            exp_features = np.zeros((self.num_actions, self.iht_size))
            exp_features[experience[0]][experience[1]] = 1

            exp_features *= weight_per_experience
            cred_features = np.add(cred_features, exp_features)

        error = r - self.w * cred_features
        self.w += 0.01 * error * cred_features


# Original HIPPO Gym Agent

"""
This is a demo file to be replaced by the researcher as required.
This file is imported by trial.py and trial.py will call:
start()
step()
render()
reset()
close()
These functions are mandatory. This file contains minimum working versions
of these functions, adapt as required for individual research goals.
"""


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
        self.tamer = True
        if self.tamer:
            np.random.seed(0)
            self.tamerAgent = TamerAgent()
        self.env = gym.make(game)
        return

    def step(self, action, reward):
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
        if self.tamer:
            if self.tamerAgent.time_step == 0:
                self.tamerAgent.agent_start(self.tamerAgent.first_state)
                time.sleep(1.5)

            self.tamerAgent.time_step += 1
            self.tamerAgent.update_reward_function(reward)
            self.tamerAgent.last_action = self.tamerAgent.current_action
            self.tamerAgent.previous_tiles = self.tamerAgent.current_tiles

            if reward != "None":
                updated = True
            else:
                updated = False

            observation, reward, done, info = self.env.step(
                self.tamerAgent.current_action
            )
            action = self.tamerAgent.current_action
        else:
            observation, reward, done, info = self.env.step(action)

        envState = {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info,
            "agentAction": action,
        }

        if self.tamer:
            self.tamerAgent.action_selection(observation)
            self.tamerAgent.experiences.append(
                (
                    self.tamerAgent.current_action,
                    self.tamerAgent.current_tiles,
                    time.time(),
                )
            )
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
        return self.env.render("rgb_array")

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
        if self.tamer:
            self.tamerAgent.time_step = 0
            self.tamerAgent.first_state = self.env.reset()
        else:
            self.env.reset()

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
        self.env.close()
