from aer_led_tracker.models.aer_track_plotter import plot_tracks
from aer_led_tracker.resolver import enumerate_id_track
from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric


class AERAltPlotter(Block):
    Block.alias('aer_alt_plotter')
    Block.config('width', 'Image dimension', default=128)
    Block.input('alts')
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
        alts = self.input.alts

        markers = ['s', 'o', 'x']
        for i, alt in enumerate(alts):
            subset = alt.subset
            print subset
            # get the last ones
            tracks = get_last(subset)
            print tracks
            
            marker = markers[i % len(markers)]
            plot_tracks(pylab, tracks, base_markersize=10, marker=marker)
        

def get_last(subset):
    tracks = {}
    for id_track, its_data in enumerate_id_track(subset):
        tracks[id_track] = its_data[-1:]
    return tracks
