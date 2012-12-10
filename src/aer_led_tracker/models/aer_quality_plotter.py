from aer_led_tracker.models.utils import get_track_colors
from aer_led_tracker.tracks import enumerate_id_track
from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric
import numpy as np


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
        assert isinstance(tracks, np.ndarray)
        
        t2c = get_track_colors(tracks)
        x_ticks = []
        x_label = []
        for i, xx in enumerate(enumerate_id_track(tracks)):
            id_track, its_data = xx
            x_ticks.append(i)
            x_label.append(id_track)
            quality = its_data['quality']
            for j, qq in enumerate(quality):
                xj = i + 0.16 * (j + 1 - len(quality) / 2.0)
                pylab.plot([xj, xj], [0, qq], '%s-' % t2c[id_track], linewidth=2)
                
        self.max_q = max(self.max_q, np.max(tracks['quality']))
    
        M = 0.1
        pylab.axis((-1, len(x_ticks), -M * self.max_q, self.max_q * (1 + M)))
        pylab.xticks(x_ticks, x_label)
        pylab.title('Detection quality') 
        
        
