from procgraph import Block
from aer_led_tracker.tracks import aer_track_dtype
import numpy as np

class Smoother(object):
    """ Smooths different tracks"""
    def __init__(self, num):
        """ num: number of tracks """
        self.num = num
        self.last = {}
        
    def push(self, x):
        id_track = x[0]['id_track'].item()
        self.last[id_track] = x
        
    def is_complete(self):
        return len(self.last) >= self.num

    def get_values(self):
        values = []
        for x in self.last.values():
            values.extend(x)
        x = np.asarray(values, dtype=aer_track_dtype)
        return x

    
class AERSmoother(Block):
    Block.alias('aer_smoother')
    Block.config('ntracks')
    Block.input('track_log')
    Block.output('tracks')
    
    def init(self):
        self.smoother = Smoother(self.config.ntracks)
        
    def update(self):
        self.smoother.push(self.input.track_log)
        if self.smoother.is_complete():
            self.set_output('tracks', self.smoother.get_values())
        
