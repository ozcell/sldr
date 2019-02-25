import random
from collections import namedtuple
import numpy as np
import torch as K

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0
        self.pre_norm_clip = 200
        self.post_norm_clip = 5

    def push(self, *args):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    
    def pull(self):
        #memory = self.memory[::-1]
        memory = self.memory
        self.memory = []
        self.position = 0
        return memory

    def __len__(self):
        return len(self.memory)

    
class Normalizer(object):
    def __init__(self, pre_norm_clip=200, post_norm_clip=5):
        self.N = 0.0
        self.pre_norm_clip = pre_norm_clip
        self.post_norm_clip = post_norm_clip

    def update_stats(self, x):
        self.N += 1
        if self.N == 1:
            self.oldMean = x
            self.Mean = x
            self.Var = np.zeros_like(x)
        else:
            self.Mean = self.oldMean + (x - self.oldMean)/self.N
            self.Var = self.Var + (x - self.oldMean)*(x - self.Mean)
            self.oldMean = self.Mean

    def preprocess(self, x):
        #pre-normalisation clipping
        x = x.clamp(-self.pre_norm_clip, self.pre_norm_clip)
        #normalising
        mu, std = self.get_stats()
        x -= K.tensor(mu, dtype=x.dtype, device=x.device)
        x /= (K.tensor(std, dtype=x.dtype, device=x.device)  + 1e-2)
        #post-normalisation clipping
        x = x.clamp(-self.post_norm_clip, self.post_norm_clip)

        return x

    def preprocess_with_update(self, x):
        #pre-normalisation clipping
        x = x.clamp(-self.pre_norm_clip, self.pre_norm_clip)
        self.update_stats(x)
        #normalising
        mu, std = self.get_stats()
        x -= K.tensor(mu, dtype=x.dtype, device=x.device)
        x /= (K.tensor(std, dtype=x.dtype, device=x.device)  + 1e-2)
        #post-normalisation clipping
        x = x.clamp(-self.post_norm_clip, self.post_norm_clip)

        return x

    def get_stats(self):
        if self.N < 2:
            return 0.0, 1.0
        else:
            return self.Mean, np.sqrt(self.Var/(self.N-1))
        

    


