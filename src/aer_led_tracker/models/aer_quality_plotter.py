from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric
import numpy as np
from aer_led_tracker.models import aer_color_sequence


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
        
        cmax_q = 0
        labels = sorted(tracks.keys(), key=int)
        for i, label in enumerate(labels):
            choices = tracks[label]
            x.append(i)
            c.append(aer_color_sequence[i])
            qualities = choices['quality']
            q.append(qualities)
            cmax_q = max(cmax_q, np.max(qualities))
        
        for i in range(len(x)):
            for j, qq in enumerate(q[i]):
                xj = x[i] + 0.1 * j
                pylab.plot([xj, xj], [0, qq], '%s-' % c[i])
                
        self.max_q = max(self.max_q, cmax_q)
    
        pylab.axis((-1, len(x), 0, self.max_q))
        pylab.xticks(x, labels)
        pylab.title('quality')
        
#        
#        T = self.get_input_timestamp(0)
#        title = 'T = %.1f ms' % (T * 1000)
#        pylab.title(title)

