from contracts import contract
from operator import attrgetter
import itertools
import numpy as np


class Resolver(object):
    
    """ Resolves ambiguities based on track history """
    def __init__(self, min_track_dist, motion_model, history):
        """
            :param history: Length of history to consider.
            :param min_track_dist: Minimum distance between different track (pixels)
            :param max_vel: Maximum velocity (pixels/s)
        """
        self.min_track_dist = min_track_dist
        self.motion_model = motion_model
        self.history = history
        
        self.buffer = []
        
    @contract(track_observations='array[>=1]')
    def push_obs(self, track_observations):
        self.buffer.append(track_observations)
        
        def too_big():
            t1 = self.buffer[-1][0]['timestamp']
            t0 = self.buffer[0][0]['timestamp']
            delta = t1 - t0
            print('Current delta: %s  n: %s' % (delta, len(self.buffer)))
            return delta > self.history
                
        while too_big():
            self.buffer.pop(0)

    def push(self, track_observations):
        """
            :param track_observations: array of track_observations_dtype
        """
        self.push_obs(track_observations)
        
#        res = compute_alternatives(self.buffer)
#        print res
        
        
    def compute_alternatives(self):
        print('------------')
        alt1 = compute_alternatives_sep(self.buffer, self.motion_model)
        print('------------')
        alt1 = compute_alternatives(self.buffer, self.motion_model)
        return alt1
    
    def compute_alternatives_combinatorial(self):
        """ Uses a combinatorial algorithm """
        return compute_alternatives_combinatorial(self.buffer, self.motion_model)




