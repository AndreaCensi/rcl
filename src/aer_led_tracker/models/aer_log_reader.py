from procgraph.block_utils.textlog import TextLog
from procgraph import Block
from aer_led_tracker.logio import aer_track_parse_line
from procgraph_mpl.plot_generic import PlotGeneric
from procgraph.core.registrar_other import simple_block
 
 
class AERLogReader(TextLog):
    Block.alias('aer_tracker_log')
    Block.config('file')
    Block.output('track')
        
    def init(self):
        self.last = -1
        TextLog.init(self)
        
    def parse_format(self, line):
        x = aer_track_parse_line(line)
        if x is None:
            return None
        else:
            t = x['timestamp']
            if t <= self.last:
                t = self.last + 0.0000001
            self.last = t
            return t, [(0, x)]

class Smoother(object):
    """ Smooths different tracks"""
    def __init__(self, num):
        """ num: number of tracks """
        self.num = num
        self.last = {}
        
    def push(self, x):
        id_track = x['id_track'].item()
        self.last[id_track] = x
        
    def is_complete(self):
        return len(self.last) >= self.num

    def get_values(self):
        return dict(**self.last)
    
    
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
        
#
# class AERSmootherQuality(Block):
#    Block.alias('aer_smoother')
#    Block.config('ntracks')
#    Block.input('track_log')
#    Block.output('quality')
#    
#    def init(self):
#        self.smoother = Smoother(self.config.ntracks)
#        
#    def update(self):
#        self.smoother.push(self.input.track_log)
#        if self.smoother.is_complete():
#            self.set_output('tracks', self.smoother.get_values())
#        
        
# @simple_block
# def track_quality(tracks, id_track=COMPULSORY):
#    return tracks[id_track]['quality'].item()

import numpy as np

@simple_block
def tracks_quality(tracks):
    q = [tracks[x]['quality'] for x in sorted(tracks.keys())]
    return np.array(q)


class AERTrackPlotter(Block):
    Block.alias('aer_track_plotter')
    Block.config('width', 'Image dimension', default=128)
    Block.input('tracks')
    Block.output('rgb')
    
    def init(self):
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.width,
                                        transparent=False,
                                        tight=False)
        
    def update(self):
        self.output.rgb = self.plot_generic.get_rgb(self.plot)
        
    def plot(self, pylab):
        tracks = self.input.tracks
        
        label2c = {}
        labels = sorted(tracks.keys(), key=int)
        for i, label in enumerate(labels):
            label2c[label] = colors[i]
            
        for i in range(len(labels)):
            id_track = labels[i]
            t = tracks[id_track]
            x = t['x']
            y = t['y']
            # pylab.text(x, y + 15, id_track)
            pylab.plot(x, y, '%ss' % label2c[id_track])
            pylab.axis((0, 128, 0, 128))

        T = self.get_input_timestamp(0)
        title = 'T = %.1f ms' % (T * 1000)
        pylab.title(title)

colors = ['r', 'g', 'b', 'k']

class AERqualityPlotter(Block):
    Block.alias('aer_quality_plotter')
    Block.config('width', 'Image dimension', default=128)
    Block.input('tracks')
    Block.output('rgb')
    
    def init(self):
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.width,
                                        transparent=False,
                                        tight=False)
        self.max_q = 0
        
    def update(self):
        self.output.rgb = self.plot_generic.get_rgb(self.plot)
        
    def plot(self, pylab):
        tracks = self.input.tracks
        
        x = []
        q = []
        c = []
        labels = sorted(tracks.keys(), key=int)
        for i, label in enumerate(labels):
            x.append(i)
            c.append(colors[i])
            q.append(tracks[label]['quality'])
        
        for i in range(len(x)):
            pylab.plot([x[i], x[i]], [0, q[i]], '%s-' % c[i])
        # pylab.plot(x, q, 's')
        
        self.max_q = max(self.max_q, np.max(q))
    
        pylab.axis((-1, len(x), 0, self.max_q))
        pylab.xticks(x, labels)
        pylab.title('quality')
        
#        
#        T = self.get_input_timestamp(0)
#        title = 'T = %.1f ms' % (T * 1000)
#        pylab.title(title)



