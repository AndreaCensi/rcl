from aer_led_tracker.models.utils import set_viewport_style, get_track_colors
from aer_led_tracker.tracks import enumerate_id_track
from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric
import numpy as np


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
        
        plot_tracks(pylab, tracks, base_markersize=10, alpha=0.5)

        T = self.get_input_timestamp(0)
        pylab.title('Raw detections')
        time = 'T = %.1f ms' % (T * 1000)
        pylab.text(3, 3, time)
        set_viewport_style(pylab)


def plot_tracks(pylab, tracks, base_markersize=5, marker='s', alpha=1):
    assert isinstance(tracks, np.ndarray)
    
    t2c = get_track_colors(tracks)
    for id_track, its_data in enumerate_id_track(tracks):
        for t in its_data: 
            x = t['i']
            y = t['j']            
            # r = 1 is best, r =0 is worst
            r = (t['npeaks'] - t['peak']) * 1.0 / t['npeaks']
            markersize = base_markersize * (r / 2 + 0.5) 
            pylab.plot(x, y, color=t2c[id_track], marker=marker,
                       markersize=markersize, alpha=alpha)
