from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric
from aer_led_tracker.models import aer_color_sequence
from aer_led_tracker.models.utils import set_viewport_style


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
    
        plot_tracks(pylab, tracks, base_markersize=5)

        T = self.get_input_timestamp(0)
        title = 'T = %.1f ms' % (T * 1000)
        pylab.title(title)
        set_viewport_style(pylab)


def plot_tracks(pylab, tracks, base_markersize=5, marker='s'):
    label2c = {}
    labels = sorted(tracks.keys(), key=int)
    for i, label in enumerate(labels):
        label2c[label] = aer_color_sequence[i]
        
    for i in range(len(labels)):
        id_track = labels[i]
        for t in tracks[id_track]: 
            x = t['i']
            y = t['j']
            # pylab.text(x, y + 15, id_track)
            
            # r = 1 is best, r =0 is worst
            r = (t['npeaks'] - t['peak']) * 1.0 / t['npeaks']
            markersize = base_markersize * (r / 2 + 0.5) 
            pylab.plot(x, y, color=label2c[id_track], marker=marker,
                       markersize=markersize)
            pylab.axis((0, 128, 0, 128))
