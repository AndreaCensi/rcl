from aer_led_tracker import aer_track_parse_line
from procgraph import Block
from procgraph.block_utils import TextLog
import numpy as np

class AERTrackerLogReader(TextLog):
    Block.alias('aer_tracker_log')
    Block.config('file')
    Block.output('track')
        
    def init(self):
        self.last = -1
        self.buffer = []
        TextLog.init(self)
        
    def parse_format(self, line):
        # return none if we want more data
        x = aer_track_parse_line(line)
        if x is None:
            return None
        
        self.buffer.append(x)
        # If it was the last in the sequence:
        if x['peak'] == x['npeaks'] - 1:
            res = np.array(self.buffer, self.buffer[0].dtype)
            self.buffer = []
            
            t = res[0]['timestamp']
            if t <= self.last:
                t = self.last + 0.0000001
            self.last = t
            
            return t, [(0, res)]

# @simple_block
# def tracks_quality(tracks):
#    q = [tracks[x]['quality'] for x in sorted(tracks.keys())]
#    return np.array(q)





