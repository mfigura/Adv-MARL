import numpy as np
import random
import gym
from gym import spaces

random.seed(10)
np.random.seed(10)


class Grid_World(gym.Env):
    """
    Multi agent Grid-World
    Objective of each agent is to reach their desired positions with out colliding and following a shortest path
    nrow, ncol: dimensions of the grid world 
    n_agents: number of agents/players
    rew_scaling: if True scales the reward with some values [p1,p2,p3] (s.t. p1+p2+p3 =1 ), 
                 for example for 3 agents, the rewards [r1,r2,r3] will be transformed to
                  [p1*r1, p2*r2, p3*r3]
    """ 
    metadata = {'render.modes': ['console']}

    def __init__(self, nrow = 5, ncol=5, n_agents = 1, rew_scaling = True):
        super(Grid_world, self).__init__()
        self.nrow = nrow
        self.ncol = ncol
        self.n_agents = n_agents
        self.total_states = self.nrow * self.ncol
        self.n_actions = self.n_agents
        self.rew_scaling = rew_scaling

        #self.observation_space = spaces.Discrete(self.total_states*n_agents)
        self.observation_space = gym.spaces.MultiDiscrete([env.total_states for _ in range(env.n_agents)])
        self.action_space = gym.spaces.MultiDiscrete([self.n_actions for _ in range(env.n_agents)])

        self._state_map()
        self._get_state()
        self._get_desired()
        self._reward_scaling()

    def _get_state(self):
        self.state = np.array(random.sample(range(self.total_states), self.n_agents))

    def _get_desired(self):
        self.desired_state = np.array(random.sample(range(self.total_states), self.n_agents))

    def _set_state(self, state):
        self.state = state

    def _set_desired(self, desired_state):
        self.desired_state = desired_state
    
    def _reward_scaling(self):
        temp = np.random.uniform(low=0, high=1, size=(self.n_agents,))
        self.reward_scaling = temp/temp.sum()

    def _to_s(self, row, col):
        return row*self.ncol + col
    
    def _state_map(self):
        """
        self.state_transformation: is a dict with 
                                    key - (x,y) co-ordinate
                                    vaue - state (0 - self.total_states)
        self.i_state_transformation: is a dict with 
                                    key - state (0 - self.total_states)
                                    vaue - (x,y) co-ordinate                                   
        """
        self.state_transformation={}
        for row in range(self.nrow):
            for col in range(self.ncol):
                self.state_transformation[(row, col)] = self._to_s(row, col)
        self.i_state_transformation={}
        for key, value in self.state_transformation.items():
            self.i_state_transformation[value]=key

    def _dist(self, s1, s2):
        """
        measures the shortest distance between the state s1 and s2
        s1, s2 are integers
        """
        x1, y1 = self.i_state_transformation[s1]
        x2, y2 = self.i_state_transformation[s2]
        return abs(x1-x2)+abs(y1-y2)

    def _inc(self, row, col, a):
        """
        row, col, a are all integers
        at (row,col) coordinate, taking the action = (0,1,2,3)
        we arrive at (row, col) coordinate
        """
        if a == 0:
            col = max(col - 1, 0)
        elif a == 1:
            row = min(row + 1, self.nrow - 1)
        elif a == 2:
            col = min(col + 1, self.ncol - 1)
        elif a == 3:
            row = max(row - 1, 0)
        return (row, col)
    
    def reset(self):
        """
        resets the environment
        1 - resets the state and its desired values to some random values
        2- returns the current state numpy array of dim (self.n_agents, )
        """
        self._get_state()
        self._get_desired()
        return self.state

    def step(self, a):
        """
        a: represent the actions of all agents, a numpy array of shape (self.n_agents, )
        returns the new state, reward, terminal states after taking action a

        returns
        self.state: numpy array (self.n_agents, )
        self.reward: numpy array (self.n_agents, )
        done: True (if all agents reached their desired positions) or False (otherwise)
        """
        temp_s = []
        rew =[]
        d = []
        for s,a, s_d in zip(self.state, a, self.desired_state):
            x, y = self.i_state_transformation[s]
            new_x, new_y = self._inc(x, y, a)
            new_s = self.state_transformation[(new_x, new_y)]
            temp_s.append(new_s)
            rew.append(-self._dist(s,s_d))

        for i, s in enumerate(self.state):
            sub_s = np.delete(self.state, [i])
            if s in sub_s:
                rew[i] = rew[i] - (self.ncol+self.nrow)/2
        
        self.state = np.array(temp_s)
        if self.rew_scaling:
            self.reward = np.array(rew)*self.reward_scaling
        else:
            self.reward = np.array(rew)
        self.done = np.array_equal(self.state, self.desired_state)

        return self.state, self.reward, self.done, {}
    
    def get_node(self, node_index, complete_state = True):
        """
        This can be used to control information leak in MARL
        using get_node we get the reward of the specified node (only)
        If complete_state is False, then we can not observe the states of other agents
        always use get_node after using the step method
        """
        if complete_state:
            return self.state, self.reward[node_index], self.done, {}
        else:
            return self.state[node_index], self.reward[node_index], self.done, {}

    def close(self):
        pass

env = Grid_world(6,6,36)
print(env.observation_space.shape[0])
print(env.action_space.shape[0])
state = env.reset()
np.shape(state)